"""Pool that redirects tasks to a Slurm cluster."""

import weakref
import logging
import datetime
from functools import wraps
from typing import Callable, Any, Optional

try:
    import gevent
    from gevent import GreenletExit
except ImportError:
    # Avoid error one import. Do cause error when actually trying to use this pool.
    gevent = NotImplemented
    GreenletExit = NotImplemented

from celery.concurrency.gevent import TaskPool as _TaskPool

try:
    from pyslurmutils.concurrent.futures import SlurmRestExecutor
    from pyslurmutils.concurrent.futures import SlurmRestFuture
except ImportError:
    SlurmRestExecutor = None
    SlurmRestFuture = Any

from .executor import set_execute_getter, ExecuteType


__all__ = ("TaskPool",)

logger = logging.getLogger(__name__)


class TaskPool(_TaskPool):
    """SLURM Task Pool."""

    EXECUTOR_OPTIONS = dict()

    def __init__(self, *args, **kwargs):
        if SlurmRestExecutor is None:
            raise RuntimeError("requires pyslurmutils")
        super().__init__(*args, **kwargs)
        self._create_slurm_executor()

    def restart(self):
        self._safe_remove_slurm_executor()
        self._create_slurm_executor()

    def on_stop(self):
        self._safe_remove_slurm_executor()
        super().on_stop()

    def _safe_remove_slurm_executor(self):
        if self._is_in_gevent_callback():
            g = gevent.spawn(self._remove_slurm_executor)
            g.join()
        else:
            self._remove_slurm_executor()

    def _is_in_gevent_callback(self):
        hub = gevent.get_hub()
        return gevent.getcurrent() is hub

    def _create_slurm_executor(self):
        maxtasksperchild = self.options["maxtasksperchild"]
        if maxtasksperchild is None:
            logger.warning(
                "The 'slurm' pool does not support Slurm jobs which execute an unlimited number of celery jobs. Use '--max-tasks-per-child=1' to remove this warning."
            )
            maxtasksperchild = 1
        kwargs = {
            "max_workers": self.limit,
            "max_tasks_per_worker": maxtasksperchild,
            **self.EXECUTOR_OPTIONS,
        }
        self._slurm_executor = SlurmRestExecutor(**kwargs)
        self._slurm_executor._celery_options = dict(self.options)
        _set_slurm_executor(self._slurm_executor)

    def _remove_slurm_executor(self):
        if self._slurm_executor is not None:
            self._slurm_executor.__exit__(None, None, None)
            self._slurm_executor = None


_SLURM_EXECUTOR = None


def _set_slurm_executor(slurm_executor):
    global _SLURM_EXECUTOR
    _SLURM_EXECUTOR = weakref.proxy(slurm_executor)
    set_execute_getter(_get_execute_method)


def _get_execute_method() -> ExecuteType:
    try:
        submit = _SLURM_EXECUTOR.submit
    except (AttributeError, ReferenceError):
        # TaskPool is not instantiated
        return
    timeout = _SLURM_EXECUTOR._celery_options["timeout"]
    soft_timeout = _SLURM_EXECUTOR._celery_options["soft_timeout"]
    return _slurm_execute_method(submit, timeout, soft_timeout)


_SubmitType = Callable[[Callable, Any, Any], SlurmRestFuture]


def _slurm_execute_method(
    submit: _SubmitType, timeout: Optional[float], soft_timeout: Optional[float]
) -> Callable[[_SubmitType], ExecuteType]:
    """Instead of executing the celery task, forward the ewoks task to Slurm."""

    if timeout is None and soft_timeout is None:
        time_limit_sec = None
    elif soft_timeout is None:
        time_limit_sec = timeout
    elif timeout is None:
        time_limit_sec = soft_timeout + 10
    else:
        time_limit_sec = timeout

    @wraps(submit)
    def execute(ewoks_task: Callable, *args, **kwargs):
        if time_limit_sec is not None:
            slurm_arguments = kwargs.setdefault("slurm_arguments", {})
            parameters = slurm_arguments.setdefault("parameters", {})
            time_limit = str(datetime.timedelta(seconds=round(time_limit_sec)))
            _ = parameters.setdefault("time_limit", time_limit)

        future = submit(ewoks_task, *args, **kwargs)
        try:
            return future.result()
        except GreenletExit:
            _ensure_cancel_job(future)
            raise

    return execute


def _ensure_cancel_job(future: SlurmRestFuture) -> None:
    not_cancelled = True
    while not_cancelled:
        try:
            logger.info("Cancel Slurm job %s", future.job_id)
            future.abort()
        except GreenletExit:
            continue
        not_cancelled = False
