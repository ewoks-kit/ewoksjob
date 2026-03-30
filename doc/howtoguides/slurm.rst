How to submit jobs to Slurm via a worker
========================================

To distribute jobs to a Slurm cluster, one or more workers with the ``--pool=slurm`` option needs to be running.
A client is in general unaware of this, unless it wants to specify Slurm job parameters for each job it submits.

Worker side
-----------

When started with the ``--pool=slurm`` the worker redirects jobs to a Slurm cluster.

.. code-block:: bash

    export SLURM_URL="http://..."
    export SLURM_USER="myname"
    export SLURM_TOKEN="eyJhbGciO..."

    ewoksjob worker --pool=slurm -Q slurm -n slurm@id00 \
        --slurm-pre-script='module load myenv' \
        --slurm-log-directory='/tmp_14_days/{user_name}/slurm_logs'
        -sp time_limit=240
        -sp current_working_directory=/path/to/data
        -se VAR1
        -se VAR2=VALUE2

Environment variables ``SLURM_URL``, ``SLURM_USER`` and ``SLURM_TOKEN`` are needed to communicate
and authenticate with the Slurm frontend. These variables can also be specified through the
command line interface like this

.. code-block:: bash

    ewoksjob worker --pool=slurm -Q slurm -n slurm@id00 \
        --slurm-url=http://... \
        --slurm-user=myname \
        --slurm-token=eyJhbGciO...
        --slurm-pre-script='module load myenv' \
        --slurm-log-directory='/tmp_14_days/{user_name}/slurm_logs'
        -sp time_limit=240
        -sp current_working_directory=/path/to/data
        -se VAR1
        -se VAR2=VALUE2

The option ``--slurm-pre-script='module load myenv'`` can be provided to activate a specific environment
on Slurm in which the execute the workflows. This can be any command like `conda activate myenv`,
``source /path/to/bin/activate`, ... The environment selected in this way needs to be setup like any
other worker environment.

The option ``--slurm-log-directory='/tmp_14_days/{user_name}/slurm_logs'`` can be provided when Slurm jobs
should be logged. The ``{user_name}`` is the only string template variable available.

Slurm job parameters can be provided with ``-sp <name>=<value>``. A description of all possible Slurm
parameters can be found `here <https://pyslurmutils.readthedocs.io>`_.

Slurm job environment variables can be provided separately with ``-se <name>[=<value>]``. When the value is omitted
the variables is loaded from the local environment. In addition enviroment variables ``SLURM_ENV_HELLO=world``
are loaded by `pyslurmutils` and send to slurm as ``HELLO=world``.

Environment variables
^^^^^^^^^^^^^^^^^^^^^

Slurm job environment variables can be passed in three ways. For example:

.. code-block:: bash

    export MYVAR3=MYVALUE3
    export SLURM_ENV_MYVAR5=MYVALUE5

    ewoksjob worker --pool=slurm \
            -sp environment='{"MYVAR1":"MYVALUE1", "MYVAR2":"MYVALUE2"}'
            -se MYVAR3
            -se MYVAR4=MYVALUE4

In this example, the final Slurm job parameter ``environment`` will be:

.. code-block:: bash

    environment = {
        "MYVAR1": "MYVALUE1",   # from -sp JSON
        "MYVAR2": "MYVALUE2",   # from -sp JSON
        "MYVAR3": "MYVALUE3",   # from local env, referenced by -se
        "MYVAR4": "MYVALUE4",   # from -se argument
        "MYVAR5": "MYVALUE5",   # from SLURM_ENV_*
    }

Note that ``MYVAR3`` needs to be referenced by ``-se`` to be passed to SLURM.

Other environment variables do not get passed automatically unless they start
with the prefix ``SLURM_ENV_`` in which case the prefix is stripped before passing
the variable to SLURM. For example the local environment variable ``SLURM_ENV_FOO=bar``
becomes SLURM job environment variable ``FOO=bar``.

Priority of environment variables from high to low:

1. ``-se`` (explicit Slurm environment variable argument)
2. ``-sp`` (parameters JSON environment)
3. ``SLURM_ENV_*`` (local environment variables prefixed with `SLURM_ENV_`)

Variables from a higher-priority source override those from lower-priority sources.

Client side
-----------

The client does not have to do anything special. However you can overwrite Slurm job parameters
specified by the worker or add additional parameters with the ``slurm_arguments`` argument.

.. code-block:: python

    from ewoksjob.client import submit

    kwargs["slurm_arguments"] = {
        "parameters": {
            "partition": "pname",
            "cpus_per_task": 8,
            "memory_per_cpu": "8GB",
            "time_limit": "02:00:00",
            "tres_per_node": "gres/gpu=1",
            "current_working_directory": "/other/path/to/data",
        },
        "pre_script": "module load myotherenv",
        "python_cmd": "python"
    }

    future = submit(args=("/path/to/workflow.json",), kwargs=kwargs)
    result = future.result(timeout=None)

A description of all possible Slurm parameters can be found `here <https://pyslurmutils.readthedocs.io>`_.
