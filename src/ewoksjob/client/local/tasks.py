import os
from functools import wraps
from typing import Callable, Mapping, Optional, Tuple
from concurrent.futures import Future

from .pool import get_active_pool
from ..test_workflow import test_workflow

try:
    from ... import tasks
except ImportError as e:
    tasks = None
    tasks_import_error = e


__all__ = [
    "execute_graph",
    "execute_test_graph",
    "convert_workflow",
    "discover_tasks_from_modules",
]


def _require_tasks(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        if tasks is None:
            raise ImportError(tasks_import_error)
        return method(*args, **kwargs)

    return wrapper


@_require_tasks
def execute_graph(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    return _submit_with_jobid(tasks.execute_graph, args=args, kwargs=kwargs)


def execute_test_graph(
    seconds=0, filename=None, kwargs: Optional[Mapping] = None
) -> Future:
    args = (test_workflow(),)
    if kwargs is None:
        kwargs = dict()
    kwargs["inputs"] = [
        {"id": "sleep", "name": 0, "value": seconds},
        {"id": "result", "name": "filename", "value": filename},
    ]
    return execute_graph(args=args, kwargs=kwargs)


@_require_tasks
def convert_workflow(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    return pool.submit(tasks.convert_graph, args=args, kwargs=kwargs)


@_require_tasks
def discover_tasks_from_modules(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    return pool.submit(tasks.discover_tasks_from_modules, args=args, kwargs=kwargs)


def _submit_with_jobid(
    func: Callable, args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    if kwargs is None:
        kwargs = dict()
    execinfo = kwargs.setdefault("execinfo", dict())
    if not execinfo.get("job_id"):
        job_id = os.environ.get("SLURM_JOB_ID", None)
        if job_id:
            execinfo["job_id"] = job_id
    task_id = pool.generate_task_id(execinfo.get("job_id"))
    execinfo["job_id"] = task_id
    return pool.submit(func, task_id=task_id, args=args, kwargs=kwargs)
