"""
LLM Providers Configuration
"""
from typing import Dict, Any

LLM_PROVIDERS: Dict[str, Any] = {
    "openai": {
        "name": "OpenAI",
        "name_zh": "OpenAI",
        "models": [
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "context": 128000},
            {"id": "gpt-4o", "name": "GPT-4o", "context": 128000},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini", "context": 128000},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "context": 16385},
        ],
        "default_model": "gpt-4-turbo",
        "base_url": "https://api.openai.com/v1",
        "requires_key": True,
        "type": "openai_compatible",
    },
    "qwen": {
        "name": "Qwen (通义千问)",
        "name_zh": "通义千问",
        "models": [
            {"id": "qwen-max", "name": "Qwen Max", "context": 8000},
            {"id": "qwen-plus", "name": "Qwen Plus", "context": 32000},
            {"id": "qwen-turbo", "name": "Qwen Turbo", "context": 8000},
            {"id": "qwen-long", "name": "Qwen Long", "context": 1000000},
        ],
        "default_model": "qwen-max",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "requires_key": True,
        "type": "openai_compatible",
    },
    "claude": {
        "name": "Claude (Anthropic)",
        "name_zh": "Claude",
        "models": [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet", "context": 200000},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet", "context": 200000},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku", "context": 200000},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus", "context": 200000},
        ],
        "default_model": "claude-3-5-sonnet-20241022",
        "base_url": "https://api.anthropic.com",
        "requires_key": True,
        "type": "anthropic",
    },
    "deepseek": {
        "name": "DeepSeek",
        "name_zh": "DeepSeek",
        "models": [
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "context": 64000},
            {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner", "context": 64000},
        ],
        "default_model": "deepseek-chat",
        "base_url": "https://api.deepseek.com",
        "requires_key": True,
        "type": "openai_compatible",
    },
    "ollama": {
        "name": "Ollama (本地)",
        "name_zh": "Ollama 本地模型",
        "models": [
            {"id": "qwen:7b", "name": "Qwen 7B", "context": 8000},
            {"id": "qwen:14b", "name": "Qwen 14B", "context": 8000},
            {"id": "llama3:8b", "name": "Llama 3 8B", "context": 8000},
            {"id": "mistral:7b", "name": "Mistral 7B", "context": 8000},
        ],
        "default_model": "qwen:7b",
        "base_url": "http://localhost:11434",
        "requires_key": False,
        "type": "ollama",
    },
}

# System prompt template for instruction parsing
SYSTEM_PROMPT = """你是一个专业的 Microsoft Access 数据库助手。用户将用自然语言描述他们想在 Access 中执行的操作，你需要将这些指令解析为结构化的 JSON 格式。

你的任务是：
1. 理解用户的自然语言指令
2. 识别需要执行的 Access 操作类型
3. 提取操作所需的参数
4. 生成详细的操作步骤

支持的操作类型：
- create_table: 创建数据表
- modify_table: 修改数据表结构
- import_data: 导入数据（Excel/CSV）
- query_data: 查询数据
- create_form: 创建窗体
- create_report: 创建报表
- run_macro: 运行宏
- execute_vba: 执行 VBA 代码
- open_database: 打开数据库
- close_database: 关闭数据库
- other: 其他操作

请始终返回有效的 JSON 格式，不要包含任何额外的文本或解释。
"""

INSTRUCTION_PROMPT_TEMPLATE = """用户指令：{instruction}

请将上述指令解析为以下 JSON 格式：
{{
    "action": "操作类型",
    "description": "操作描述",
    "params": {{
        // 根据操作类型填写相应参数
    }},
    "steps": [
        {{
            "step": 1,
            "type": "操作类型（click/type/wait/screenshot等）",
            "description": "步骤描述",
            "params": {{}}
        }}
    ],
    "confidence": 0.95,
    "warnings": []
}}

操作参数说明：
- create_table: {{"table_name": "表名", "fields": [{{"name": "字段名", "type": "字段类型", "required": true}}]}}
- import_data: {{"file_path": "文件路径", "table_name": "目标表名", "has_header": true}}
- query_data: {{"table_name": "表名", "conditions": "查询条件", "fields": ["字段1", "字段2"]}}
- create_form: {{"form_name": "窗体名", "table_name": "数据源表名", "fields": ["字段1"]}}
- create_report: {{"report_name": "报表名", "table_name": "数据源表名"}}

字段类型支持：Text（文本）、Number（数字）、Date/Time（日期/时间）、Yes/No（是/否）、AutoNumber（自动编号）、Currency（货币）、Memo（备注）

请确保返回有效的 JSON。
"""
