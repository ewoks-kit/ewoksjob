import pytest

from ..client.task_utils import TaskSubmitter

EXECUTION_MODES = "celery", "thread"  # , "process", "slurm"


@pytest.mark.parametrize("execution_mode", EXECUTION_MODES)
def test_function_submitter(execution_mode, ewoks_worker):
    submit_addfunc = TaskSubmitter(
        "ewokscore.tests.examples.tasks.addfunc.addfunc", execution_mode=execution_mode
    )
    assert submit_addfunc(arg=2).result(timeout=10) == 3


@pytest.mark.parametrize("execution_mode", EXECUTION_MODES)
def test_builtin_function_submitter(execution_mode, ewoks_worker):
    submit_max = TaskSubmitter("builtins.max", execution_mode=execution_mode)
    assert submit_max(1, 2, -1).result(timeout=10) == 2


@pytest.mark.parametrize("execution_mode", EXECUTION_MODES)
def test_task_submitter(execution_mode, ewoks_worker):
    submit_sum_task = TaskSubmitter(
        "ewokscore.tests.examples.tasks.sumtask.SumTask", execution_mode=execution_mode
    )
    assert submit_sum_task(a=1, b=2).result(timeout=10) == {"result": 3}


@pytest.mark.parametrize("execution_mode", EXECUTION_MODES)
def test_function_from_script_submitter(execution_mode, tmp_path, ewoks_worker):
    script_path = tmp_path / "test.py"
    script_path.write_text("def function(a, b): return a + b\n")

    submit_script_function = TaskSubmitter(
        f"{script_path}::function", execution_mode=execution_mode
    )
    assert submit_script_function(a=1, b=2).result(timeout=10) == 3


@pytest.mark.parametrize("execution_mode", EXECUTION_MODES)
def test_script_submitter(execution_mode, tmp_path, ewoks_worker):
    script_path = tmp_path / "test.py"
    script_path.write_text("import sys; sys.exit(2)")

    submit_script = TaskSubmitter(str(script_path), execution_mode=execution_mode)
    assert submit_script().result(timeout=10) == {
        "err": None,
        "out": None,
        "return_code": 2,
    }
