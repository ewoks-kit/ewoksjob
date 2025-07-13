import pytest

from ..client import celery
from ..client import local
from ..client.futures import TimeoutError


def test_future(ewoks_worker):
    future = celery.get_future("abc")
    assert not future.running()
    with pytest.raises(TimeoutError):
        _ = future.result(timeout=0)
    future._async_result.backend.remove_pending_result(future._async_result)


def test_future_local(local_ewoks_worker):
    future = local.get_future("abc")
    assert not future.running()
    with pytest.raises(TimeoutError):
        _ = future.result(timeout=0)
