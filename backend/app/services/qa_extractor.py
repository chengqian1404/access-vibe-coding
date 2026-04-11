import json
from typing import Dict, List

from app.utils.logger import logger
from app.services.content_analyzer import ContentAnalyzer

QA_EXTRACT_PROMPT = """你是直播问答分析专家。请从以下直播转录文本和弹幕中提取问答对。

【主播转录文本（含时间戳）】
{transcript}

【弹幕消息（含时间戳）】
{danmaku}

规则：
1. 弹幕中以"？"结尾或明显提问语气的为问题
2. 找到主播在该弹幕时间戳后最近的回答段落
3. 如果主播没有直接回答，标记answer为null

以JSON数组格式返回：
[
  {{
    "question": "用户提问内容",
    "answer": "主播回答内容（无法确定则为null）",
    "timestamp": 123.4,
    "question_source": "danmaku",
    "confidence": 0.85
  }}
]"""

CATEGORIZE_PROMPT = """请对以下直播问答对进行分类：

{qa_pairs}

每个问答对添加category字段，分类选项：
- product_inquiry（产品咨询）
- price（价格询问）
- process（购买/使用流程）
- quality（质量相关）
- shipping（物流配送）
- promotion（优惠活动）
- comparison（产品对比）
- other（其他）

以JSON数组返回原数据加category字段。"""


class QaExtractor:
    """Extracts and categorises Q&A pairs from transcripts and danmaku."""

    def __init__(self) -> None:
        self._analyzer = ContentAnalyzer()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_qa_pairs(
        self,
        transcript_list: List[Dict],
        danmaku_list: List[Dict],
    ) -> List[Dict]:
        """
        Align danmaku questions with transcript answers using time proximity,
        then use LLM to refine and complete the pairing.
        Returns list of {question, answer, timestamp, confidence, category}.
        """
        # Step 1: Heuristic time-alignment
        candidate_questions = self._find_question_danmaku(danmaku_list)
        preliminary_pairs = self._align_with_transcript(candidate_questions, transcript_list)

        if not preliminary_pairs and not candidate_questions:
            logger.info("No danmaku questions found; falling back to LLM extraction")

        # Step 2: LLM-assisted extraction
        transcript_str = self._format_transcript(transcript_list)
        danmaku_str = self._format_danmaku(danmaku_list[:300])

        try:
            prompt = QA_EXTRACT_PROMPT.format(
                transcript=transcript_str[:6000],
                danmaku=danmaku_str[:2000],
            )
            raw = self._analyzer._call_llm(prompt)
            llm_pairs = self._analyzer._parse_json_response(raw, default=[])
            if isinstance(llm_pairs, list) and llm_pairs:
                return llm_pairs
        except Exception as exc:
            logger.error("QA LLM extraction error: %s", exc)

        return preliminary_pairs

    def categorize_questions(self, qa_pairs: List[Dict]) -> List[Dict]:
        """Add a 'category' field to each Q&A pair using LLM."""
        if not qa_pairs:
            return qa_pairs
        try:
            qa_str = json.dumps(qa_pairs[:50], ensure_ascii=False, indent=2)
            prompt = CATEGORIZE_PROMPT.format(qa_pairs=qa_str)
            raw = self._analyzer._call_llm(prompt)
            categorized = self._analyzer._parse_json_response(raw, default=qa_pairs)
            if isinstance(categorized, list) and len(categorized) == len(qa_pairs):
                return categorized
        except Exception as exc:
            logger.error("Categorize error: %s", exc)

        # Fallback: mark everything as 'other'
        for pair in qa_pairs:
            if "category" not in pair:
                pair["category"] = "other"
        return qa_pairs

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_question_danmaku(danmaku_list: List[Dict]) -> List[Dict]:
        question_markers = ("？", "?", "怎么", "如何", "什么", "哪里", "多少", "为什么", "可以吗", "能不能")
        questions = []
        for d in danmaku_list:
            text = d.get("text", "")
            if any(m in text for m in question_markers):
                questions.append(d)
        return questions

    @staticmethod
    def _align_with_transcript(
        questions: List[Dict],
        transcript_list: List[Dict],
        window: float = 30.0,
    ) -> List[Dict]:
        """Match each question danmaku to the nearest subsequent transcript segment."""
        pairs = []
        for q in questions:
            q_time = float(q.get("timestamp", 0))
            # Find transcript segments within the next `window` seconds
            answer_parts = []
            for seg in transcript_list:
                seg_start = float(seg.get("start", 0))
                if q_time <= seg_start <= q_time + window:
                    answer_parts.append(seg.get("text", ""))
            answer = "".join(answer_parts).strip() or None
            pairs.append({
                "question": q.get("text", ""),
                "answer": answer,
                "timestamp": q_time,
                "question_source": "danmaku",
                "confidence": 0.7 if answer else 0.4,
                "category": "other",
            })
        return pairs

    @staticmethod
    def _format_transcript(segments: List[Dict]) -> str:
        lines = []
        for seg in segments:
            start = seg.get("start", 0)
            text = seg.get("text", "").strip()
            if text:
                lines.append(f"[{start:.1f}s] {text}")
        return "\n".join(lines)

    @staticmethod
    def _format_danmaku(danmaku_list: List[Dict]) -> str:
        lines = []
        for d in danmaku_list:
            ts = d.get("timestamp", 0)
            user = d.get("username", "用户")
            text = d.get("text", "").strip()
            if text:
                lines.append(f"[{ts:.1f}s] {user}: {text}")
        return "\n".join(lines)
