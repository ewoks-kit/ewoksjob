import os
import time
import logging
from types import ModuleType

logger = logging.getLogger(__name__)


def has_redis_server():
    with os.popen("redis-server --version") as output:
        return bool(output.read())


def get_result(future, **kwargs):
    if hasattr(future, "get"):
        return future.get(**kwargs)
    else:
        return future.result(**kwargs)


def wait_not_finished(mod: ModuleType, expected_task_ids: set, timeout=3):
    """Wait until all running task ID's are `expected_task_ids`"""
    if mod.__name__.endswith("celery") and not has_redis_server():
        time.sleep(0.1)
        logger.warning("memory and sqlite do not support task monitoring")
        return
    t0 = time.time()
    while True:
        task_ids = set(mod.get_not_finished_task_ids())
        if task_ids == expected_task_ids:
            return
        dt = time.time() - t0
        if dt > timeout:
            assert task_ids == expected_task_ids, task_ids
        time.sleep(0.2)
