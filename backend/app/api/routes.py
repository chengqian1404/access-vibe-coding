import asyncio
import os
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response

from app.config.settings import settings
from app.models.analysis import Analysis, KeyPoint, QAPair
from app.models.recording import Danmaku, Recording, Transcript
from app.services.audio_processor import AudioProcessor
from app.services.audio_recorder import AudioRecorder
from app.services.config_manager import config_manager
from app.services.content_analyzer import ContentAnalyzer
from app.services.monitor_service import MonitorService
from app.services.qa_extractor import QaExtractor
from app.services.report_generator import ReportGenerator
from app.services.screen_recorder import ScreenRecorder
from app.services.weixin_launcher import WeixinLauncher
from app.utils.helpers import get_timestamp_str, safe_filename
from app.utils.logger import logger
from app.utils.validators import validate_weixin_id

router = APIRouter(prefix="/api")

# ── Singleton service instances ──────────────────────────────────────
_screen_recorder = ScreenRecorder()
_audio_recorder = AudioRecorder()
_monitor_service = MonitorService()
_weixin_launcher = WeixinLauncher()
_content_analyzer = ContentAnalyzer()
_qa_extractor = QaExtractor()
_report_generator = ReportGenerator()
_audio_processor = AudioProcessor()

# ── Current recording state ──────────────────────────────────────────
_current_recording: Optional[Recording] = None
_db_session = None


def _get_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    return Session()


# ─────────────────────────────────────────────────────────────────────
# Health
# ─────────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}


# ─────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────

@router.get("/config")
def get_config():
    return config_manager.get_all()


@router.post("/config")
def update_config(data: Dict[str, Any]):
    config_manager.update_from_dict(data)
    return {"status": "ok"}


# ─────────────────────────────────────────────────────────────────────
# Recordings
# ─────────────────────────────────────────────────────────────────────

@router.get("/recordings")
def list_recordings():
    db = _get_db()
    try:
        recordings = db.query(Recording).order_by(Recording.created_at.desc()).all()
        return [r.to_dict() for r in recordings]
    finally:
        db.close()


@router.get("/recordings/{recording_id}")
def get_recording(recording_id: int):
    db = _get_db()
    try:
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        result = recording.to_dict()
        result["transcripts"] = [t.to_dict() for t in recording.transcripts]
        result["danmakus"] = [d.to_dict() for d in recording.danmakus]
        return result
    finally:
        db.close()


@router.delete("/recordings/{recording_id}")
def delete_recording(recording_id: int):
    db = _get_db()
    try:
        recording = db.query(Recording).filter(Recording.id == recording_id).first()
        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")
        for file_attr in ("screen_file", "audio_file", "video_file"):
            fpath = getattr(recording, file_attr, None)
            if fpath and os.path.exists(fpath):
                try:
                    os.remove(fpath)
                except Exception:
                    pass
        db.delete(recording)
        db.commit()
        return {"status": "ok"}
    finally:
        db.close()


# ─────────────────────────────────────────────────────────────────────
# Recording control
# ─────────────────────────────────────────────────────────────────────

@router.post("/recording/start")
async def start_recording(data: Optional[Dict[str, Any]] = None):
    global _current_recording

    if _screen_recorder.get_status()["status"] == "recording":
        raise HTTPException(status_code=400, detail="Already recording")

    data = data or {}
    stream_id = data.get("stream_id") or config_manager.get_weixin_id() or "unknown"
    title_base = data.get("title") or f"直播_{stream_id}_{get_timestamp_str()}"
    title = safe_filename(title_base)

    Path(settings.RECORDINGS_PATH).mkdir(parents=True, exist_ok=True)
    ts = get_timestamp_str()
    screen_path = str(Path(settings.RECORDINGS_PATH) / f"{title}_{ts}_screen.mp4")
    audio_path = str(Path(settings.RECORDINGS_PATH) / f"{title}_{ts}_audio.wav")

    db = _get_db()
    try:
        rec = Recording(
            title=title,
            stream_id=stream_id,
            start_time=datetime.utcnow(),
            status="recording",
            screen_file=screen_path,
            audio_file=audio_path,
        )
        db.add(rec)
        db.commit()
        db.refresh(rec)
        _current_recording = rec.to_dict()
        recording_id = rec.id
    finally:
        db.close()

    try:
        _screen_recorder.start(screen_path)
    except Exception as exc:
        logger.error("Screen recorder start error: %s", exc)

    try:
        _audio_recorder.start(audio_path)
    except Exception as exc:
        logger.error("Audio recorder start error: %s", exc)

    from app.api.websocket import manager
    await manager.broadcast({
        "type": "recording_status",
        "data": {"status": "recording", "recording_id": recording_id, "title": title},
    })

    return {"status": "recording", "recording_id": recording_id, "title": title}


@router.post("/recording/stop")
async def stop_recording():
    global _current_recording

    if _screen_recorder.get_status()["status"] != "recording" and _audio_recorder.get_status()["status"] != "recording":
        raise HTTPException(status_code=400, detail="Not currently recording")

    screen_file = None
    audio_file = None

    try:
        screen_file = _screen_recorder.stop()
    except Exception as exc:
        logger.error("Screen recorder stop error: %s", exc)

    try:
        audio_file = _audio_recorder.stop()
    except Exception as exc:
        logger.error("Audio recorder stop error: %s", exc)

    if _current_recording:
        db = _get_db()
        try:
            rec = db.query(Recording).filter(Recording.id == _current_recording["id"]).first()
            if rec:
                rec.end_time = datetime.utcnow()
                if rec.start_time:
                    rec.duration = (rec.end_time - rec.start_time).total_seconds()
                rec.status = "stopped"
                if screen_file:
                    rec.screen_file = screen_file
                if audio_file:
                    rec.audio_file = audio_file
                db.commit()
                db.refresh(rec)
                _current_recording = rec.to_dict()
                recording_id = rec.id
            else:
                recording_id = _current_recording.get("id")
        finally:
            db.close()
    else:
        recording_id = None

    from app.api.websocket import manager
    await manager.broadcast({
        "type": "recording_status",
        "data": {"status": "stopped", "recording_id": recording_id},
    })

    return {"status": "stopped", "recording_id": recording_id}


@router.get("/recording/status")
def recording_status():
    screen_st = _screen_recorder.get_status()
    audio_st = _audio_recorder.get_status()
    return {
        "screen": screen_st,
        "audio": audio_st,
        "current_recording": _current_recording,
    }


@router.post("/recording/screenshot")
def take_screenshot():
    try:
        data = _screen_recorder.take_screenshot()
        return Response(content=data, media_type="image/png")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────────────────
# Monitor
# ─────────────────────────────────────────────────────────────────────

@router.get("/monitor/status")
def monitor_status():
    return _monitor_service.get_status()


@router.post("/monitor/start")
async def start_monitor(data: Optional[Dict[str, Any]] = None):
    data = data or {}
    weixin_id = data.get("weixin_id") or config_manager.get_weixin_id()
    if not weixin_id:
        raise HTTPException(status_code=400, detail="weixin_id is required")

    interval = int(data.get("interval", 30))

    from app.api.websocket import manager as ws_manager

    def on_live(wid: str):
        asyncio.run_coroutine_threadsafe(
            ws_manager.broadcast({"type": "live_detected", "data": {"weixin_id": wid}}),
            asyncio.get_event_loop(),
        )

    _monitor_service.set_live_callback(on_live)
    _monitor_service.start_monitoring(weixin_id, interval=interval)
    return {"status": "monitoring", "weixin_id": weixin_id, "interval": interval}


@router.post("/monitor/stop")
def stop_monitor():
    _monitor_service.stop_monitoring()
    return {"status": "stopped"}


# ─────────────────────────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────────────────────────

@router.post("/analysis/start/{recording_id}")
async def start_analysis(recording_id: int, background_tasks: BackgroundTasks):
    db = _get_db()
    try:
        rec = db.query(Recording).filter(Recording.id == recording_id).first()
        if not rec:
            raise HTTPException(status_code=404, detail="Recording not found")
        recording_dict = rec.to_dict()
        audio_file = rec.audio_file
        transcripts = [t.to_dict() for t in rec.transcripts]
        danmakus = [d.to_dict() for d in rec.danmakus]
    finally:
        db.close()

    background_tasks.add_task(
        _run_analysis,
        recording_id=recording_id,
        recording_dict=recording_dict,
        audio_file=audio_file,
        existing_transcripts=transcripts,
        existing_danmakus=danmakus,
    )
    return {"status": "started", "recording_id": recording_id}


async def _run_analysis(
    recording_id: int,
    recording_dict: Dict,
    audio_file: Optional[str],
    existing_transcripts: list,
    existing_danmakus: list,
) -> None:
    from app.api.websocket import manager as ws_manager

    async def emit(step: str, progress: int, message: str = ""):
        await ws_manager.broadcast({
            "type": "analysis_progress",
            "data": {"recording_id": recording_id, "step": step, "progress": progress, "message": message},
        })

    await emit("init", 0, "开始分析…")

    # Step 1: Transcription
    transcripts = existing_transcripts
    if audio_file and os.path.exists(audio_file) and not existing_transcripts:
        await emit("transcription", 10, "音频转录中…")
        try:
            transcripts = _audio_processor.transcribe(audio_file)
            db = _get_db()
            try:
                for seg in transcripts:
                    t = Transcript(
                        recording_id=recording_id,
                        start_time=seg.get("start", 0),
                        end_time=seg.get("end", 0),
                        text=seg.get("text", ""),
                        confidence=seg.get("confidence"),
                    )
                    db.add(t)
                db.commit()
            finally:
                db.close()
        except Exception as exc:
            logger.error("Transcription error: %s", exc)
            await emit("transcription", 15, f"转录失败: {exc}")

    await emit("analysis", 30, "内容分析中…")

    full_text = "\n".join(t.get("text", "") for t in transcripts)

    try:
        analysis_result = _content_analyzer.analyze_transcript(full_text, existing_danmakus)
    except Exception as exc:
        logger.error("Content analysis error: %s", exc)
        analysis_result = {
            "summary": f"分析失败: {exc}",
            "key_topics": [],
            "speech_style": {},
            "audience_engagement": "",
        }

    await emit("speech_style", 50, "讲话风格分析…")
    speech_style = analysis_result.get("speech_style") or {}

    await emit("key_points", 60, "提取关键信息点…")
    try:
        key_points_raw = _content_analyzer.extract_key_points(full_text)
    except Exception as exc:
        logger.warning("Key points error: %s", exc)
        key_points_raw = []

    await emit("qa", 70, "提取问答对…")
    try:
        qa_pairs_raw = _qa_extractor.extract_qa_pairs(transcripts, existing_danmakus)
        qa_pairs_raw = _qa_extractor.categorize_questions(qa_pairs_raw)
    except Exception as exc:
        logger.warning("QA extraction error: %s", exc)
        qa_pairs_raw = []

    await emit("saving", 85, "保存分析结果…")

    import json

    db = _get_db()
    try:
        analysis_obj = Analysis(
            recording_id=recording_id,
            summary=analysis_result.get("summary", ""),
            speech_style=json.dumps(speech_style, ensure_ascii=False),
            key_topics=json.dumps(analysis_result.get("key_topics") or [], ensure_ascii=False),
            total_qa_count=len(qa_pairs_raw),
        )
        db.add(analysis_obj)
        db.flush()

        for kp in key_points_raw:
            db.add(KeyPoint(
                analysis_id=analysis_obj.id,
                content=kp.get("content", ""),
                importance=int(kp.get("importance") or 3),
                category=kp.get("category", "other"),
                timestamp=kp.get("timestamp"),
            ))

        for qa in qa_pairs_raw:
            db.add(QAPair(
                analysis_id=analysis_obj.id,
                question=qa.get("question", ""),
                answer=qa.get("answer") or "",
                timestamp=qa.get("timestamp"),
                category=qa.get("category", "other"),
                confidence=qa.get("confidence"),
            ))

        db.commit()
        db.refresh(analysis_obj)
        analysis_dict = analysis_obj.to_dict()
    finally:
        db.close()

    await emit("done", 100, "分析完成")
    await ws_manager.broadcast({
        "type": "analysis_complete",
        "data": {"recording_id": recording_id, "analysis_id": analysis_dict["id"]},
    })


@router.get("/analysis/{recording_id}")
def get_analysis(recording_id: int):
    db = _get_db()
    try:
        analysis = (
            db.query(Analysis)
            .filter(Analysis.recording_id == recording_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis.to_dict()
    finally:
        db.close()


@router.get("/analysis/{recording_id}/report")
def download_markdown_report(recording_id: int):
    db = _get_db()
    try:
        analysis = (
            db.query(Analysis)
            .filter(Analysis.recording_id == recording_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        rec = db.query(Recording).filter(Recording.id == recording_id).first()
        if not analysis or not rec:
            raise HTTPException(status_code=404, detail="Analysis or recording not found")
        analysis_dict = analysis.to_dict()
        recording_dict = rec.to_dict()
    finally:
        db.close()

    import json
    # Deserialise stored JSON strings
    if isinstance(analysis_dict.get("speech_style"), str):
        try:
            analysis_dict["speech_style"] = json.loads(analysis_dict["speech_style"])
        except Exception:
            analysis_dict["speech_style"] = {}
    if isinstance(analysis_dict.get("key_topics"), str):
        try:
            analysis_dict["key_topics"] = json.loads(analysis_dict["key_topics"])
        except Exception:
            analysis_dict["key_topics"] = []

    md = _report_generator.generate_markdown(analysis_dict, recording_dict)
    return Response(
        content=md.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="report_{recording_id}.md"'},
    )


@router.get("/analysis/{recording_id}/excel")
def download_excel_report(recording_id: int):
    db = _get_db()
    try:
        analysis = (
            db.query(Analysis)
            .filter(Analysis.recording_id == recording_id)
            .order_by(Analysis.created_at.desc())
            .first()
        )
        rec = db.query(Recording).filter(Recording.id == recording_id).first()
        if not analysis or not rec:
            raise HTTPException(status_code=404, detail="Analysis or recording not found")
        analysis_dict = analysis.to_dict()
        recording_dict = rec.to_dict()
    finally:
        db.close()

    import json
    if isinstance(analysis_dict.get("speech_style"), str):
        try:
            analysis_dict["speech_style"] = json.loads(analysis_dict["speech_style"])
        except Exception:
            analysis_dict["speech_style"] = {}
    if isinstance(analysis_dict.get("key_topics"), str):
        try:
            analysis_dict["key_topics"] = json.loads(analysis_dict["key_topics"])
        except Exception:
            analysis_dict["key_topics"] = []

    xlsx_bytes = _report_generator.generate_excel(analysis_dict, recording_dict)
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="report_{recording_id}.xlsx"'},
    )


# ─────────────────────────────────────────────────────────────────────
# WeChat / WeXin
# ─────────────────────────────────────────────────────────────────────

@router.post("/weixin/open")
def open_weixin(data: Optional[Dict[str, Any]] = None):
    data = data or {}
    weixin_id = data.get("weixin_id")
    if weixin_id:
        config_manager.save_weixin_id(weixin_id)
        success = _weixin_launcher.open_live_stream(weixin_id)
    else:
        success = _weixin_launcher.open_weixin()
    return {"success": success, "is_running": _weixin_launcher.is_weixin_running()}


# ─────────────────────────────────────────────────────────────────────
# Devices
# ─────────────────────────────────────────────────────────────────────

@router.get("/devices/audio")
def list_audio_devices():
    return {"devices": _audio_recorder.list_devices()}
