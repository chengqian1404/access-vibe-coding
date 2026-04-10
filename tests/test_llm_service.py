"""
Tests for LLM Service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.llm_service import LLMService


@pytest.fixture
def llm_service():
    return LLMService()


@pytest.mark.asyncio
async def test_parse_instruction_returns_dict(llm_service):
    """Test that parse_instruction returns a dictionary."""
    mock_response = json.dumps({
        "action": "create_table",
        "description": "创建员工信息表",
        "params": {"table_name": "Employees", "fields": []},
        "steps": [],
        "confidence": 0.95,
        "warnings": [],
    })

    with patch.object(llm_service, 'call_llm', new=AsyncMock(return_value=mock_response)):
        result = await llm_service.parse_instruction("创建员工表")
        assert isinstance(result, dict)
        assert result["action"] == "create_table"
        assert result["confidence"] == 0.95


@pytest.mark.asyncio
async def test_parse_instruction_invalid_json_returns_fallback(llm_service):
    """Test that invalid JSON from LLM returns fallback response."""
    with patch.object(llm_service, 'call_llm', new=AsyncMock(return_value="not valid json")):
        result = await llm_service.parse_instruction("some instruction")
        assert isinstance(result, dict)
        assert result["action"] == "other"
        assert len(result["warnings"]) > 0


@pytest.mark.asyncio
async def test_test_connection_success(llm_service):
    """Test successful connection test."""
    with patch.object(llm_service, '_call_openai_compatible', new=AsyncMock(return_value='{"status": "ok"}')):
        result = await llm_service.test_connection("openai", "sk-test123")
        assert result is True


@pytest.mark.asyncio
async def test_test_connection_failure(llm_service):
    """Test failed connection test."""
    with patch.object(
        llm_service, '_call_openai_compatible',
        new=AsyncMock(side_effect=Exception("Connection refused"))
    ):
        result = await llm_service.test_connection("openai", "invalid-key")
        assert result is False


def test_get_available_providers(llm_service):
    """Test that available providers list is returned."""
    providers = llm_service.get_available_providers()
    assert isinstance(providers, list)
    assert len(providers) > 0

    provider_ids = [p["id"] for p in providers]
    assert "openai" in provider_ids
    assert "qwen" in provider_ids
    assert "claude" in provider_ids
    assert "deepseek" in provider_ids
    assert "ollama" in provider_ids


def test_provider_has_required_fields(llm_service):
    """Test that each provider has required fields."""
    providers = llm_service.get_available_providers()
    required_fields = {"id", "name", "name_zh", "models", "default_model", "requires_key"}

    for provider in providers:
        for field in required_fields:
            assert field in provider, f"Provider {provider['id']} missing field: {field}"
