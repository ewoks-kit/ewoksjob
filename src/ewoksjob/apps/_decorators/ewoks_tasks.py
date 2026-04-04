from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict

import ewoks
from ewokscore import task_discovery

from ...worker.executor import get_execute_method
from ..errors import replace_exception_for_client


def get_native_ewoks_task(task_name: str) -> Callable:
    return _TASK_MAPPING[task_name]


def celery_task_is_bound(task_name: str) -> bool:
    return task_name in _BOUND_TASKS


def ewoks_task(celery_task: Callable) -> Callable:
    """Wraps all celery tasks in order to

    * convert exception types that the client is not expected to have
    * execute with a worker specific executor (e.g. redirect the
      ewoks task to another job scheduler)
    """

    @wraps(celery_task)
    def new_celery_task(*args, **kwargs) -> Any:
        with replace_exception_for_client():
            execute = get_execute_method()

            if execute is None:
                return celery_task(*args, **kwargs)

            # Remove all references to ewoksjob
            ewoks_task = get_native_ewoks_task(celery_task.__name__)
            if celery_task_is_bound(celery_task.__name__):
                args = args[1:]  # remove `self`

            return execute(ewoks_task, *args, **kwargs)

    return new_celery_task


_TASK_MAPPING: Dict[Callable, Callable] = {
    "execute_graph": ewoks.execute_graph,
    "convert_graph": ewoks.convert_graph,
    "discover_tasks_from_modules": task_discovery.discover_tasks_from_modules,
    "discover_all_tasks": task_discovery.discover_all_tasks,
}

_BOUND_TASKS = {"execute_graph"}
# WARNING: all the task with @app.task(bind=True)
