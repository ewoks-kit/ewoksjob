"""SLURM execution pool."""
from functools import wraps
import logging
import traceback
from contextlib import contextmanager
from typing import Callable, Optional
import weakref
from celery.concurrency import thread

try:
    from pyslurmutils.futures import SlurmExecutor
    from pyslurmutils.client.errors import SlurmError
except ImportError:
    SlurmExecutor = None

__all__ = ("TaskPool",)

logger = logging.getLogger(__name__)

_SLURM_EXECUTOR = None


def get_submit_function() -> Optional[Callable]:
    """All SlurmError exceptions are converted to RuntimeError
    so that the client does not need pyslurmutils.
    """
    try:
        func = _SLURM_EXECUTOR.submit
    except (AttributeError, ReferenceError):
        return None
    return _replace_slurm_error(func)


class TaskPool(thread.TaskPool):
    """SLURM Task Pool."""

    executor_options = dict()

    def __init__(self, *args, **kwargs):
        if SlurmExecutor is None:
            raise RuntimeError("requires pyslurmutils")
        super().__init__(*args, **kwargs)
        self._create_slurm_executor()

    def restart(self):
        self.slurm_executor.shutdown()
        self.slurm_executor = None
        self._create_slurm_executor()

    def _create_slurm_executor(self):
        global _SLURM_EXECUTOR
        self.slurm_executor = SlurmExecutor(
            max_workers=self.limit, **self.executor_options
        )
        _SLURM_EXECUTOR = weakref.proxy(self.slurm_executor)

    def on_stop(self):
        self.slurm_executor.shutdown()
        super().on_stop()

    def terminate_job(self, pid, signal=None):
        raise NotImplementedError("SLURM job termination not implemented yet")


@contextmanager
def _replace_slurm_error_ctx():
    try:
        yield
    except SlurmError as e:
        tb = traceback.format_exc()
        cause = RuntimeError('\n"""\n%s"""' % tb)
        raise RuntimeError(str(e)) from cause


def _replace_slurm_error(method):
    @wraps(method)
    def wrapper(*args, **kwargs):
        with _replace_slurm_error_ctx():
            return method(*args, **kwargs)

    return wrapper
