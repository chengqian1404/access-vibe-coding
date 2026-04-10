"""
Instruction Parser - Convert LLM output to executable automation steps
"""
from typing import Any, Dict, List, Optional
from loguru import logger

from app.models.instruction import ParsedInstruction, ActionType
from app.models.operation import OperationStep, StepType


class InstructionParser:
    """Converts LLM parsed instructions into executable automation steps."""

    def parse(self, llm_response: Dict[str, Any]) -> ParsedInstruction:
        """Parse LLM response into a structured ParsedInstruction object."""
        try:
            action = llm_response.get("action", "other")
            # Normalize action type
            try:
                action_type = ActionType(action)
            except ValueError:
                action_type = ActionType.OTHER

            parsed = ParsedInstruction(
                action=action_type,
                description=llm_response.get("description", ""),
                params=llm_response.get("params", {}),
                steps=llm_response.get("steps", []),
                confidence=llm_response.get("confidence", 0.9),
                warnings=llm_response.get("warnings", []),
            )

            # If no steps provided, generate default steps based on action
            if not parsed.steps:
                parsed.steps = self._generate_default_steps(action_type, parsed.params)

            logger.debug(f"Parsed instruction: action={parsed.action}, steps={len(parsed.steps)}")
            return parsed

        except Exception as e:
            logger.error(f"Failed to parse instruction: {e}")
            raise

    def _generate_default_steps(
        self, action: ActionType, params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate default automation steps based on action type."""
        steps = []

        if action == ActionType.CREATE_TABLE:
            steps = self._steps_create_table(params)
        elif action == ActionType.IMPORT_DATA:
            steps = self._steps_import_data(params)
        elif action == ActionType.QUERY_DATA:
            steps = self._steps_query_data(params)
        elif action == ActionType.CREATE_FORM:
            steps = self._steps_create_form(params)
        elif action == ActionType.CREATE_REPORT:
            steps = self._steps_create_report(params)
        elif action == ActionType.OPEN_DATABASE:
            steps = self._steps_open_database(params)

        return steps

    def _steps_create_table(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Steps to create a table in Access."""
        table_name = params.get("table_name", "NewTable")
        fields = params.get("fields", [])

        steps = [
            {
                "step": 1,
                "type": StepType.FIND_WINDOW,
                "description": "查找 Access 窗口",
                "params": {"window_title": "Microsoft Access"},
            },
            {
                "step": 2,
                "type": StepType.FOCUS_WINDOW,
                "description": "激活 Access 窗口",
                "params": {"window_title": "Microsoft Access"},
            },
            {
                "step": 3,
                "type": StepType.SCREENSHOT,
                "description": "截图确认当前状态",
                "params": {},
            },
            {
                "step": 4,
                "type": StepType.HOTKEY,
                "description": "通过功能区创建新表（设计视图）",
                "params": {"keys": ["alt", "n", "t", "d"]},
            },
            {
                "step": 5,
                "type": StepType.WAIT,
                "description": "等待表设计视图打开",
                "params": {"seconds": 1.0},
            },
            {
                "step": 6,
                "type": StepType.SCREENSHOT,
                "description": "截图确认设计视图已打开",
                "params": {},
            },
        ]

        # Add steps to define each field
        step_num = 7
        for i, field in enumerate(fields):
            field_name = field.get("name", f"Field{i+1}")
            field_type = field.get("type", "Text")

            steps.append({
                "step": step_num,
                "type": StepType.TYPE,
                "description": f"输入字段名: {field_name}",
                "params": {"text": field_name, "submit": True},
            })
            step_num += 1

            steps.append({
                "step": step_num,
                "type": StepType.TYPE,
                "description": f"设置字段类型: {field_type}",
                "params": {"text": field_type},
            })
            step_num += 1

        # Save the table
        steps.append({
            "step": step_num,
            "type": StepType.HOTKEY,
            "description": "保存表",
            "params": {"keys": ["ctrl", "s"]},
        })
        step_num += 1

        steps.append({
            "step": step_num,
            "type": StepType.WAIT,
            "description": "等待保存对话框",
            "params": {"seconds": 0.5},
        })
        step_num += 1

        steps.append({
            "step": step_num,
            "type": StepType.TYPE,
            "description": f"输入表名: {table_name}",
            "params": {"text": table_name, "submit": True},
        })

        return steps

    def _steps_import_data(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Steps to import data into Access."""
        file_path = params.get("file_path", "")
        table_name = params.get("table_name", "ImportedData")

        return [
            {
                "step": 1,
                "type": StepType.FOCUS_WINDOW,
                "description": "激活 Access 窗口",
                "params": {"window_title": "Microsoft Access"},
            },
            {
                "step": 2,
                "type": StepType.HOTKEY,
                "description": "打开外部数据导入向导",
                "params": {"keys": ["alt", "x", "i"]},
            },
            {
                "step": 3,
                "type": StepType.WAIT,
                "description": "等待导入对话框",
                "params": {"seconds": 1.0},
            },
            {
                "step": 4,
                "type": StepType.SCREENSHOT,
                "description": "截图确认导入对话框",
                "params": {},
            },
        ]

    def _steps_query_data(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Steps to query data in Access."""
        table_name = params.get("table_name", "")

        return [
            {
                "step": 1,
                "type": StepType.FOCUS_WINDOW,
                "description": "激活 Access 窗口",
                "params": {"window_title": "Microsoft Access"},
            },
            {
                "step": 2,
                "type": StepType.HOTKEY,
                "description": "创建查询（设计视图）",
                "params": {"keys": ["alt", "n", "q", "d"]},
            },
            {
                "step": 3,
                "type": StepType.WAIT,
                "description": "等待查询设计视图",
                "params": {"seconds": 1.0},
            },
            {
                "step": 4,
                "type": StepType.SCREENSHOT,
                "description": "截图确认查询设计视图",
                "params": {},
            },
        ]

    def _steps_create_form(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Steps to create a form in Access."""
        form_name = params.get("form_name", "NewForm")
        table_name = params.get("table_name", "")

        return [
            {
                "step": 1,
                "type": StepType.FOCUS_WINDOW,
                "description": "激活 Access 窗口",
                "params": {"window_title": "Microsoft Access"},
            },
            {
                "step": 2,
                "type": StepType.HOTKEY,
                "description": "创建新窗体",
                "params": {"keys": ["alt", "n", "f"]},
            },
            {
                "step": 3,
                "type": StepType.WAIT,
                "description": "等待窗体设计视图",
                "params": {"seconds": 1.0},
            },
            {
                "step": 4,
                "type": StepType.SCREENSHOT,
                "description": "截图确认窗体设计视图",
                "params": {},
            },
        ]

    def _steps_create_report(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Steps to create a report in Access."""
        report_name = params.get("report_name", "NewReport")

        return [
            {
                "step": 1,
                "type": StepType.FOCUS_WINDOW,
                "description": "激活 Access 窗口",
                "params": {"window_title": "Microsoft Access"},
            },
            {
                "step": 2,
                "type": StepType.HOTKEY,
                "description": "创建新报表",
                "params": {"keys": ["alt", "n", "r"]},
            },
            {
                "step": 3,
                "type": StepType.WAIT,
                "description": "等待报表设计视图",
                "params": {"seconds": 1.0},
            },
            {
                "step": 4,
                "type": StepType.SCREENSHOT,
                "description": "截图确认报表设计视图",
                "params": {},
            },
        ]

    def _steps_open_database(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Steps to open a database."""
        file_path = params.get("file_path", "")

        return [
            {
                "step": 1,
                "type": StepType.FOCUS_WINDOW,
                "description": "激活 Access 窗口",
                "params": {"window_title": "Microsoft Access"},
            },
            {
                "step": 2,
                "type": StepType.HOTKEY,
                "description": "打开文件",
                "params": {"keys": ["ctrl", "o"]},
            },
            {
                "step": 3,
                "type": StepType.WAIT,
                "description": "等待打开文件对话框",
                "params": {"seconds": 0.5},
            },
            {
                "step": 4,
                "type": StepType.TYPE,
                "description": f"输入文件路径: {file_path}",
                "params": {"text": file_path, "submit": True},
            },
        ]

    def to_operation_steps(self, parsed: ParsedInstruction) -> List[OperationStep]:
        """Convert parsed instruction steps to OperationStep objects."""
        operation_steps = []

        for i, step_data in enumerate(parsed.steps):
            try:
                step_type_str = step_data.get("type", "wait")
                try:
                    step_type = StepType(step_type_str)
                except ValueError:
                    step_type = StepType.WAIT

                op_step = OperationStep(
                    step=step_data.get("step", i + 1),
                    type=step_type,
                    description=step_data.get("description", ""),
                    params=step_data.get("params", {}),
                )
                operation_steps.append(op_step)
            except Exception as e:
                logger.warning(f"Failed to convert step {i}: {e}")

        return operation_steps
