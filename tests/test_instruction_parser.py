"""
Tests for Instruction Parser
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.instruction_parser import InstructionParser
from app.models.instruction import ActionType, ParsedInstruction
from app.models.operation import StepType


@pytest.fixture
def parser():
    return InstructionParser()


def test_parse_create_table(parser):
    """Test parsing a create table instruction."""
    llm_response = {
        "action": "create_table",
        "description": "创建员工表",
        "params": {
            "table_name": "Employees",
            "fields": [
                {"name": "ID", "type": "AutoNumber"},
                {"name": "Name", "type": "Text"},
                {"name": "Salary", "type": "Currency"},
            ]
        },
        "steps": [],
        "confidence": 0.95,
        "warnings": [],
    }

    parsed = parser.parse(llm_response)

    assert isinstance(parsed, ParsedInstruction)
    assert parsed.action == ActionType.CREATE_TABLE
    assert parsed.description == "创建员工表"
    assert parsed.confidence == 0.95
    assert len(parsed.steps) > 0  # Should generate default steps


def test_parse_import_data(parser):
    """Test parsing an import data instruction."""
    llm_response = {
        "action": "import_data",
        "description": "导入Excel数据",
        "params": {
            "file_path": "C:\\data\\sales.xlsx",
            "table_name": "Sales",
        },
        "steps": [],
        "confidence": 0.88,
        "warnings": [],
    }

    parsed = parser.parse(llm_response)

    assert parsed.action == ActionType.IMPORT_DATA
    assert len(parsed.steps) > 0


def test_parse_unknown_action_defaults_to_other(parser):
    """Test that unknown action type defaults to 'other'."""
    llm_response = {
        "action": "unknown_action_xyz",
        "description": "未知操作",
        "params": {},
        "steps": [],
        "confidence": 0.5,
        "warnings": [],
    }

    parsed = parser.parse(llm_response)
    assert parsed.action == ActionType.OTHER


def test_parse_with_provided_steps(parser):
    """Test parsing when LLM provides explicit steps."""
    custom_steps = [
        {"step": 1, "type": "focus_window", "description": "激活窗口", "params": {"window_title": "Microsoft Access"}},
        {"step": 2, "type": "hotkey", "description": "按快捷键", "params": {"keys": ["ctrl", "s"]}},
    ]

    llm_response = {
        "action": "create_table",
        "description": "创建表",
        "params": {},
        "steps": custom_steps,
        "confidence": 0.9,
        "warnings": [],
    }

    parsed = parser.parse(llm_response)
    assert len(parsed.steps) == len(custom_steps)


def test_to_operation_steps(parser):
    """Test conversion to OperationStep objects."""
    llm_response = {
        "action": "create_table",
        "description": "创建表",
        "params": {"table_name": "Test", "fields": []},
        "steps": [],
        "confidence": 0.9,
        "warnings": [],
    }

    parsed = parser.parse(llm_response)
    op_steps = parser.to_operation_steps(parsed)

    assert isinstance(op_steps, list)
    assert len(op_steps) > 0

    # Check that each step has required attributes
    for step in op_steps:
        assert hasattr(step, 'step')
        assert hasattr(step, 'type')
        assert hasattr(step, 'description')


def test_parse_query_data(parser):
    """Test parsing a query instruction."""
    llm_response = {
        "action": "query_data",
        "description": "查询高薪员工",
        "params": {
            "table_name": "Employees",
            "conditions": "Salary > 8000",
        },
        "steps": [],
        "confidence": 0.92,
        "warnings": [],
    }

    parsed = parser.parse(llm_response)
    assert parsed.action == ActionType.QUERY_DATA
    assert parsed.params["table_name"] == "Employees"


def test_parse_with_warnings(parser):
    """Test that warnings are preserved."""
    warnings = ["操作可能影响现有数据", "请先备份"]
    llm_response = {
        "action": "modify_table",
        "description": "修改表结构",
        "params": {},
        "steps": [],
        "confidence": 0.7,
        "warnings": warnings,
    }

    parsed = parser.parse(llm_response)
    assert parsed.warnings == warnings
