"""
Configuration Models
"""
from typing import Optional
from pydantic import BaseModel, Field


class LLMProviderConfig(BaseModel):
    provider: str = Field(..., description="提供商名称")
    api_key: Optional[str] = Field(None, description="API密钥（加密存储）")
    base_url: Optional[str] = Field(None, description="API基础URL")
    model: Optional[str] = Field(None, description="模型名称")
    timeout: int = Field(default=30, description="请求超时（秒）")
    max_retries: int = Field(default=3, description="最大重试次数")


class AppConfig(BaseModel):
    default_provider: str = Field(default="openai", description="默认LLM提供商")
    providers: dict = Field(default_factory=dict, description="各提供商配置")
    automation_delay: float = Field(default=0.1, description="自动化操作间隔（秒）")
    screenshot_enabled: bool = Field(default=True, description="是否启用截图")
    language: str = Field(default="zh-CN", description="界面语言")
    theme: str = Field(default="light", description="界面主题")
    save_history: bool = Field(default=True, description="是否保存历史记录")
    max_history: int = Field(default=100, description="最大历史记录数")


class ConfigUpdateRequest(BaseModel):
    provider: str = Field(..., description="提供商名称")
    api_key: str = Field(..., description="API密钥")
    base_url: Optional[str] = Field(None, description="自定义API URL")
    model: Optional[str] = Field(None, description="模型名称")
