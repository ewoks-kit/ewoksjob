"""Celery ewoks application"""

from functools import wraps
from typing import Dict, List, Union, Callable

import celery
import ewoks
from ewokscore import task_discovery

from ..worker.options import add_options
from ..worker.task import worker_execute_wrapper

app = celery.Celery("ewoks")
add_options(app)


def _ensure_ewoks_job_id(method):
    """Use celery task ID as ewoks job ID when not ewoks job ID is provided"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        execinfo = kwargs.setdefault("execinfo", dict())
        if not execinfo.get("job_id"):
            execinfo["job_id"] = self.request.id
        return method(self, *args, **kwargs)

    return wrapper


@app.task(bind=True)
@_ensure_ewoks_job_id
@worker_execute_wrapper
def execute_graph(self, *args, **kwargs) -> Dict:
    return ewoks.execute_graph(*args, **kwargs)


@app.task()
@worker_execute_wrapper
def convert_graph(*args, **kwargs) -> Union[str, dict]:
    return ewoks.convert_graph(*args, **kwargs)


@app.task()
@worker_execute_wrapper
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return task_discovery.discover_tasks_from_modules(*args, **kwargs)


_TASK_MAPPING: Dict[Callable, Callable] = {
    "execute_graph": ewoks.execute_graph,
    "convert_graph": ewoks.convert_graph,
    "discover_tasks_from_modules": task_discovery.discover_tasks_from_modules,
}

_BOUND_TASKS = {"execute_graph"}


def get_ewoks_task_from_celery_task(celery_task: Callable) -> Callable:
    return _TASK_MAPPING[celery_task.__name__]


def celery_task_is_bound(celery_task: Callable) -> Callable:
    return celery_task.__name__ in _BOUND_TASKS
