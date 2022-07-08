Usage with Bliss at the ESRF
============================

Assume you have a project called `ewoksxrpd` which implements some tasks for data processing.

You need to create a worker environment, install *ewoksjob* in the bliss conda environment
and create a celery configuration file.

Worker environment
------------------

Decide first whether the code needs to be managed and edited by the beamline staff or BCU staff.
When the data processing code is not well established, most likely the beamline staff will manage it.

Managed by *blissadm*
^^^^^^^^^^^^^^^^^^^^^

Create a conda environment for the worker, in this example called `ewoksworker`

.. code:: bash

    conda create --prefix /users/blissadm/conda/miniconda/envs/ewoksworker python=3.7

Activate the environment

.. code:: bash

    . blissenv -e ewoksworker

Basic worker dependencies

.. code:: bash

    python3 -m pip install ewoksjob[worker,redis,monitor]

Install the project that implements the actual worker tasks (`ewoksxrpd` is just an example)

.. code:: bash

    python3 -m pip install ewoksxrpd

Supervisor
++++++++++

In this example we register a job monitor (you only ever need one) and one worker (you may need more than one)

.. code::

    [group:ewoks]
    programs=ewoksmonitor, ewoksworker
    priority=900

    [program:ewoksmonitor]
    command=bash -c "source /users/opid00/anaconda3/bin/activate ewoksworker &&& exec celery flower"
    directory=/users/opid00/ewoks/
    user=opid00
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

    [program:ewoksworker]
    command=bash -c "source /users/opid00/anaconda3/bin/activate ewoksworker &&& exec celery -A ewoksjob.apps.ewoks worker"
    directory=/users/opid00/ewoks/
    user=opid00
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

Managed by *opid00*
^^^^^^^^^^^^^^^^^^^

Create a conda environment for the worker, in this example called `ewoksworker`

.. code:: bash

    conda create --name ewoksworker python=3.7

Activate the environment

.. code:: bash

    conda activate ewoksworker

Basic worker dependencies

.. code:: bash

    python3 -m pip install ewoksjob[worker,redis,monitor]

Install the project that implements the actual worker tasks (`ewoksxrpd` is just an example)

.. code:: bash

    python3 -m pip install ewoksxrpd

Supervisor
++++++++++

In this example we register a job monitor (you only ever need one) and one worker (you may need more than one)

.. code::

    [group:ewoks]
    programs=ewoksmonitor, ewoksworker
    priority=900

    [program:ewoksmonitor]
    command=bash -c "source /users/opid00/anaconda3/bin/activate ewoksworker &&& exec celery flower"
    directory=/users/opid00/ewoks/
    user=opid00
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

    [program:ewoksworker]
    command=bash -c "source /users/opid00/anaconda3/bin/activate ewoksworker &&& exec celery -A ewoksjob.apps.ewoks worker"
    directory=/users/opid00/ewoks/
    user=opid00
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

Bliss environment
-----------------

Activate the Bliss environment

.. code:: bash

    . blissenv -d

Install the client dependencies

.. code:: bash

    conda install celery
    python3 -m pip install ewoksjob

Celery configuration
--------------------

The celery configuration must be in a file called `celeryconfig.py` in the working directory
as specified in the supervisor configuration. For example

.. code:: python

    # /users/opid00/ewoks/celeryconfig.py

    broker_url = "redis://hostname:25001/2"
    result_backend = "redis://hostname:25001/3"

    result_serializer = "pickle"
    accept_content = ["application/json", "application/x-python-serialize"]

    result_expires = 600

Note that `hostname` must be the host where the Redis database is running.

Test installation
-----------------

Run a test workflow in a Bliss session

.. code:: python

    DEMO_SESSION [1]: import os
    DEMO_SESSION [2]: from ewoksjob.client import submit_test
    DEMO_SESSION [3]: os.environ["CELERY_CONFIG_MODULE"]="/users/opid00/ewoks/celeryconfig.py"
    DEMO_SESSION [4]: submit_test().get()
             Out [4]: {'return_value': True}
