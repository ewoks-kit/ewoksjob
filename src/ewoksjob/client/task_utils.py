import re
from copy import deepcopy
from typing import Literal
from typing import Optional

from ewoksutils.task_utils import task_inputs

from .celery import submit as _submit_celery
from .celery.futures import CeleryFuture
from .futures import FutureInterface
from .local import pool as _local_pool
from .local import submit as _submit_local
from .local.futures import LocalFuture
from .local.pool import _LocalPool

_QUALNAME_RE = re.compile(r"^[A-Za-z_]\w*(\.[A-Za-z_]\w*)*$")


def _guess_task_type(task_identifier: str):
    parts = task_identifier.rsplit("::", 1)
    if len(parts) == 2 and _QUALNAME_RE.match(parts[1]):
        return "method"

    if _QUALNAME_RE.match(task_identifier):
        name = task_identifier.split(".")[-1]
        if name == "run":
            return "ppfmethod"
        elif name[0].isupper():
            return "class"
        else:
            return "method"

    if task_identifier.endswith(".ipynb"):
        return "notebook"
    else:
        return "script"


class _MethodCeleryFuture(CeleryFuture):
    """Celery future that unwraps method task result"""

    def result(self, timeout: Optional[float] = None, interval: Optional[float] = None):
        task_result = super().result(timeout, interval)
        return task_result["return_value"]


class _MethodLocalFuture(LocalFuture):
    """Local future that unwraps method task result"""

    def result(self, timeout: Optional[float] = None):
        task_result = super().result(timeout)
        return task_result["return_value"]


class TaskSubmitter:
    def __init__(
        self,
        task_identifier: str,
        task_type: Optional[str] = None,
        execution_mode: Literal["celery", "process", "thread", "slurm"] = "celery",
        **submit_options,
    ):
        self._task_identifier = task_identifier
        if task_type is None:
            task_type = _guess_task_type(task_identifier)
        self._task_type = task_type
        self._execution_mode = execution_mode
        self._submit_options = deepcopy(submit_options)

        if self._execution_mode == "celery":
            self._local_executor = None
        else:
            self._local_executor = _LocalPool(
                pool_type=execution_mode, **self._submit_options
            )

    @property
    def task_identifier(self) -> str:
        return self._task_identifier

    @property
    def task_type(self) -> str:
        return self._task_type

    def __call__(self, *args, **kwargs) -> FutureInterface:
        graph = {
            "graph": {"id": self._task_identifier},
            "nodes": [
                {
                    "id": self._task_identifier,
                    "task_type": self._task_type,
                    "task_identifier": self._task_identifier,
                },
            ],
            "links": [],
        }

        inputs = task_inputs(
            task_identifier=self._task_identifier,
            inputs={
                # Positional arguments
                **{index: arg for index, arg in enumerate(args)},
                **kwargs,
            },
        )

        kwargs = {
            "inputs": inputs,
            "outputs": [{"all": True}],
            "merge_outputs": True,
        }

        if self._execution_mode == "celery":
            future = _submit_celery(
                args=(graph,), kwargs=kwargs, **self._submit_options
            )
            if self._task_type == "method":
                return _MethodCeleryFuture(future.uuid)
            else:
                return future
        else:
            with _local_pool.active_pool_context(self._local_executor):
                future = _submit_local(args=(graph,), kwargs=kwargs)
                if self._task_type == "method":
                    return _MethodLocalFuture(future.uuid)
                else:
                    return future
