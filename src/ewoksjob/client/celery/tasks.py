from celery.execute import send_task
from celery.result import AsyncResult
from ..test_workflow import test_workflow

__all__ = [
    "execute_graph",
    "execute_test_graph",
    "convert_workflow",
    "discover_tasks_from_modules",
]


def execute_graph(**kw) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.execute_graph", **kw)


def execute_test_graph(
    seconds=0, filename=None, args=None, kwargs=None, **kw
) -> AsyncResult:
    if args:
        raise TypeError("execute_test_graph does not take position arguments")
    args = (test_workflow(),)
    if kwargs is None:
        kwargs = dict()
    kwargs["inputs"] = [
        {"id": "sleep", "name": 0, "value": seconds},
        {"id": "result", "name": "filename", "value": filename},
    ]
    return execute_graph(args=args, kwargs=kwargs, **kw)


def convert_workflow(**kw) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.convert_graph", **kw)


def discover_tasks_from_modules(**kw) -> AsyncResult:
    return send_task("ewoksjob.apps.ewoks.discover_tasks_from_modules", **kw)
