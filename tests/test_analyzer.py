"""Unit tests for ContentAnalyzer, QaExtractor, and ReportGenerator."""

import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.content_analyzer import ContentAnalyzer
from app.services.qa_extractor import QaExtractor
from app.services.report_generator import ReportGenerator


SAMPLE_TRANSCRIPT = """[00:00] 大家好，欢迎来到今天的直播课。
[01:00] 今天我们讲的主题是 Python 异步编程。
[02:00] async 和 await 是 Python 3.5 引入的关键字。
[03:00] asyncio 事件循环负责调度协程的执行。"""

SAMPLE_DANMAKU = [
    {"timestamp": 30.0, "user": "用户A", "text": "老师，协程和线程有什么区别？"},
    {"timestamp": 90.0, "user": "用户B", "text": "async def 和普通 def 有什么不一样？"},
    {"timestamp": 150.0, "user": "用户C", "text": "事件循环是什么？"},
]

MOCK_ANALYSIS_JSON = {
    "summary": "本课讲解了 Python 异步编程的核心概念，包括 async/await 和 asyncio 事件循环。",
    "key_topics": ["async/await", "asyncio", "协程", "事件循环"],
    "speech_style": {
        "tone": "专业",
        "pace": "中等",
        "persuasion_techniques": [],
        "professionalism_score": 9,
        "strengths": ["讲解清晰"],
        "improvements": ["可增加更多示例"],
    },
    "audience_engagement": "学员积极提问，互动活跃",
}

MOCK_QA_JSON = [
    {
        "question": "协程和线程有什么区别？",
        "answer": "协程是用户态的轻量线程，由事件循环调度，无需系统切换开销。",
        "timestamp": 30.0,
        "question_source": "danmaku",
        "confidence": 0.91,
    },
    {
        "question": "async def 和普通 def 有什么不一样？",
        "answer": "async def 定义的函数返回协程对象，需要 await 调用。",
        "timestamp": 90.0,
        "question_source": "danmaku",
        "confidence": 0.88,
    },
]


# ── ContentAnalyzer Tests ─────────────────────────────────────────────────────

class TestContentAnalyzer(unittest.TestCase):
    """Test ContentAnalyzer with mock LLM responses."""

    def test_analyze_transcript_returns_dict(self):
        analyzer = ContentAnalyzer()
        with patch.object(analyzer, "_call_llm", return_value=json.dumps(MOCK_ANALYSIS_JSON)):
            result = analyzer.analyze_transcript(SAMPLE_TRANSCRIPT, SAMPLE_DANMAKU)
            self.assertIsInstance(result, dict)

    def test_analyze_transcript_extracts_summary(self):
        analyzer = ContentAnalyzer()
        with patch.object(analyzer, "_call_llm", return_value=json.dumps(MOCK_ANALYSIS_JSON)):
            result = analyzer.analyze_transcript(SAMPLE_TRANSCRIPT, SAMPLE_DANMAKU)
            self.assertIn("summary", result)

    def test_analyze_transcript_handles_invalid_json(self):
        analyzer = ContentAnalyzer()
        with patch.object(analyzer, "_call_llm", return_value="not-json"):
            result = analyzer.analyze_transcript(SAMPLE_TRANSCRIPT, SAMPLE_DANMAKU)
            self.assertIsInstance(result, dict)

    def test_analyze_transcript_handles_empty_input(self):
        analyzer = ContentAnalyzer()
        with patch.object(analyzer, "_call_llm", return_value=json.dumps({})):
            result = analyzer.analyze_transcript("", [])
            self.assertIsInstance(result, dict)

    def test_get_status_returns_dict(self):
        analyzer = ContentAnalyzer()
        status = analyzer.get_status()
        self.assertIsInstance(status, dict)


# ── QaExtractor Tests ─────────────────────────────────────────────────────────

class TestQaExtractor(unittest.TestCase):
    """Test QaExtractor with sample transcript and danmaku data."""

    def test_extract_qa_pairs_returns_list(self):
        extractor = QaExtractor()
        with patch.object(extractor._analyzer, "_call_llm", return_value=json.dumps(MOCK_QA_JSON)):
            with patch.object(extractor, "_align_with_transcript", return_value=MOCK_QA_JSON):
                result = extractor.extract_qa_pairs(
                    [{"start": 0, "end": 10, "text": SAMPLE_TRANSCRIPT}],
                    SAMPLE_DANMAKU,
                )
                self.assertIsInstance(result, list)

    def test_extract_qa_pairs_structure(self):
        extractor = QaExtractor()
        with patch.object(extractor, "_align_with_transcript", return_value=MOCK_QA_JSON):
            result = extractor.extract_qa_pairs(
                [{"start": 0, "end": 10, "text": SAMPLE_TRANSCRIPT}],
                SAMPLE_DANMAKU,
            )
            if result:
                first = result[0]
                self.assertIn("question", first)
                self.assertIn("answer", first)

    def test_extract_qa_pairs_empty_danmaku(self):
        extractor = QaExtractor()
        result = extractor.extract_qa_pairs(
            [{"start": 0, "end": 10, "text": "some text"}],
            [],
        )
        self.assertEqual(result, [])

    def test_categorize_questions_returns_list(self):
        extractor = QaExtractor()
        with patch.object(extractor._analyzer, "_call_llm", return_value=json.dumps(MOCK_QA_JSON)):
            result = extractor.categorize_questions(MOCK_QA_JSON)
            self.assertIsInstance(result, list)


# ── ReportGenerator Tests ─────────────────────────────────────────────────────

class TestReportGenerator(unittest.TestCase):
    """Test ReportGenerator output format and Markdown structure."""

    def setUp(self):
        self.generator = ReportGenerator()
        self.recording = {
            "title": "Python 异步编程直播课",
            "created_at": "2024-01-01T12:00:00",
            "duration": 3600,
        }
        self.analysis = {
            **MOCK_ANALYSIS_JSON,
            "qa_pairs": MOCK_QA_JSON,
            "transcript": SAMPLE_TRANSCRIPT,
        }

    def test_generate_markdown_returns_string(self):
        md = self.generator.generate_markdown(self.analysis, self.recording)
        self.assertIsInstance(md, str)

    def test_markdown_contains_title(self):
        md = self.generator.generate_markdown(self.analysis, self.recording)
        self.assertIn("直播学习分析报告", md)

    def test_markdown_contains_summary_section(self):
        md = self.generator.generate_markdown(self.analysis, self.recording)
        self.assertIn("概述", md)

    def test_markdown_contains_recording_title(self):
        md = self.generator.generate_markdown(self.analysis, self.recording)
        self.assertIn("Python 异步编程直播课", md)

    def test_markdown_contains_key_topics(self):
        md = self.generator.generate_markdown(self.analysis, self.recording)
        self.assertTrue(
            any(topic in md for topic in MOCK_ANALYSIS_JSON["key_topics"])
        )

    def test_markdown_structure_has_headers(self):
        md = self.generator.generate_markdown(self.analysis, self.recording)
        self.assertIn("##", md)

    def test_generate_markdown_empty_analysis(self):
        md = self.generator.generate_markdown({}, self.recording)
        self.assertIsInstance(md, str)
        self.assertGreater(len(md), 0)


if __name__ == "__main__":
    unittest.main()
