Submit one task
===============

Submit one task without a workflow file. Call the task like a function:

.. code-block:: python

    from ewoksjob.client.task_utils import TaskSubmitter

    submit_max = TaskSubmitter("builtins.max")
    future = submit_max(1, 5, 3)
    assert future.result() == 5

    submit_sum = TaskSubmitter("ewokscore.tests.examples.tasks.sumtask.SumTask")
    future = submit_sum(a=10, b=20)
    assert future.result() == {"result": 30}

The task can also be a task class or a function. The task type is guessed
from the task. Use ``task_type`` to set it.

Use ``execution_mode`` to select where the task executes:

- ``"celery"`` (default): in a worker
- ``"thread"``, ``"process"`` or ``"slurm"``: in a local executor (requires ``ewoks``)
- ``"synchronous"``: in the current thread, when called (requires ``ewoks``)

From the command line, use ``--task``:

.. code-block:: bash

    ewoksjob submit builtins.max --task -pa 0=1 -pa 1=5 -pa 2=3 --wait 10
