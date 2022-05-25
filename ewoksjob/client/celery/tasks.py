from celery.execute import send_task
from celery.result import AsyncResult
from ..test_workflow import test_workflow

__all__ = [
    "trigger_workflow",
    "trigger_test_workflow",
    "convert_workflow",
    "convert_and_trigger_workflow",
    "convert_and_trigger_test_workflow",
    "discover_tasks_from_modules",
]


def trigger_workflow(**kwargs) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.execute_workflow", **kwargs)


def trigger_test_workflow(seconds=0, args=None, **kwargs) -> AsyncResult:
    if args:
        raise TypeError(
            f"trigger_test_workflow() got on unexpected position arguments {args}"
        )
    kwargs["args"] = (test_workflow(),)
    kw = kwargs.setdefault("kwargs", dict())
    kw["inputs"] = [{"id": "sleepnode", "name": 0, "value": seconds}]
    return trigger_workflow(**kwargs)


def convert_workflow(**kwargs) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.convert_workflow", **kwargs)


def convert_and_trigger_workflow(**kwargs) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.convert_and_execute_workflow", **kwargs)


def convert_and_trigger_test_workflow(seconds=0, args=None, **kwargs) -> AsyncResult:
    if len(args) != 1:
        raise TypeError(
            f"convert_and_trigger_test_workflow() requires 1 position arguments 'destination' but got {len(args)}"
        )
    kwargs["args"] = (test_workflow(),) + args
    kw = kwargs.setdefault("kwargs", dict())
    kw["inputs"] = [{"id": "sleepnode", "name": 0, "value": seconds}]
    return convert_and_trigger_workflow(**kwargs)


def discover_tasks_from_modules(**kwargs) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.discover_tasks_from_modules", **kwargs)
