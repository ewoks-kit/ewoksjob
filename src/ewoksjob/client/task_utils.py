from concurrent.futures import Future
from copy import deepcopy
from typing import Callable
from typing import Literal
from typing import Optional
from typing import Union
from uuid import uuid4

from ewoksutils.import_utils import qualname
from ewoksutils.task_utils import task_graph
from ewoksutils.task_utils import task_inputs

from . import celery
from .futures import FutureInterface

# ewoks is optional for celery execution; it is required for: synchronous, thread, process and slurm
try:
    import ewoks
except ImportError:
    ewoks = None
else:
    from . import local
    from .local.pool import _LocalPool
    from .local.pool import active_pool_context

    class _MethodLocalFuture(local.Future):
        """Local future that unwraps method task result"""

        def result(self, timeout: Optional[float] = None):
            task_result = super().result(timeout)
            return task_result["return_value"]


class _MethodCeleryFuture(celery.Future):
    """Celery future that unwraps method task result"""

    def result(self, timeout: Optional[float] = None, interval: Optional[float] = None):
        task_result = super().result(timeout, interval)
        return task_result["return_value"]


class TaskSubmitter:
    def __init__(
        self,
        task: Union[str, type, Callable],
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

        :param task: Task identifier, task class or function.
        :param task_type: Task type. When not provided, it is guessed from the task.
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
        if ewoks is None and execution_mode != "celery":
            raise RuntimeError(
                f"Please install the 'ewoks' package to use the '{execution_mode}' execution mode."
            )

        if isinstance(task, str):
            task_identifier = task
        else:
            task_identifier = qualname(task)
            if task_type is None:
                task_type = "class" if isinstance(task, type) else "method"
        self._graph = task_graph(task_identifier, task_type)
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
        return self._graph["nodes"][0]["task_identifier"]

    @property
    def task_type(self) -> str:
        return self._graph["nodes"][0]["task_type"]

    def shutdown(self, **kwargs):
        """Shutdown local executor, do nothing for remote and synchronous execution"""
        if self._local_executor is not None:
            self._local_executor.shutdown(**kwargs)

    def __call__(self, *args, **kwargs) -> FutureInterface:
        inputs = task_inputs(
            task_identifier=self.task_identifier,
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
            future = celery.submit(
                args=(self._graph,), kwargs=kwargs, **self._submit_options
            )
            if self.task_type == "method":
                return _MethodCeleryFuture(future.uuid)
            else:
                return future
        elif self._execution_mode == "synchronous":
            future = Future()
            try:
                result = ewoks.execute_graph(self._graph, **kwargs)
            except Exception as e:
                future.set_exception(e)
            else:
                future.set_result(result)
            if self.task_type == "method":
                return _MethodLocalFuture(str(uuid4()), future)
            else:
                return local.Future(str(uuid4()), future)
        else:
            with active_pool_context(self._local_executor):
                future = local.submit(args=(self._graph,), kwargs=kwargs)
                if self.task_type == "method":
                    return _MethodLocalFuture(future.uuid)
                else:
                    return future
