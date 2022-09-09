"""SLURM execution pool."""
import logging
from typing import Callable, Optional
import weakref
from celery.concurrency import thread

try:
    from pyslurmutils.futures import SlurmExecutor
except ImportError:
    SlurmExecutor = None


__all__ = ("TaskPool",)

logger = logging.getLogger(__name__)


_SLURM_EXECUTOR = None


def get_submit_function() -> Optional[Callable]:
    try:
        return _SLURM_EXECUTOR.submit
    except (AttributeError, ReferenceError):
        pass


class TaskPool(thread.TaskPool):
    """SLURM Task Pool."""

    slurm_executor_options = dict()

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
            max_workers=self.limit, **self.slurm_executor_options
        )
        _SLURM_EXECUTOR = weakref.proxy(self.slurm_executor)

    def on_stop(self):
        self.slurm_executor.shutdown()
        super().on_stop()

    def terminate_job(self, pid, signal=None):
        raise NotImplementedError("SLURM job termination not implemented yet")
