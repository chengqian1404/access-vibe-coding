"""
Data Models for Instructions
"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ActionType(str, Enum):
    CREATE_TABLE = "create_table"
    MODIFY_TABLE = "modify_table"
    IMPORT_DATA = "import_data"
    QUERY_DATA = "query_data"
    CREATE_FORM = "create_form"
    CREATE_REPORT = "create_report"
    RUN_MACRO = "run_macro"
    EXECUTE_VBA = "execute_vba"
    OPEN_DATABASE = "open_database"
    CLOSE_DATABASE = "close_database"
    OTHER = "other"


class InstructionRequest(BaseModel):
    instruction: str = Field(..., min_length=1, max_length=2000, description="自然语言指令")
    provider: Optional[str] = Field(None, description="LLM提供商")
    model: Optional[str] = Field(None, description="LLM模型")
    session_id: Optional[str] = Field(None, description="会话ID")


class ParsedInstruction(BaseModel):
    action: ActionType = Field(..., description="操作类型")
    description: str = Field(..., description="操作描述")
    params: Dict[str, Any] = Field(default_factory=dict, description="操作参数")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="操作步骤")
    confidence: float = Field(default=0.9, ge=0.0, le=1.0, description="置信度")
    warnings: List[str] = Field(default_factory=list, description="警告信息")


class ExecutionRequest(BaseModel):
    instruction: str = Field(..., description="原始指令")
    parsed: ParsedInstruction = Field(..., description="解析后的指令")
    session_id: Optional[str] = Field(None, description="会话ID")
    dry_run: bool = Field(default=False, description="是否只模拟执行")


class InstructionHistory(BaseModel):
    id: str = Field(..., description="历史记录ID")
    instruction: str = Field(..., description="原始指令")
    parsed_action: str = Field(..., description="解析的操作类型")
    status: str = Field(..., description="执行状态")
    created_at: str = Field(..., description="创建时间")
    execution_time: Optional[float] = Field(None, description="执行时间（秒）")
    result: Optional[Dict[str, Any]] = Field(None, description="执行结果")
