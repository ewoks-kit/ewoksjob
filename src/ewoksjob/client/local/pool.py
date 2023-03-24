import sys
from contextlib import contextmanager
from typing import Mapping, Optional, Tuple
from uuid import uuid4
import multiprocessing
import weakref
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import Future

try:
    from pyslurmutils.concurrent.futures import SlurmRestExecutor
    from pyslurmutils.client.job_io.file_io import Future as SlurmFuture
except ImportError:
    SlurmRestExecutor = None


__all__ = ["get_active_pool", "pool_context"]


_EWOKS_WORKER_POOL = None


def get_active_pool(raise_on_missing: Optional[bool] = True):
    if raise_on_missing and _EWOKS_WORKER_POOL is None:
        raise RuntimeError("No worker pool is available")
    return _EWOKS_WORKER_POOL


@contextmanager
def pool_context(*args, **kwargs):
    global _EWOKS_WORKER_POOL
    if _EWOKS_WORKER_POOL is None:
        with _LocalPool(*args, **kwargs) as pool_obj:
            _EWOKS_WORKER_POOL = pool_obj
            try:
                yield pool_obj
            finally:
                _EWOKS_WORKER_POOL = None
    else:
        yield _EWOKS_WORKER_POOL


class _LocalPool:
    def __init__(
        self,
        *args,
        pool_type: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs,
    ) -> None:
        if pool_type is None:
            pool_type = "process"
        if context is None:
            context = "spawn"
        if pool_type == "process":
            if context:
                if sys.version_info >= (3, 7):
                    kwargs["mp_context"] = multiprocessing.get_context(context)
                else:
                    multiprocessing.set_start_method(context, force=True)
            self._executor = ProcessPoolExecutor(*args, **kwargs)
        elif pool_type == "thread":
            self._executor = ThreadPoolExecutor(*args, **kwargs)
        elif pool_type == "slurm":
            if SlurmRestExecutor is None:
                raise RuntimeError("requires pyslurmutils")
            self._executor = SlurmRestExecutor(*args, **kwargs)
        else:
            raise ValueError(f"Unknown pool type '{pool_type}'")
        self._pool_type = pool_type
        self._tasks = weakref.WeakValueDictionary()

    def __enter__(self):
        self._executor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self._executor.__exit__(exc_type, exc_val, exc_tb)

    def shutdown(self, **kw):
        return self._executor.shutdown(**kw)

    @property
    def pool_type(self):
        return self._pool_type

    def submit(
        self,
        func,
        task_id=None,
        args: Optional[Tuple] = tuple(),
        kwargs: Optional[Mapping] = None,
    ) -> Future:
        """Like celery.send_task"""
        if kwargs is None:
            kwargs = dict()
        future = self._executor.submit(func, *args, **kwargs)
        self._patch_future(future, task_id)
        self._tasks[future.task_id] = future
        return future

    def generate_task_id(self, task_id=None):
        if self.pool_type == "slurm":
            return task_id
        if task_id is None:
            task_id = str(uuid4())
            while task_id in self._tasks:
                task_id = str(uuid4())
            return task_id
        if task_id in self._tasks:
            raise RuntimeError(f"Job '{task_id}' already exists")
        return task_id

    def get_future(self, task_id):
        future = self._tasks.get(task_id)
        if future is None:
            return self._get_dummy_future(task_id)
        return future

    def _get_dummy_future(self, task_id):
        if self.pool_type == "slurm":
            future = SlurmFuture(0, "", self._executor.client.io_handler)
        else:
            future = Future()
        self._patch_future(future, self.generate_task_id(task_id))
        return future

    def get_not_finished_task_ids(self) -> list:
        """Get all task ID's that are not finished"""
        return [task_id for task_id, future in self._tasks.items() if not future.done()]

    def _patch_future(self, future, task_id):
        if not task_id and self.pool_type == "slurm":
            future.task_id = str(future.job_id)
        else:
            future.task_id = task_id
        # Warning: this causes the future to never be garbage collected
        # future.get = future.result
