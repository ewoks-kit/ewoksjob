from ..client import celery
from ..client import local
from .utils import get_result


def test_submit(ewoks_worker):
    assert_submit(celery)
    assert_submit(celery, "ewokscore")
    assert_submit(celery)


def test_submit_local(local_ewoks_worker):
    assert_submit(local)
    assert_submit(local, "ewokscore")
    assert_submit(local)


def assert_submit(mod, *modules):
    if modules:
        future1 = mod.discover_tasks_from_modules(args=modules)
    else:
        future1 = mod.discover_all_tasks()
    future2 = mod.get_future(future1.task_id)
    results = get_result(future1, timeout=10)
    assert results
    results = get_result(future2, timeout=0)
    assert results
