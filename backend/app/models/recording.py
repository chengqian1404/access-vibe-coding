from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False, default="未命名录制")
    stream_id = Column(String(128), nullable=True, index=True)
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Float, nullable=True)
    status = Column(String(32), nullable=False, default="idle")  # idle, recording, stopped, error
    screen_file = Column(String(512), nullable=True)
    audio_file = Column(String(512), nullable=True)
    video_file = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    transcripts = relationship("Transcript", back_populates="recording", cascade="all, delete-orphan")
    danmakus = relationship("Danmaku", back_populates="recording", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="recording", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "stream_id": self.stream_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "status": self.status,
            "screen_file": self.screen_file,
            "audio_file": self.audio_file,
            "video_file": self.video_file,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(Float, nullable=False, default=0.0)
    end_time = Column(Float, nullable=False, default=0.0)
    text = Column(Text, nullable=False, default="")
    confidence = Column(Float, nullable=True)
    speaker = Column(String(64), nullable=True)

    recording = relationship("Recording", back_populates="transcripts")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recording_id": self.recording_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "text": self.text,
            "confidence": self.confidence,
            "speaker": self.speaker,
        }


class Danmaku(Base):
    __tablename__ = "danmakus"

    id = Column(Integer, primary_key=True, index=True)
    recording_id = Column(Integer, ForeignKey("recordings.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(Float, nullable=False, default=0.0)
    username = Column(String(128), nullable=True)
    text = Column(Text, nullable=False, default="")
    is_question = Column(Integer, nullable=False, default=0)  # 0=False, 1=True (SQLite compat)

    recording = relationship("Recording", back_populates="danmakus")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "recording_id": self.recording_id,
            "timestamp": self.timestamp,
            "username": self.username,
            "text": self.text,
            "is_question": bool(self.is_question),
        }
