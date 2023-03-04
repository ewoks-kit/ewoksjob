from ..client import celery
from ..client import local
from .utils import get_result


def test_submit(ewoks_worker):
    assert_submit(celery)


def test_submit_local(local_ewoks_worker):
    assert_submit(local)


def assert_submit(mod):
    future1 = mod.discover_tasks_from_modules(args=("ewokscore",))
    future2 = mod.get_future(future1.task_id)
    results = get_result(future1, timeout=10)
    assert results
    results = get_result(future2, timeout=0)
    assert results
