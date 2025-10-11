Getting started
===============

Job scheduling involves several components

- Message broker: for submitting jobs (*Redis* or *RabbitMQ* or *Sqlite3*)
- Result backend: for storing job return values (*Redis* or *Sqlite3*)
- Client: submits jobs
- Worker: executes jobs
- Monitor: monitors job execution

Job schedulers
--------------

Currently these job schedulers are supported

`celery <https://docs.celeryq.dev>`_
++++++++++++++++++++++++++++++++++++

This is the default job scheduler used in production. *Redis* or *RabbitMQ* or *Sqlite3*
can be used for the Celery message broker. *Redis* or *Sqlite3* can be used for the Celery
result backend.

Workers can handle several jobs concurrently by using one of these pools

- `prefork` (default): sub-processes (child processes can be created with `billiard <https://billiard.readthedocs.io>`_)
- `process`: sub-processes (child processes can be created with python's builtin libraries)
- `solo`: no concurrency
- `threads`: system threads
- `gevent`: green threads
- `eventlet`: green threads
- `slurm`: foward jobs to a SLURM job scheduler with `pyslurmutils <https://pyslurmutils.readthedocs.io>`_

local
+++++

The client and the single worker are in the same process. Monitoring is not supported.

The single worker can handle several jobs concurrently by using one of these pools

- `process` (default): sub-processes
- `thread`: system threads
- `slurm`: foward jobs to a SLURM job scheduler with `pyslurmutils <https://pyslurmutils.readthedocs.io>`_

Start worker
------------

Start a worker that can execute *ewoks* graphs

.. code-block:: bash

    ewoksjob worker

Start monitor
-------------

Start a web server for monitoring jobs

.. code-block:: bash

    export FLOWER_UNAUTHENTICATED_API=true  # allows canceling jobs
    ewoksjob monitor

Submit workflow
---------------

Submit a workflow from python, possible from another machine

.. code-block:: python

    from ewoksjob.client import submit

    workflow = {"graph": {"id": "mygraph"}}
    future = submit(args=(workflow,))
    result = future.result(timeout=None)
