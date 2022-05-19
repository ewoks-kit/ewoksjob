Routing
=======

Workers can have different capabilities. You can have workers
with specific hardware

.. code:: bash

    celery -A ewoksjob.apps.ewoks worker -Q cpuworker
    celery -A ewoksjob.apps.ewoks worker -Q gpuworker --pool=solo
    celery -A ewoksjob.apps.ewoks worker -Q slurmworker --pool=slurm

Or you can have workers with different environments

.. code:: bash

    conda activate xrf; celery -A ewoksjob.apps.ewoks worker -Q xrf
    conda activate xrpd; celery -A ewoksjob.apps.ewoks worker -Q xrpd

The client can then select a specific worker

.. code:: python

    submit(..., queue="xrf")

If you don't have workers without a queue

.. code:: bash

    celery -A ewoksjob.apps.ewoks worker

you can add a default queue to the celery configuration

.. code:: python

    task_default_queue = 'cpuworker'
