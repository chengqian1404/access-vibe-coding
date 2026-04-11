import json
from typing import Any, Dict, List, Optional

from app.utils.logger import logger

ANALYSIS_PROMPT_TEMPLATE = """你是一名专业的直播内容分析师。请分析以下直播转录文本和弹幕互动内容，提供详细分析。

【直播转录文本】
{transcript}

【弹幕互动列表】
{danmaku}

请以JSON格式返回以下分析结果：
{{
  "summary": "直播内容总结（200字以内）",
  "key_topics": ["话题1", "话题2", "话题3"],
  "speech_style": {{
    "tone": "语气风格描述",
    "pace": "语速评估（快/中/慢）",
    "persuasion_techniques": ["技巧1", "技巧2"],
    "professionalism": "专业度评分说明",
    "strengths": ["优点1", "优点2"],
    "improvements": ["建议1", "建议2"]
  }},
  "audience_engagement": "受众互动情况分析"
}}"""

SPEECH_STYLE_PROMPT = """请分析以下直播主播的讲话风格：

{transcript}

以JSON格式返回：
{{
  "tone": "语气（亲切/专业/热情/平和等）",
  "pace": "语速（快/中等/慢）",
  "vocabulary_level": "用词水平（专业/通俗/混合）",
  "persuasion_techniques": ["使用的营销话术列表"],
  "call_to_action": ["号召行动语句"],
  "professionalism_score": 8,
  "strengths": ["讲话优势列表"],
  "improvement_suggestions": ["改进建议列表"]
}}"""

KEY_POINTS_PROMPT = """请从以下直播文本中提取关键信息点：

{transcript}

以JSON格式返回关键点列表：
[
  {{
    "content": "关键点内容",
    "category": "分类（产品介绍/价格信息/促销活动/使用方法/其他）",
    "importance": 5,
    "timestamp_hint": "大约出现时间描述"
  }}
]
importance评分1-5，5为最重要。"""


class ContentAnalyzer:
    """Uses LLM APIs to analyze live stream transcripts and danmaku."""

    def __init__(self) -> None:
        self._status: str = "idle"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_transcript(self, transcript_text: str, danmaku_list: List[Dict]) -> Dict:
        self._status = "analyzing"
        try:
            danmaku_str = "\n".join(
                f"[{d.get('timestamp', 0):.1f}s] {d.get('username', '用户')}: {d.get('text', '')}"
                for d in danmaku_list[:200]
            )
            prompt = ANALYSIS_PROMPT_TEMPLATE.format(
                transcript=transcript_text[:8000],
                danmaku=danmaku_str[:2000] or "（无弹幕数据）",
            )
            raw = self._call_llm(prompt)
            return self._parse_json_response(raw, default={
                "summary": "分析失败",
                "key_topics": [],
                "speech_style": {},
                "audience_engagement": "",
            })
        finally:
            self._status = "idle"

    def analyze_speech_style(self, transcript_text: str) -> Dict:
        self._status = "analyzing"
        try:
            prompt = SPEECH_STYLE_PROMPT.format(transcript=transcript_text[:8000])
            raw = self._call_llm(prompt)
            return self._parse_json_response(raw, default={
                "tone": "未知",
                "pace": "中等",
                "vocabulary_level": "通俗",
                "persuasion_techniques": [],
                "call_to_action": [],
                "professionalism_score": 5,
                "strengths": [],
                "improvement_suggestions": [],
            })
        finally:
            self._status = "idle"

    def extract_key_points(self, transcript_text: str) -> List[Dict]:
        self._status = "analyzing"
        try:
            prompt = KEY_POINTS_PROMPT.format(transcript=transcript_text[:8000])
            raw = self._call_llm(prompt)
            result = self._parse_json_response(raw, default=[])
            if isinstance(result, list):
                return result
            return []
        finally:
            self._status = "idle"

    def get_status(self) -> Dict:
        return {"status": self._status}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _get_client_and_model(self):
        from app.services.config_manager import config_manager
        cfg = config_manager.get_llm_config()
        provider = cfg.get("provider", "qwen")
        api_key = cfg.get("api_key", "")
        base_url = cfg.get("base_url", "")
        model = cfg.get("model", "qwen-max")

        if not api_key:
            raise ValueError(f"API key for provider '{provider}' is not configured")

        if provider == "claude":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            return client, model, "claude"

        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url)
        return client, model, "openai_compat"

    def _call_llm(self, prompt: str) -> str:
        try:
            client, model, client_type = self._get_client_and_model()

            if client_type == "claude":
                response = client.messages.create(
                    model=model,
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )
                return response.content[0].text if response.content else ""

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的直播内容分析助手，返回结构化JSON数据。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=4096,
            )
            return response.choices[0].message.content or ""
        except Exception as exc:
            logger.error("LLM call error: %s", exc)
            raise

    @staticmethod
    def _parse_json_response(raw: str, default: Any = None) -> Any:
        """Extract and parse JSON from LLM response text."""
        if not raw:
            return default
        # Strip markdown code fences if present
        text = raw.strip()
        for fence in ("```json", "```"):
            if text.startswith(fence):
                text = text[len(fence):]
            if text.endswith("```"):
                text = text[:-3]
        text = text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON substring
            import re
            match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except Exception:
                    pass
            logger.warning("Failed to parse LLM JSON response: %s…", text[:200])
            return default
