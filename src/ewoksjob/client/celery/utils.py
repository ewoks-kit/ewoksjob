import warnings
import logging
from typing import Dict, List, Optional, Set, Any
from celery import current_app
from celery.result import AsyncResult

__all__ = [
    "get_future",
    "cancel",
    "get_result",
    "get_not_finished_task_ids",
    "get_not_finished_futures",
    "get_queues",
    "get_workers",
]


logger = logging.getLogger(__name__)


def get_future(task_id:str) -> AsyncResult:
    return AsyncResult(task_id)


def cancel(task_id:str) -> None:
    future = get_future(task_id)
    if future is not None:
        future.revoke(terminate=True)


def get_result(task_id:str, **kwargs) -> Any:
    kwargs.setdefault("interval", 0.1)
    future = AsyncResult(task_id)
    if future is not None:
        return future.get(**kwargs)


def get_not_finished_task_ids() -> List[str]:
    inspect = current_app.control.inspect()
    task_ids = list()

    workers = inspect.active()  # running
    if workers is None:
        logger.warning("No Celery workers were detected")
        workers = dict()
    for tasks in workers.values():
        for task in tasks:
            task_ids.append(task["id"])

    workers = inspect.scheduled()  # pending
    if workers is None:
        workers = dict()
    for tasks in workers.values():
        for task in tasks:
            task_ids.append(task["id"])

    return task_ids


def get_not_finished_futures() -> List[AsyncResult]:
    lst = [get_future(task_id) for task_id in get_not_finished_task_ids()]
    return [future for future in lst if future is not None]


def get_workers() -> List[str]:
    warnings.warn(
        "'get_workers' is deprecated in favor of 'get_queues'", DeprecationWarning
    )
    return get_queues()


def get_queues() -> List[str]:
    worker_info: Optional[Dict[str, List[dict]]] = (
        current_app.control.inspect().active_queues()
    )
    if worker_info is None:
        return list()

    queues: Set[str] = set()
    for queue_infos in worker_info.values():
        for queue_info in queue_infos:
            queues.add(queue_info["name"])

    return list(queues)
