Named queues
============

Workers can have different capabilities. You can have workers
with specific hardware

.. code-block:: bash

    ewoksjob worker -Q cpuworker
    ewoksjob worker -Q gpuworker --pool=solo
    ewoksjob worker -Q slurmworker --pool=slurm

Or you can have workers with different environments

.. code-block:: bash

    conda activate xrf; ewoksjob worker -Q xrf
    conda activate xrpd; ewoksjob worker -Q xrpd

The client can then select a specific worker

.. code-block:: python

    submit(..., queue="xrf")

If you don't have workers without a queue

.. code-block:: bash

    ewoksjob worker

you can add a default queue to the celery configuration

.. code-block:: python

    task_default_queue = 'cpuworker'

By default a worker is identified by the name `celery@<hostname>`.
When multiple workers run on the same host you need to provide
the name yourself to avoid name collision or `celery` will raise a warning. For example

.. code-block:: bash

    ewoksjob worker -Q worker1 -n worker1@mypcname
    ewoksjob worker -Q worker2 -n worker2@mypcname
