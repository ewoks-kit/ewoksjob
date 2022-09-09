import pytest
from celery.exceptions import TimeoutError as CeleryTimeoutError
from concurrent.futures import TimeoutError as localTimeoutError
from ..client import celery
from ..client import local
from .utils import get_result


def test_task_discovery(ewoks_worker):
    future = celery.get_future("abc")
    assert future.status == "PENDING"
    with pytest.raises(CeleryTimeoutError):
        future.get(timeout=1e-8)


def test_task_discovery_local(local_ewoks_worker):
    future = local.get_future("abc")
    assert not future.running()
    with pytest.raises(localTimeoutError):
        get_result(future, timeout=0)


def test_task_discovery_local_slurm(local_slurm_ewoks_worker):
    future = local.get_future("abc")
    assert not future.running()
    with pytest.raises(localTimeoutError):
        get_result(future, timeout=0)
