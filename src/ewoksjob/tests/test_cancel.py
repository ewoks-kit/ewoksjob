import pytest
from ..client import celery
from ..client import local
from .utils import wait_not_finished


def test_normal(ewoks_worker):
    assert_normal(celery)


def test_normal_local(local_ewoks_worker):
    assert_normal(local)


def test_normal_local_slurm(local_slurm_ewoks_worker):
    assert_normal(local)


def test_cancel(ewoks_worker):
    assert_cancel(celery)


def test_cancel_local(local_ewoks_worker):
    assert_cancel(local)


def test_cancel_local_slurm(local_slurm_ewoks_worker):
    assert_cancel(local)


def assert_normal(mod):
    seconds = 1
    timeout = 3
    future = mod.submit_test(seconds)
    wait_not_finished(mod, {future.task_id}, timeout=timeout)
    results = mod.get_result(future.task_id, timeout=timeout)
    assert results == {"return_value": True}
    wait_not_finished(mod, set(), timeout=timeout)


def assert_cancel(mod):
    seconds = 10
    timeout = seconds * 2
    future = mod.submit_test(seconds)

    if mod is local:
        # The current implementation does not allow cancelling running tasks
        mod.cancel(future.task_id)
        try:
            results = mod.get_result(future.task_id, timeout=timeout)
        except mod.CancelledError:
            # cancelled before it started
            pass
        else:
            assert results == {"return_value": True}
            pytest.xfail("ran until completion")
    else:
        wait_not_finished(mod, {future.task_id}, timeout=timeout)
        mod.cancel(future.task_id)
        try:
            results = mod.get_result(future.task_id, timeout=timeout)
        except mod.CancelledError:
            pass
        else:
            assert results == {"return_value": True}
            pytest.xfail("ran until completion")

    wait_not_finished(mod, set(), timeout=timeout)
