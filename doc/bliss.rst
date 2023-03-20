Usage with *BLISS* at the ESRF
==============================

For online data processing with *Ewoks*, a beamline needs at least one python environment
with the scientific libraries installed (conda or anything else) and Ewoks to be
enabled in the beamline configuration (Beacon). When workflows are triggered from *BLISS*,
the *BLISS* conda environment needs *ewoksjob* to be installed.

Worker environment
------------------

Create a python environment (conda, venv, ...) under *blissadm* (BCU manages the scientific software)
or *opid00* (beamline staff manages the scientific software).

When using conda, create a conda environment for the worker (called `ewoksworker` in this example) like this

.. code:: bash

    conda create --name ewoksworker python=3.8

Activate the environment

.. code:: bash

    conda activate ewoksworker

Install basic worker dependencies

.. code:: bash

    pip install ewoksjob[blissworker]

Install the project(s) that implement the actual worker tasks (depends on the beamline).

Some beamlines may want multiple environments for different scientific software.

Supervisor
----------

The supervisor config should be created in `/users/blissadm/local/daemon/config/supervisor.d`. 

At each change, the configuration must be reloaded in `supervisor` through `supervisorctl`. 

For this, run `supervisorctl` to enter supervisor's shell and then the following commands:
  - `reread`: to check changes in the config. It should print that the `ewoks` config changed
  - `update`: to apply changes in the config.

Other `supervisorctl` commands can be listed with `help`.

Below is an example that registers a job monitor (you only ever need one) and one worker (you may need more than one).

.. code::

    [group:ewoks]
    programs=ewoksmonitor, ewoksworker
    priority=900

    [program:ewoksmonitor]
    command=bash -c "source /users/blissadm/conda/miniconda/bin/activate ewoksworker && celery flower"
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000",CELERY_LOADER="ewoksjob.config.EwoksLoader"
    startsecs=5
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

    [program:ewoksworker]
    command=bash -c "source /users/blissadm/conda/miniconda/bin/activate ewoksworker && celery -A ewoksjob.apps.ewoks worker"
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000",CELERY_LOADER="ewoksjob.config.EwoksLoader"
    startsecs=5
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

Make sure to replace `opid00` and `id00` with the proper string.

The filename `/users/blissadm/conda/miniconda/bin/activate` may differ as well. Type `conda activate base;type activate` in a terminal
with the correct user to see where the conda activation script is located.

The working directory is important if the beamline wants to quickly add workflow tasks (i.e. without pip-installing a python project).
In this case `directory=/users/opid00/ewoks` is probably more appropriate. All `.py` files in this directory can contain ewoks tasks.

Instead of `BEACON_HOST="id00:25000"` you could provide an explicit URL of the celery configuration with `CELERY_CONFIG_URI`

.. code::

    [program:ewoksmonitor]
    ...
    environment=CELERY_CONFIG_URI="beacon:///id00:25000/ewoks/config.yml",CELERY_LOADER="ewoksjob.config.EwoksLoader"

    [program:ewoksworker]
    ...
    environment=CELERY_CONFIG_URI="beacon:///id00:25000/ewoks/config.yml",CELERY_LOADER="ewoksjob.config.EwoksLoader"

*BLISS* environment
-------------------

Activate the *BLISS* conda environment

.. code:: bash

    . blissenv -d

Install the client dependencies

.. code:: bash

    conda install celery
    pip install ewoksjob

This is only needed when workflows are triggered directly from *BLISS*.

When triggering workflows, either the `BEACON_HOST` or `CELERY_CONFIG_URI` environment variables need to be provided.
When triggering directly from *BLISS*, the `BEACON_HOST` environment variable is already set so nothing extra to do.

.. note::
    
    For `bliss<=1.10`, `blissdata` must be installed separately

    .. code:: bash

        pip install blissdata

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
        task_remote_tracebacks: true

Make sure to replace `hostname` with the host where the Redis database is
running (never use *localhost*).

Test installation
-----------------

Run a test workflow in a *BLISS* session

.. code:: python

    DEMO_SESSION [1]: from ewoksjob.client import submit_test
    DEMO_SESSION [2]: submit_test().get()
             Out [2]: {'return_value': True}
