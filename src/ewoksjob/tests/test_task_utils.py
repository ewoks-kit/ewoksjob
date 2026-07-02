import pytest

from ..client.task_utils import TaskSubmitter

TASK_TESTS = [
    ("ewokscore.tests.examples.tasks.addfunc.addfunc", (), {"arg": 2}, 3),
    ("builtins.max", (1, 2, -1), {}, 2),
    (
        "ewokscore.tests.examples.tasks.sumtask.SumTask",
        (),
        {"a": 1, "b": 2},
        {"result": 3},
    ),
]


@pytest.mark.parametrize("task,args,kwargs,result", TASK_TESTS)
def test_task_submitter_worker(ewoks_worker, task, args, kwargs, result):
    submitter = TaskSubmitter(task, execution_mode="celery")
    assert submitter(*args, **kwargs).result(timeout=10) == result


@pytest.mark.parametrize("task,args,kwargs,result", TASK_TESTS)
def test_task_submitter_thread(task, args, kwargs, result):
    submitter = TaskSubmitter(task, execution_mode="thread")
    assert submitter(*args, **kwargs).result(timeout=10) == result


@pytest.mark.parametrize("task,args,kwargs,result", TASK_TESTS)
def test_task_submitter_process(skip_if_gevent, task, args, kwargs, result):
    submitter = TaskSubmitter(task, execution_mode="process")
    assert submitter(*args, **kwargs).result(timeout=10) == result


def test_function_from_script_submitter_worker(ewoks_worker, tmp_path):
    script_path = tmp_path / "test.py"
    script_path.write_text("def function(a, b): return a + b\n")

    submit_script_function = TaskSubmitter(
        f"{script_path}::function", execution_mode="celery"
    )
    assert submit_script_function(a=1, b=2).result(timeout=10) == 3


def test_function_from_script_submitter_thread(tmp_path):
    script_path = tmp_path / "test.py"
    script_path.write_text("def function(a, b): return a + b\n")

    submit_script_function = TaskSubmitter(
        f"{script_path}::function", execution_mode="thread"
    )
    assert submit_script_function(a=1, b=2).result(timeout=10) == 3


def test_function_from_script_submitter_process(skip_if_gevent, tmp_path):
    script_path = tmp_path / "test.py"
    script_path.write_text("def function(a, b): return a + b\n")

    submit_script_function = TaskSubmitter(
        f"{script_path}::function", execution_mode="thread"
    )
    assert submit_script_function(a=1, b=2).result(timeout=10) == 3


def test_script_submitter_worker(ewoks_worker, tmp_path):
    script_path = tmp_path / "test.py"
    script_path.write_text("import sys; sys.exit(2)")

    submit_script = TaskSubmitter(str(script_path), execution_mode="celery")
    assert submit_script().result(timeout=10) == {
        "err": None,
        "out": None,
        "return_code": 2,
    }


def test_script_submitter_thread(tmp_path):
    script_path = tmp_path / "test.py"
    script_path.write_text("import sys; sys.exit(2)")

    submit_script = TaskSubmitter(str(script_path), execution_mode="thread")
    assert submit_script().result(timeout=10) == {
        "err": None,
        "out": None,
        "return_code": 2,
    }


def test_script_submitter_process(skip_if_gevent, tmp_path):
    script_path = tmp_path / "test.py"
    script_path.write_text("import sys; sys.exit(2)")

    submit_script = TaskSubmitter(str(script_path), execution_mode="process")
    assert submit_script().result(timeout=10) == {
        "err": None,
        "out": None,
        "return_code": 2,
    }
