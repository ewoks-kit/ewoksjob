"""Pool that redirects tasks to a Slurm cluster."""

import weakref
import logging
from functools import wraps
from typing import Callable

from celery.concurrency.gevent import TaskPool as _TaskPool

try:
    from pyslurmutils.client import SlurmPythonJobRestClient
except ImportError:
    SlurmPythonJobRestClient = None

from .executor import set_executor_getter, ExecutorType


__all__ = ("TaskPool",)

logger = logging.getLogger(__name__)


class TaskPool(_TaskPool):
    """SLURM Task Pool."""

    EXECUTOR_OPTIONS = dict()

    def __init__(self, *args, **kwargs):
        if SlurmPythonJobRestClient is None:
            raise RuntimeError("requires pyslurmutils")
        super().__init__(*args, **kwargs)
        self._create_slurm_client()

    def restart(self):
        self._remove_slurm_client()
        self._create_slurm_client()

    def on_stop(self):
        self._remove_slurm_client()
        super().on_stop()

    def terminate_job(self, pid, signal=None):
        print("TODO: support job cancelling for the slurm pool")

    def _create_slurm_client(self):
        self._slurm_client = SlurmPythonJobRestClient(
            max_workers=self.limit, **self.EXECUTOR_OPTIONS
        )
        _set_slurm_client(self._slurm_client)

    def _remove_slurm_client(self):
        self._slurm_client.cleanup()
        self._slurm_client = None


_SLURM_CLIENT = None


def _set_slurm_client(slurm_client):
    global _SLURM_CLIENT
    _SLURM_CLIENT = weakref.proxy(slurm_client)
    set_executor_getter(_get_executor)


def _get_executor() -> ExecutorType:
    try:
        spawn = _SLURM_CLIENT.spawn
    except (AttributeError, ReferenceError):
        # TaskPool is not instantiated
        return
    return _slurm_execute(spawn)


def _slurm_execute(spawn: Callable) -> Callable:
    """Instead of executing the celery task, forward the ewoks task to Slurm."""

    @wraps(spawn)
    def executor(ewoks_task: Callable, *args, **kwargs):
        future = spawn(ewoks_task, args=args, kwargs=kwargs)
        try:
            return future.result()
        except BaseException:
            future.client.log_stdout_stderr(
                future.job_id, logger=logger, level=logging.ERROR
            )
            raise
        else:
            future.client.log_stdout_stderr(
                future.job_id, logger=logger, level=logging.INFO
            )
        finally:
            try:
                status = future.job_status()
                logger.info("Slurm job %s, %s", future.job_id, status)
                if future.job_status() not in ("COMPLETED", "CANCELLED", "FAILED"):
                    future.cancel_job()
            finally:
                future.cleanup_job()

    return executor
