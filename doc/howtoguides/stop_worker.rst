How to stop a Celery worker
===========================

An ``ewoksjob worker`` is a `Celery <https://docs.celeryq.dev/>`_ worker. A Celery *warm shutdown* stops
a worker from accepting new jobs, waits for its running jobs to finish and then exits. Jobs the worker
received but did not start yet are returned to the queue.

Use remote control commands
---------------------------

Remote control commands can be sent from any machine that has the worker configuration.
Stop accepting new jobs, wait until no job is running anymore and then shut down

.. code-block:: bash

    # Stop consuming jobs from the queue
    ewoksjob control cancel_consumer myqueue -d myworker@id00

    # List the running jobs (repeat until empty)
    ewoksjob inspect active -d myworker@id00

    # Warm shutdown of the worker
    ewoksjob control shutdown -d myworker@id00

When the worker is managed by a process manager like Supervisor, replace the last step by
stopping the worker through the process manager (see :ref:`stop-worker-supervisor`), otherwise the worker might be restarted.

To accept jobs again without restarting the worker

.. code-block:: bash

    # Start consuming jobs from the queue again
    ewoksjob control add_consumer myqueue -d myworker@id00

Send a signal
-------------

This section describes how a Celery worker reacts to signals.

The process tree of a running worker looks like this

.. code-block:: text

    wrapper process (optional)
    └── main worker process (ewoksjob worker)
        └── pool processes (--pool=prefork or --pool=process, execute the jobs)
            └── sub-processes started by jobs (optional)

All processes in this tree belong to the same *process group*, unless a sub-process explicitly
starts a new one (e.g. ``subprocess.Popen(..., start_new_session=True)``). The process group ID
is usually the PID of the top process in the tree (e.g. when started by Supervisor). Find it with

.. code-block:: bash

    ps -o pgid= -p <main-worker-pid>

A wrapper process is any process that starts the worker as a child process and stays alive.
A typical example is a bash script that starts the worker without ``exec``

.. code-block:: bash

    #!/bin/bash
    source /path/to/venv/bin/activate
    ewoksjob worker "$@"       # without exec: bash stays the parent of the worker

With ``exec ewoksjob worker "$@"`` the script is replaced by the worker and there is no wrapper process.

The effect of a signal on a Celery worker depends on which processes receive it

.. list-table::
    :header-rows: 1

    * - Signal
      - Sent to
      - Main worker process
      - Running jobs
      - Same signal a second time
    * - ``SIGINT``
      - main worker process
      - stops when the running jobs are finished
      - finish
      - stops immediately, running jobs are aborted
    * - ``SIGTERM``
      - main worker process
      - stops when the running jobs are finished
      - finish
      - no effect: warm shutdown continues
    * - ``SIGQUIT``
      - main worker process
      - stops immediately
      - aborted
      - no effect: no processes are left
    * - ``SIGKILL``
      - main worker process
      - killed immediately
      - aborted
      - no effect: no processes are left
    * - ``SIGINT``
      - process group
      - stops when the running jobs are finished
      - finish
      - stops immediately, running jobs are aborted
    * - ``SIGTERM``
      - process group
      - stops immediately
      - aborted
      - no effect: no processes are left
    * - ``SIGQUIT``
      - process group
      - stops immediately
      - aborted
      - no effect: no processes are left
    * - ``SIGKILL``
      - process group
      - killed immediately
      - aborted
      - no effect: no processes are left
    * - ``SIGINT``
      - wrapper process
      - keeps running
      - continue
      - no effect: the worker keeps running
    * - ``SIGTERM``
      - wrapper process
      - keeps running without parent
      - continue
      - no effect: the wrapper process no longer exists
    * - ``SIGQUIT``
      - wrapper process
      - keeps running
      - continue
      - no effect: the worker keeps running
    * - ``SIGKILL``
      - wrapper process
      - keeps running without parent
      - continue
      - no effect: the wrapper process no longer exists

So send ``SIGINT`` or ``SIGTERM`` to the main worker process, or ``SIGINT`` to the process group
when the worker is started by a wrapper process

.. code-block:: bash

    # Without wrapper process: signal the main worker process
    kill -INT <main-worker-pid>

    # With wrapper process: signal all processes in the process group (note the minus sign)
    kill -INT -- -<process-group-id>

.. note::

    Sub-processes started by a job (``subprocess``, ``multiprocessing`` with any start method, ...)
    inherit the ignored ``SIGINT`` from the pool processes. A sub-process that installs its own ``SIGINT``
    handler (e.g. ``signal.signal(signal.SIGINT, ...)``) does react to ``SIGINT`` sent to the process group
    and may abort the job.

.. _stop-worker-supervisor:

Supervisor
----------

Send ``SIGINT`` to the whole process group, so that it works with or without wrapper process, and give the
running jobs enough time to finish before all processes are killed with ``SIGKILL``

.. code-block:: ini

    [program:ewoksworker]
    command=ewoksjob worker -n myworker@%(host_node_name)s -Q myqueue
    stopsignal=INT
    stopasgroup=true
    killasgroup=true
    stopwaitsecs=43200
