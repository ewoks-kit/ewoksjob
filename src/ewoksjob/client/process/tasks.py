from functools import wraps
from typing import Callable, Mapping, Optional, Tuple
from concurrent.futures import Future

from .pool import get_active_pool
from ..test_workflow import test_workflow

try:
    import ewoks
    from ewokscore import task_discovery
    from ... import tasks
except ImportError as e:
    ewoks = None
    ewoks_import_error = e


__all__ = [
    "trigger_workflow",
    "trigger_test_workflow",
    "convert_workflow",
    "convert_and_trigger_workflow",
    "convert_and_trigger_test_workflow",
    "trigger_and_upload_workflow",
    "discover_tasks_from_modules",
]


def _requires_ewoks(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        if ewoks is None:
            raise ImportError(ewoks_import_error)
        return method(*args, **kwargs)

    return wrapper


@_requires_ewoks
def trigger_workflow(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    return _submit_with_jobid(ewoks.execute_graph, args=args, kwargs=kwargs)


@_requires_ewoks
def convert_workflow(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    if kwargs is None:
        kwargs = dict()
    return pool.submit(ewoks.convert_graph, args=args, kwargs=kwargs)


@_requires_ewoks
def convert_and_trigger_workflow(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    return _submit_with_jobid(tasks.convert_and_execute_graph, args=args, kwargs=kwargs)


@_requires_ewoks
def trigger_and_upload_workflow(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    return _submit_with_jobid(tasks.execute_and_upload_graph, args=args, kwargs=kwargs)


def trigger_test_workflow(seconds=0, kwargs: Optional[Mapping] = None) -> Future:
    args = (test_workflow(),)
    if kwargs is None:
        kwargs = dict()
    kwargs["inputs"] = [{"id": "sleepnode", "name": 0, "value": seconds}]
    return trigger_workflow(
        args=args,
        kwargs=kwargs,
    )


def convert_and_trigger_test_workflow(
    seconds=0, args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    if len(args) != 1:
        raise TypeError(
            f"convert_and_trigger_test_workflow() requires 1 position arguments 'destination' but got {len(args)}"
        )
    args = (test_workflow(),) + args
    if kwargs is None:
        kwargs = dict()
    kwargs["inputs"] = [{"id": "sleepnode", "name": 0, "value": seconds}]
    return convert_and_trigger_workflow(args=args, kwargs=kwargs)


@_requires_ewoks
def discover_tasks_from_modules(
    args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    if kwargs is None:
        kwargs = dict()
    return pool.submit(_discover_tasks_from_modules, args=args, kwargs=kwargs)


def _discover_tasks_from_modules(*args, **kwargs):
    return list(task_discovery.discover_tasks_from_modules(*args, **kwargs))


def _submit_with_jobid(
    func: Callable, args: Optional[Tuple] = tuple(), kwargs: Optional[Mapping] = None
) -> Future:
    pool = get_active_pool()
    if kwargs is None:
        kwargs = dict()
    execinfo = kwargs.setdefault("execinfo", dict())
    task_id = pool.check_task_id(execinfo.get("job_id"))
    execinfo["job_id"] = task_id
    return pool.submit(func, task_id=task_id, args=args, kwargs=kwargs)
