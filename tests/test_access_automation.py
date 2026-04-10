"""
Tests for Access Automation
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.access_automation import AccessAutomation
from app.models.operation import OperationStep, StepType, ExecutionResult


@pytest.fixture
def automation():
    return AccessAutomation()


@pytest.mark.asyncio
async def test_execute_empty_steps(automation):
    """Test executing an empty list of steps."""
    result = await automation.execute_steps([])
    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.total_steps == 0
    assert result.completed_steps == 0


@pytest.mark.asyncio
async def test_execute_steps_dry_run(automation):
    """Test executing steps in dry run mode."""
    steps = [
        OperationStep(
            step=1,
            type=StepType.WAIT,
            description="等待",
            params={"seconds": 0.01},
        ),
        OperationStep(
            step=2,
            type=StepType.SCREENSHOT,
            description="截图",
            params={},
        ),
    ]

    result = await automation.execute_steps(steps, dry_run=True)
    assert isinstance(result, ExecutionResult)
    assert result.success is True
    assert result.total_steps == 2
    assert result.completed_steps == 2


@pytest.mark.asyncio
async def test_execute_simulated_steps(automation):
    """Test executing simulated steps on non-Windows."""
    steps = [
        OperationStep(step=1, type=StepType.CLICK, description="点击", params={"x": 100, "y": 200}),
        OperationStep(step=2, type=StepType.TYPE, description="输入", params={"text": "hello"}),
        OperationStep(step=3, type=StepType.HOTKEY, description="快捷键", params={"keys": ["ctrl", "s"]}),
    ]

    # Should always succeed in dry_run mode regardless of platform
    result = await automation.execute_steps(steps, dry_run=True)
    assert result.success is True
    assert result.completed_steps == 3


def test_is_access_running_non_windows(automation):
    """Test is_access_running on non-Windows returns False."""
    import platform
    if platform.system() != "Windows":
        assert automation.is_access_running() is False


def test_find_access_window_non_windows(automation):
    """Test find_access_window on non-Windows returns None."""
    import platform
    if platform.system() != "Windows":
        assert automation.find_access_window() is None


def test_set_progress_callback(automation):
    """Test setting progress callback."""
    progress_data = []

    def callback(data):
        progress_data.append(data)

    automation.set_progress_callback(callback)
    assert automation._progress_callback == callback


@pytest.mark.asyncio
async def test_step_results_included_in_execution_result(automation):
    """Test that step results are included in execution result."""
    steps = [
        OperationStep(step=1, type=StepType.WAIT, description="等待", params={"seconds": 0.01}),
        OperationStep(step=2, type=StepType.WAIT, description="等待", params={"seconds": 0.01}),
    ]

    result = await automation.execute_steps(steps, dry_run=True)
    assert len(result.step_results) == 2
    assert result.step_results[0]["step"] == 1
    assert result.step_results[1]["step"] == 2
