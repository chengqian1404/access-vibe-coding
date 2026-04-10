"""
API Routes - FastAPI route handlers
"""
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from loguru import logger

from app.models.config import ConfigUpdateRequest
from app.models.instruction import ExecutionRequest, InstructionRequest, ParsedInstruction
from app.services.access_automation import AccessAutomation
from app.services.config_manager import ConfigManager
from app.services.instruction_parser import InstructionParser
from app.services.llm_service import LLMService
from app.services.screenshot_service import ScreenshotService
from app.services.session_manager import get_session_manager

router = APIRouter()

# Service instances
llm_service = LLMService()
instruction_parser = InstructionParser()
automation = AccessAutomation()
screenshot_service = ScreenshotService()
config_manager = ConfigManager()


# ─── Instruction Endpoints ────────────────────────────────────────────────────

@router.post("/instruction/parse", response_model=Dict[str, Any])
async def parse_instruction(request: InstructionRequest):
    """Parse a natural language instruction using LLM."""
    try:
        logger.info(f"Parsing instruction: {request.instruction[:100]}...")
        llm_response = await llm_service.parse_instruction(
            instruction=request.instruction,
            provider=request.provider,
            model=request.model,
        )
        parsed = instruction_parser.parse(llm_response)
        return {
            "success": True,
            "parsed": parsed.model_dump(),
        }
    except Exception as e:
        logger.error(f"Failed to parse instruction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/instruction/execute", response_model=Dict[str, Any])
async def execute_instruction(request: ExecutionRequest, background_tasks: BackgroundTasks):
    """Execute a parsed instruction."""
    session_manager = get_session_manager()
    session_id = request.session_id or session_manager.create_session()

    try:
        logger.info(f"Executing instruction: {request.instruction[:100]}...")

        # Convert parsed instruction to operation steps
        operation_steps = instruction_parser.to_operation_steps(request.parsed)

        # Execute the steps
        result = await automation.execute_steps(operation_steps, dry_run=request.dry_run)

        # Record in history
        background_tasks.add_task(
            session_manager.add_to_history,
            instruction=request.instruction,
            action=request.parsed.action.value,
            status="success" if result.success else "failed",
            result=result.model_dump(),
            execution_time=result.execution_time,
        )

        return {
            "success": result.success,
            "session_id": session_id,
            "result": result.model_dump(),
        }
    except Exception as e:
        logger.error(f"Failed to execute instruction: {e}")
        session_manager.add_to_history(
            instruction=request.instruction,
            action=request.parsed.action.value,
            status="error",
        )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/instruction/run", response_model=Dict[str, Any])
async def run_instruction(request: InstructionRequest, background_tasks: BackgroundTasks):
    """Parse and execute an instruction in one step."""
    try:
        logger.info(f"Running instruction: {request.instruction[:100]}...")

        # Step 1: Parse
        llm_response = await llm_service.parse_instruction(
            instruction=request.instruction,
            provider=request.provider,
            model=request.model,
        )
        parsed = instruction_parser.parse(llm_response)

        # Step 2: Execute
        operation_steps = instruction_parser.to_operation_steps(parsed)
        result = await automation.execute_steps(operation_steps)

        session_manager = get_session_manager()
        background_tasks.add_task(
            session_manager.add_to_history,
            instruction=request.instruction,
            action=parsed.action.value,
            status="success" if result.success else "failed",
            result=result.model_dump(),
            execution_time=result.execution_time,
        )

        return {
            "success": result.success,
            "parsed": parsed.model_dump(),
            "result": result.model_dump(),
        }
    except Exception as e:
        logger.error(f"Failed to run instruction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Screenshot Endpoints ─────────────────────────────────────────────────────

@router.get("/screenshot")
async def get_screenshot():
    """Take and return a screenshot."""
    screenshot = screenshot_service.take_screenshot_base64()
    if screenshot:
        return {"success": True, "screenshot": screenshot}
    raise HTTPException(status_code=500, detail="截图失败")


# ─── Configuration Endpoints ──────────────────────────────────────────────────

@router.get("/config")
async def get_config():
    """Get current application configuration."""
    return {
        "success": True,
        "config": config_manager.get_all_settings(),
    }


@router.post("/config/provider")
async def update_provider_config(request: ConfigUpdateRequest):
    """Update LLM provider configuration."""
    try:
        config_manager.set_provider_config(
            provider=request.provider,
            api_key=request.api_key,
            base_url=request.base_url,
            model=request.model,
        )
        return {"success": True, "message": f"已保存 {request.provider} 配置"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config/provider/test")
async def test_provider_connection(request: ConfigUpdateRequest):
    """Test LLM provider connection."""
    try:
        success = await llm_service.test_connection(
            provider=request.provider,
            api_key=request.api_key,
            model=request.model,
        )
        if success:
            return {"success": True, "message": "连接测试成功"}
        else:
            return {"success": False, "message": "连接测试失败，请检查API密钥和网络"}
    except Exception as e:
        logger.error(f"Connection test exception for {request.provider}: {e}")
        return {"success": False, "message": "连接测试失败，请检查API密钥和网络连接"}


@router.delete("/config/provider/{provider}")
async def delete_provider_config(provider: str):
    """Delete provider configuration."""
    deleted = config_manager.delete_provider_config(provider)
    if deleted:
        return {"success": True, "message": f"已删除 {provider} 配置"}
    raise HTTPException(status_code=404, detail=f"未找到 {provider} 配置")


@router.post("/config/default-provider")
async def set_default_provider(provider: str = Query(...)):
    """Set the default LLM provider."""
    config_manager.set_default_provider(provider)
    return {"success": True, "message": f"已设置默认提供商为 {provider}"}


# ─── LLM Providers Endpoints ──────────────────────────────────────────────────

@router.get("/providers")
async def get_providers():
    """Get list of available LLM providers."""
    providers = llm_service.get_available_providers()
    return {"success": True, "providers": providers}


# ─── History Endpoints ────────────────────────────────────────────────────────

@router.get("/history")
async def get_history(limit: int = Query(default=20, le=100), offset: int = Query(default=0)):
    """Get execution history."""
    session_manager = get_session_manager()
    history = session_manager.get_history(limit=limit, offset=offset)
    return {"success": True, "history": history}


@router.delete("/history")
async def clear_history():
    """Clear all execution history."""
    session_manager = get_session_manager()
    session_manager.clear_history()
    return {"success": True, "message": "历史记录已清除"}


@router.delete("/history/{item_id}")
async def delete_history_item(item_id: str):
    """Delete a specific history item."""
    session_manager = get_session_manager()
    deleted = session_manager.delete_history_item(item_id)
    if deleted:
        return {"success": True, "message": "历史记录已删除"}
    raise HTTPException(status_code=404, detail="历史记录不存在")


# ─── System Endpoints ─────────────────────────────────────────────────────────

@router.get("/system/info")
async def get_system_info():
    """Get system information."""
    from app.utils.helpers import get_platform_info, is_windows
    return {
        "success": True,
        "info": {
            **get_platform_info(),
            "access_running": automation.is_access_running(),
            "is_windows": is_windows(),
        },
    }


@router.get("/templates")
async def get_templates():
    """Get instruction templates."""
    import json
    from pathlib import Path

    templates_file = Path(__file__).parent.parent.parent.parent / "resources" / "templates" / "instruction_templates.json"
    if templates_file.exists():
        with open(templates_file, "r", encoding="utf-8") as f:
            templates = json.load(f)
        return {"success": True, "templates": templates}
    return {"success": True, "templates": []}
