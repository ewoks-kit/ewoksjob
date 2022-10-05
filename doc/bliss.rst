Usage with *BLISS* at the ESRF
==============================

For online data processing with *Ewoks*, a beamline needs at least one python environment
with the scientific libraries installed (conda or anything else) and Ewoks to be
enabled in the beamline configuration (Beacon). When workflows are triggered from *BLISS*,
the *BLISS* conda environment needs *ewoksjob* to be installed.

Worker environment
------------------

Decide first whether the code needs to be managed and edited by the beamline staff or BCU.
When the data processing code is well established and doesn't change often, most likely the
BCU will manage it.

Some beamlines will need more than one worker environment.

Managed by *blissadm*
+++++++++++++++++++++

Create a conda environment for the worker, in this example called `ewoksworker`

.. code:: bash

    conda create --prefix /users/blissadm/conda/miniconda/envs/ewoksworker python=3.7

Activate the environment

.. code:: bash

    . blissenv -e ewoksworker

Basic worker dependencies

.. code:: bash

    python3 -m pip install ewoksjob[worker,beacon,redis,monitor,slurm]

Install the project(s) that implement the actual worker tasks (depends on the beamline).

Managed by *opid00*
+++++++++++++++++++

Create a conda environment for the worker, in this example called `ewoksworker`

.. code:: bash

    conda create --name ewoksworker python=3.7

Activate the environment

.. code:: bash

    conda activate ewoksworker

Basic worker dependencies

.. code:: bash

    python3 -m pip install ewoksjob[worker,beacon,redis,monitor,slurm]

Install the project(s) that implement the actual worker tasks (depends on the beamline).

Supervisor
----------

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

This is only needed when workflows are triggered directly from *BLISS*.

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

Make sure to replace `hostname` with the host where the Redis database is
running (never use *localhost*).

Test installation
-----------------

Run a test workflow in a *BLISS* session

.. code:: python

    DEMO_SESSION [1]: from ewoksjob.client import submit_test
    DEMO_SESSION [2]: submit_test().get()
             Out [2]: {'return_value': True}
