Usage with Bliss at the ESRF
============================

Assume you have a project called `ewoksxrpd` which implements some tasks for data processing.

Worker environment
------------------

Create a conda environment for the worker, in this example called `xrpdworker`

.. code:: bash

    conda create --prefix /users/blissadm/conda/miniconda/envs/xrpdworker python=3.7

Activate the environment

.. code:: bash

    . blissenv -e xrpdworker

Basic worker dependencies

.. code:: bash

    python -m pip install ewoksjob[worker,redis,monitor]

Install the project that implements the actual worker tasks (`ewoksxrpd` in this example)

.. code:: bash

    python -m pip install ewoksxrpd

Install `hdf5plugin` if you need to read lima data

.. code:: bash

    conda install hdf5plugin

Install `ewoksorange` if you need a Qt GUI to create workflows

.. code:: bash

    python -m pip install ewoksorange[orange]

Client environment
------------------

Activate the Bliss environment

.. code:: bash

    . blissenv -d

Install the client dependencies

.. code:: bash

    conda install celery
    python -m pip install ewoksjob

Supervisor
----------

In this example we register a job monitor and only one worker

.. code::

    [group:ewoks]
    programs=xrpdworker, xrpdmonitor
    priority=900

    [program:xrpdworker]
    command=bash -c "source /users/blissadm/bin/blissenv -e xrpdworker && exec celery -A ewoksjob.apps.ewoks worker"
    directory=/users/opid31/ewoks/
    user=opid31
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

    [program:xrpdmonitor]
    command=bash -c "source /users/blissadm/bin/blissenv -e xrpdworker && exec celery flower"
    directory=/users/opid31/ewoks/
    user=opid31
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

The celery configuration must be in a file called `celeryconfig.py` in the working directory, for example

.. code:: python

    # /users/opid31/ewoks/celeryconfig.py

    broker_url = "redis://hostname:25001/2"
    result_backend = "redis://hostname:25001/3"

    result_serializer = "pickle"
    accept_content = ["application/json", "application/x-python-serialize"]


Note that `hostname` must be the host where the Redis database is running.
