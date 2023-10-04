Usage with *BLISS* at the ESRF
==============================

For online data processing with *Ewoks*, a beamline needs at least one python environment
with the scientific libraries installed (conda or anything else) and Ewoks to be configured
in Beacon. When workflows are triggered from *BLISS*, the *BLISS* conda environment needs
the *ewoksjob* python package.

.. _Worker environment:

Worker environment
------------------

Create a python environment (conda, venv, ...) as *blissadm*.

When using conda, create a conda environment for the worker (called `ewoksworker` in this example) like this

.. code:: bash

    conda create --name ewoksworker python=3.9

Any python version supported by `ewoksjob` will do. Activate the environment

.. code:: bash

    conda activate ewoksworker

Install basic worker dependencies

.. code:: bash

    pip install ewoksjob[blissworker]

Install the project(s) that implement the actual worker tasks (depends on the beamline).

Some beamlines may want multiple environments for different scientific software.

Supervisor
----------

The supervisor config should be created in `/users/blissadm/local/daemon/config/supervisor.d/ewoks.conf`.

Each change made to the configuration must be applied by the `supervisorctl` shell command:
  - `supervisorctl reread`: to load changes in the config.
  - `supervisorctl update`: to apply changes in the config.

This is an example that registers a job monitor (you only ever need one) and one worker (you may need more than one):

.. code::

    [group:ewoks]
    programs=ewoksmonitor, ewoksworker
    priority=900

    [program:ewoksmonitor]
    command=bash -c "source /users/blissadm/conda/miniconda/bin/activate ewoksworker && ewoksjob monitor"
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000"
    startsecs=5
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

    [program:ewoksworker]
    command=bash -c "source /users/blissadm/conda/miniconda/bin/activate ewoksworker && ewoksjob worker"
    directory=/users/opid00/
    user=opid00
    environment=BEACON_HOST="id00:25000"
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
In this case `directory=/users/opid00/ewoks` is probably more appropriate. All `.py` files in this directory and its subdirectories
can contain ewoks tasks.

Instead of `BEACON_HOST="id00:25000"` you could provide an explicit URL of the celery configuration with `EWOKS_CONFIG_URI`

.. code::

    [program:ewoksmonitor]
    ...
    environment=EWOKS_CONFIG_URI="beacon:///id00:25000/ewoks/config.yml"

    [program:ewoksworker]
    ...
    environment=EWOKS_CONFIG_URI="beacon:///id00:25000/ewoks/config.yml"

*BLISS* environment
-------------------

Activate the *BLISS* conda environment

.. code:: bash

    . blissenv -d

Install the client dependencies for `bliss >=1.11`

.. code:: bash

    pip install ewoksjob

For older versions of bliss do this instead

.. code:: bash

    conda install celery  # Bliss dependencies were managed by conda
    pip install ewoksjob, blissdata

This is only needed when workflows are triggered directly from *BLISS*.

When triggering workflows, either the `BEACON_HOST` or `EWOKS_CONFIG_URI` environment variables need to be provided.
When triggering directly from *BLISS*, the `BEACON_HOST` environment variable is already set so nothing extra to do.

Beacon configuration
--------------------

Ewoks must be configured in the beamline configuration (Beacon). For example

.. code:: yaml

    # /users/blissadm/local/beamline_configuration/ewoks/__init__.yml

    bliss_ignored: true

.. code:: yaml

    # /users/blissadm/local/beamline_configuration/ewoks/config.yml

    celery:
        broker_url: "redis://id00:25001/2"
        result_backend: "redis://id00:25001/3"
        result_serializer: "pickle"
        accept_content: ["application/json", "application/x-python-serialize"]
        result_expires: 600
        task_remote_tracebacks: true

Make sure to replace `id00` with the host where the Redis database is
running on (never use *localhost*).

Test installation
-----------------

Run a test workflow in a *BLISS* session

.. code:: python

    DEMO_SESSION [1]: from ewoksjob.client import submit_test
    DEMO_SESSION [2]: submit_test().get()
             Out [2]: {'return_value': True}


Slurm
-----

A worker that redirects jobs to slurm can be started with the `--pool=slurm` option

.. code::

    [group:ewoks]
    programs=ewoksmonitor, ewoksworker, ewoksworker_slurm
    priority=900

    [program:ewoksworker_slurm]
    command=bash -c "source /users/blissadm/conda/miniconda/bin/activate ewoksworker && exec ewoksjob worker --pool=slurm -Q slurm -n slurm@id00 --slurm-pre-script='module load ...' --slurm-log-directory='/tmp_14_days/{user_name}/slurm_logs' -sp time_limit=240"
    directory=/users/opid00/
    user=opid00
    environment=
        BEACON_HOST="id00:25000",
        SLURM_URL="http://...",
        SLURM_USER="opid00",
        SLURM_TOKEN="eyJhbGciO..."
    startsecs=2
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

More details on the parameters can be found :ref:`here <Slurm>`. The environment specified with
`--slurm-pre-script` needs to be setup like any other worker environment (see :ref:`Worker environment`).

Ewoks server
------------

To provide ewoks as a web service with a web GUI you can install this in the worker environment

.. code:: bash

    pip install ewoksserver[frontend]

Configure the server in the supervisor configuration file

.. code::

    [group:ewoks]
    programs=..., ewoksserver
    priority=900

    ...

    [program:ewoksserver]
    command=bash -c "source /users/blissadm/conda/miniconda/bin/activate ewoksworker && python -u -m ewoksserver.server -c /users/blissadm/local/daemon/config/supervisor.d/ewoksserverconfig.py --host=0.0.0.0"
    directory=/users/opid00/ewoks/
    user=opid00
    environment=BEACON_HOST="id00:25000"
    startsecs=5
    autostart=true
    redirect_stderr=true
    stdout_logfile=/var/log/%(program_name)s.log
    stdout_logfile_maxbytes=1MB
    stdout_logfile_backups=10
    stdout_capture_maxbytes=1MB

Finally the server configuration should be saved in addition to the supervisor configuration

.. code:: python

    # /users/blissadm/local/daemon/config/supervisor.d/ewoksserverconfig.py

    RESOURCE_DIRECTORY = "/users/opid01/ewoks/resources"

    EWOKS = {
        "handlers": [
            {
                "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
                "arguments": [
                    {
                        "name": "url",
                        "value": "redis://id00:25001/4",
                    },
                    {"name": "ttl", "value": 86400},
                ],
            }
        ]
    }

    CELERY = {}

Make sure to replace `id00` with the beamline name.

Note: since `CELERY` is defined but empty, the server will use `BEACON_HOST` to fetch
the celery configuration. This ensures that ewoks server executes workflows by sending
them to the workers instead of executing them locally in a subprocess.
