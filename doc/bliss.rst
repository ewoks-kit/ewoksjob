Usage with *BLISS* at the ESRF
==============================

Assume you have a project called `ewoksxrpd` which implements some tasks for data processing.

You need to create a worker python environment (conda or anything else), install *ewoksjob*
in the *BLISS* conda environment and configure ewoks in the beamline configuration (Beacon).

Worker environment
------------------

Decide first whether the code needs to be managed and edited by the beamline staff or BCU.
When the data processing code is well established and doesn't change often, most likely the
BCU will manage it.

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

    python3 -m pip install ewoksjob[worker,beacon,redis,monitor]

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
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000",CELERY_LOADER="ewoksjob.config.EwoksLoader"
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

    [program:ewoksworker]
    command=bash -c "source /users/opid00/anaconda3/bin/activate ewoksworker &&& exec celery -A ewoksjob.apps.ewoks worker"
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000",CELERY_LOADER="ewoksjob.config.EwoksLoader"
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

Make sure to replace `id00` with the proper string.

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
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000",CELERY_LOADER="ewoksjob.config.EwoksLoader"
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

    [program:ewoksworker]
    command=bash -c "source /users/opid00/anaconda3/bin/activate ewoksworker &&& exec celery -A ewoksjob.apps.ewoks worker"
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000",CELERY_LOADER="ewoksjob.config.EwoksLoader"
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

Make sure to replace `id00` with the proper string.

*BLISS* environment
-------------------

Activate the *BLISS* conda environment

.. code:: bash

    . blissenv -d

Install the client dependencies

.. code:: bash

    conda install celery
    python3 -m pip install ewoksjob

Ewoks configuration
-------------------

Ewoks must be configured in the beamline configuration (Beacon). For example

.. code:: yaml

    # /users/blissadm/local/beamline_configuration/ewoks/__init__.yml

    bliss_ignored: true

.. code:: yaml

    # /users/blissadm/local/beamline_configuration/ewoks/config.yml

    celery:
        broker_url: "redis://hostname:25001/2"
        result_backend: "redis://hostname:25001/3"
        result_serializer: "pickle"
        accept_content: ["application/json", "application/x-python-serialize"]
        result_expires: 600

Make sure to replace `hostname` with the host where the Redis database is running.

Test installation
-----------------

Run a test workflow in a *BLISS* session

.. code:: python

    DEMO_SESSION [1]: from ewoksjob.client import submit_test
    DEMO_SESSION [2]: submit_test().get()
             Out [2]: {'return_value': True}
