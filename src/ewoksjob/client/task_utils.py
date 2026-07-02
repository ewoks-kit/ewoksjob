import re
from concurrent.futures import Future
from copy import deepcopy
from typing import Literal
from typing import Optional
from uuid import uuid4

import ewoks
from ewoksutils.task_utils import task_inputs

from . import celery
from . import local
from .futures import FutureInterface
from .local.pool import _LocalPool
from .local.pool import active_pool_context

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


class _MethodCeleryFuture(celery.Future):
    """Celery future that unwraps method task result"""

    def result(self, timeout: Optional[float] = None, interval: Optional[float] = None):
        task_result = super().result(timeout, interval)
        return task_result["return_value"]


class _MethodLocalFuture(local.Future):
    """Local future that unwraps method task result"""

    def result(self, timeout: Optional[float] = None):
        task_result = super().result(timeout)
        return task_result["return_value"]


class TaskSubmitter:
    def __init__(
        self,
        task_identifier: str,
        task_type: Optional[str] = None,
        execution_mode: Literal[
            "celery", "process", "thread", "slurm", "synchronous"
        ] = "celery",
        **submit_options,
    ):
        """Wrapper function that execute a task asynchronously when called.

        .. code-block:: python

           submit_max = TaskSubmitter("builtins.max", queue="celery")
           future = submit_max(1, 2, 3)  # submit asynchronous task execution
           maximum = future.result()  # wait for the result

        :param task_identifier: The full name of the task to submit
        :param task_type: The type of the task, if not provided it is guessed from the task_identifier.
        :param execution_mode:

            - "celery": Submit the task on a remote ewoks worker through celery
            - "thread": Execute the task in a thread
            - "process": Execute the task in a different process
            - "slurm": Execute the task in a session on a SLURM cluster
            - "synchronous": Execute the task synchronously when called

        :param submit_options: Extra arguments are passed to the choosen task queue/executor.
            Arguments depend on the `execution_mode`:

            - For "celery", see [celery documentation](https://docs.celeryq.dev/en/stable/reference/celery.app.task.html#celery.app.task.Task.apply_async)
            - For "slurm", see [pyslumrutils documentation(https://pyslurmutils.readthedocs.io/en/stable/reference/_generated/pyslurmutils.concurrent.rest.SlurmRestExecutor.html#pyslurmutils.concurrent.rest.SlurmRestExecutor)
        """
        self._task_identifier = task_identifier
        if task_type is None:
            task_type = _guess_task_type(task_identifier)
        self._task_type = task_type
        self._execution_mode = execution_mode
        self._submit_options = deepcopy(submit_options)

        if self._execution_mode in ("celery", "synchronous"):
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

    def shutdown(self, **kwargs):
        """Shutdown local executor, do nothing for remote and synchronous execution"""
        if self._local_executor is not None:
            self._local_executor.shutdown(**kwargs)

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
            future = celery.submit(args=(graph,), kwargs=kwargs, **self._submit_options)
            if self._task_type == "method":
                return _MethodCeleryFuture(future.uuid)
            else:
                return future
        elif self._execution_mode == "synchronous":
            future = Future()
            try:
                result = ewoks.execute_graph(graph, **kwargs)
            except Exception as e:
                future.set_exception(e)
            else:
                future.set_result(result)
            if self._task_type == "method":
                return _MethodLocalFuture(str(uuid4()), future)
            else:
                return local.Future(str(uuid4()), future)
        else:
            with active_pool_context(self._local_executor):
                future = local.submit(args=(graph,), kwargs=kwargs)
                if self._task_type == "method":
                    return _MethodLocalFuture(future.uuid)
                else:
                    return future
