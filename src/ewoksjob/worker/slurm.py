"""SLURM execution pool."""

import weakref
import logging
from functools import wraps
from typing import Callable, Optional

from celery.concurrency.gevent import TaskPool as _TaskPool

try:
    from pyslurmutils.client import SlurmPythonJobRestClient
except ImportError:
    SlurmPythonJobRestClient = None

__all__ = ("TaskPool",)

logger = logging.getLogger(__name__)


_SLURM_CLIENT = None


def get_executor() -> Optional[Callable]:
    try:
        spawn = _SLURM_CLIENT.spawn
    except (AttributeError, ReferenceError):
        # TaskPool is not instantiated
        return None
    return _slurm_execute(spawn)


class TaskPool(_TaskPool):
    """SLURM Task Pool."""

    EXECUTOR_OPTIONS = dict()

    def __init__(self, *args, **kwargs):
        if SlurmPythonJobRestClient is None:
            raise RuntimeError("requires pyslurmutils")
        super().__init__(*args, **kwargs)
        self._create_slurm_client()

    def restart(self):
        self._slurm_client.cleanup()
        self._slurm_client = None
        self._create_slurm_client()

    def _create_slurm_client(self):
        global _SLURM_CLIENT
        self._slurm_client = SlurmPythonJobRestClient(
            max_workers=self.limit, **self.EXECUTOR_OPTIONS
        )
        _SLURM_CLIENT = weakref.proxy(self._slurm_client)

    def on_stop(self):
        self._slurm_client.cleanup()
        self._slurm_client = None
        super().on_stop()

    def terminate_job(self, pid, signal=None):
        print("TODO: support job cancelling for the slurm pool")


def _slurm_execute(spawn: Callable) -> Callable:
    @wraps(spawn)
    def executor(celery_task, *args, **kwargs):
        from ..apps import ewoks

        ewoks_task = ewoks.get_ewoks_task_from_celery_task(celery_task)
        if ewoks.celery_task_is_bound(celery_task):
            args = args[1:]  # remove `self`

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
