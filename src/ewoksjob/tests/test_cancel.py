import sys
import pathlib

import pytest

from ..client import celery
from ..client import local
from ..client.futures import TimeoutError
from ..client.futures import CancelledError

from .utils import wait_not_finished


def test_normal(ewoks_worker, slurm_tmp_path):
    _assert_normal(celery, slurm_tmp_path)


def test_normal_local(local_ewoks_worker, slurm_tmp_path):
    _assert_normal(local, slurm_tmp_path)


def _assert_normal(mod, slurm_tmp_path):
    filename = slurm_tmp_path / "finished.smf"
    future = mod.submit_test(seconds=5, filename=str(filename))
    wait_not_finished(mod, {future.uuid}, timeout=3)

    # Do not use future.result() so we test geting the result from the uuid.
    results = mod.get_result(future.uuid, timeout=30)

    assert results == {"return_value": True}
    _nfs_cache_refresh(filename)
    assert filename.exists()
    wait_not_finished(mod, set(), timeout=3)


def test_cancel(ewoks_worker, slurm_tmp_path):
    can_be_cancelled = sys.platform != "win32"
    # Cancelling a Celery job on Windows does not work.
    # https://docs.celeryq.dev/en/stable/faq.html#does-celery-support-windows
    _assert_cancel(celery, slurm_tmp_path, can_be_cancelled)


def test_cancel_local(local_ewoks_worker, slurm_tmp_path):
    can_be_cancelled = local.get_active_pool().pool_type == "slurm"
    _assert_cancel(local, slurm_tmp_path, can_be_cancelled)


def _assert_cancel(mod, slurm_tmp_path, can_be_cancelled):
    filename = slurm_tmp_path / "finished.smf"
    future = mod.submit_test(seconds=12, filename=str(filename))
    wait_not_finished(mod, {future.uuid}, timeout=3)

    if can_be_cancelled:
        _ = mod.cancel(future.uuid)

        # Check whether the job is cancelled.
        with pytest.raises(CancelledError):
            # Do not use future.result() so we test geting the result from the uuid.
            _ = mod.get_result(future.uuid, timeout=30)

        _nfs_cache_refresh(filename)
        assert not filename.exists()
    else:
        _ = mod.cancel(future.uuid)

        # Check that the job cannot be cancelled.
        with pytest.raises(TimeoutError):
            # Do not use future.result() so we test geting the result from the uuid.
            _ = mod.get_result(future.uuid, timeout=3)

        _ = future.result(timeout=30)
        _nfs_cache_refresh(filename)
        assert filename.exists()


def _nfs_cache_refresh(filename: pathlib.Path):
    dirname = filename.parent
    for entry in dirname.iterdir():
        _ = entry.stat()  # Triggers a fresh stat call
