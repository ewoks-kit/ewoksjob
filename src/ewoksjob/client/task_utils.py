import re
from copy import deepcopy
from typing import Any
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
        environment: Optional[dict] = None,
        save_options: Optional[dict] = None,
        **submit_options,
    ):
        self._task_identifier = task_identifier
        if task_type is None:
            task_type = _guess_task_type(task_identifier)
        self._task_type = task_type
        self._execution_mode = execution_mode
        self._environment = deepcopy(environment) if environment else None
        self._save_options = deepcopy(save_options) if save_options else None
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
        return self.submit(args, kwargs)

    def submit(
        self,
        args,
        kwargs,
        convert_destination: Optional[Any] = None,
        upload_parameters: Optional[dict] = None,
    ) -> FutureInterface:
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
        if convert_destination:
            kwargs["convert_destination"] = convert_destination
        if upload_parameters:
            kwargs["upload_parameters"] = upload_parameters
        if self._environment:
            kwargs["environment"] = self._environment
        if self._save_options:
            kwargs["save_options"] = self._save_options

        if self._execution_mode == "celery":
            future = _submit_celery(
                args=(graph,), kwargs=kwargs, **self._submit_options
            )
            if self._task_type == "method":
                return _MethodCeleryFuture(future.uuid)
            else:
                return future
        else:
            try:
                _local_pool._EWOKS_WORKER_POOL = self._local_executor
                future = _submit_local(args=(graph,), kwargs=kwargs)
                if self._task_type == "method":
                    return _MethodLocalFuture(future.uuid)
                else:
                    return future
            finally:
                _local_pool._EWOKS_WORKER_POOL = None
