"""
Operation Step Models
"""
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class StepType(str, Enum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    KEY_PRESS = "key_press"
    HOTKEY = "hotkey"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    SCROLL = "scroll"
    MOVE = "move"
    DRAG = "drag"
    FIND_WINDOW = "find_window"
    FOCUS_WINDOW = "focus_window"
    COM_CALL = "com_call"


class OperationStep(BaseModel):
    step: int = Field(..., description="步骤序号")
    type: StepType = Field(..., description="操作类型")
    description: str = Field(default="", description="步骤描述")
    params: Dict[str, Any] = Field(default_factory=dict, description="操作参数")
    timeout: float = Field(default=5.0, description="超时时间（秒）")
    retry_count: int = Field(default=0, description="重试次数")


class StepResult(BaseModel):
    step: int = Field(..., description="步骤序号")
    success: bool = Field(..., description="是否成功")
    message: str = Field(default="", description="结果消息")
    screenshot: Optional[str] = Field(None, description="截图（base64编码）")
    error: Optional[str] = Field(None, description="错误信息")
    duration: float = Field(default=0.0, description="执行时间（秒）")


class ExecutionResult(BaseModel):
    success: bool = Field(..., description="整体是否成功")
    total_steps: int = Field(..., description="总步骤数")
    completed_steps: int = Field(..., description="已完成步骤数")
    step_results: list = Field(default_factory=list, description="各步骤结果")
    final_screenshot: Optional[str] = Field(None, description="最终截图")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(default=0.0, description="总执行时间（秒）")
