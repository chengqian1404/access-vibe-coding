"""
LLM Service - Unified interface for multiple LLM providers
"""
import json
import os
from typing import Any, Dict, Optional
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import get_settings
from app.config.llm_providers import LLM_PROVIDERS, SYSTEM_PROMPT, INSTRUCTION_PROMPT_TEMPLATE
from app.services.config_manager import ConfigManager

settings = get_settings()


class LLMService:
    """Unified LLM interface supporting multiple providers."""

    def __init__(self):
        self.config_manager = ConfigManager()

    def _get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a provider."""
        saved_config = self.config_manager.get_provider_config(provider)
        default_config = LLM_PROVIDERS.get(provider, {})

        api_key = saved_config.get("api_key") or os.environ.get(
            f"{provider.upper()}_API_KEY", ""
        )
        base_url = saved_config.get("base_url") or default_config.get("base_url", "")
        model = saved_config.get("model") or default_config.get("default_model", "")

        return {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
            "type": default_config.get("type", "openai_compatible"),
        }

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def call_llm(
        self,
        prompt: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Call LLM API and return text response."""
        if not provider:
            provider = self.config_manager.get_default_provider() or settings.DEFAULT_LLM_PROVIDER

        config = self._get_provider_config(provider)
        if model:
            config["model"] = model

        provider_type = config.get("type", "openai_compatible")

        logger.debug(f"Calling LLM provider: {provider}, model: {config['model']}")

        if provider_type == "anthropic":
            return await self._call_anthropic(config, prompt, system_prompt)
        elif provider_type == "ollama":
            return await self._call_ollama(config, prompt, system_prompt)
        else:
            return await self._call_openai_compatible(config, prompt, system_prompt)

    async def _call_openai_compatible(
        self,
        config: Dict[str, Any],
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Call OpenAI-compatible API (OpenAI, Qwen, DeepSeek, etc.)."""
        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=config["api_key"],
                base_url=config["base_url"],
                timeout=settings.LLM_REQUEST_TIMEOUT,
            )

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await client.chat.completions.create(
                model=config["model"],
                messages=messages,
                temperature=0.1,
                response_format={"type": "json_object"},
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI-compatible API error: {e}")
            raise

    async def _call_anthropic(
        self,
        config: Dict[str, Any],
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Call Anthropic Claude API."""
        try:
            import anthropic

            client = anthropic.AsyncAnthropic(
                api_key=config["api_key"],
                base_url=config["base_url"],
                timeout=settings.LLM_REQUEST_TIMEOUT,
            )

            system = system_prompt or SYSTEM_PROMPT

            response = await client.messages.create(
                model=config["model"],
                max_tokens=4096,
                system=system,
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise

    async def _call_ollama(
        self,
        config: Dict[str, Any],
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """Call Ollama local API."""
        try:
            import aiohttp

            url = f"{config['base_url']}/api/chat"
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": config["model"],
                "messages": messages,
                "stream": False,
                "format": "json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=settings.LLM_REQUEST_TIMEOUT),
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data["message"]["content"]

        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    async def parse_instruction(
        self,
        instruction: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Parse natural language instruction into structured data."""
        prompt = INSTRUCTION_PROMPT_TEMPLATE.format(instruction=instruction)

        try:
            response_text = await self.call_llm(
                prompt=prompt,
                provider=provider,
                model=model,
                system_prompt=SYSTEM_PROMPT,
            )

            # Parse JSON response
            result = json.loads(response_text)
            logger.info(f"Instruction parsed successfully: action={result.get('action')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Return a fallback response
            return {
                "action": "other",
                "description": instruction,
                "params": {},
                "steps": [],
                "confidence": 0.5,
                "warnings": ["无法解析LLM响应，请重试"],
            }
        except Exception as e:
            logger.error(f"Failed to parse instruction: {e}")
            raise

    async def test_connection(self, provider: str, api_key: str, model: Optional[str] = None) -> bool:
        """Test LLM provider connection."""
        config = self._get_provider_config(provider)
        config["api_key"] = api_key
        if model:
            config["model"] = model

        test_prompt = 'Return this JSON: {"status": "ok"}'

        try:
            provider_type = config.get("type", "openai_compatible")
            if provider_type == "anthropic":
                result = await self._call_anthropic(config, test_prompt, "You are a test assistant.")
            elif provider_type == "ollama":
                result = await self._call_ollama(config, test_prompt, None)
            else:
                result = await self._call_openai_compatible(config, test_prompt, "You are a test assistant.")

            return bool(result)
        except Exception as e:
            logger.error(f"Connection test failed for {provider}: {e}")
            return False

    def get_available_providers(self) -> list:
        """Get list of available LLM providers."""
        return [
            {
                "id": provider_id,
                "name": provider_info["name"],
                "name_zh": provider_info["name_zh"],
                "models": provider_info["models"],
                "default_model": provider_info["default_model"],
                "requires_key": provider_info["requires_key"],
            }
            for provider_id, provider_info in LLM_PROVIDERS.items()
        ]
