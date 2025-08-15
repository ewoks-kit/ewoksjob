How to submit jobs to Slurm via a worker
========================================

To distribute jobs to a Slurm cluster, one or more workers with the `--pool=slurm` option needs to be running.
A client is in general unaware of this, unless it wants to specify Slurm job parameters for each job it submits.

Worker side
-----------

When started with the `--pool=slurm` the worker redirects jobs to a Slurm cluster.


.. code:: bash

    export SLURM_URL="http://..."
    export SLURM_USER="myname"
    export SLURM_TOKEN="eyJhbGciO..."

    ewoksjob worker --pool=slurm -Q slurm -n slurm@id00 \
        --slurm-pre-script='module load myenv' \
        --slurm-log-directory='/tmp_14_days/{user_name}/slurm_logs'
        -sp time_limit=240
        -sp current_working_directory=/path/to/data

Environment variables `SLURM_URL`, `SLURM_USER` and `SLURM_TOKEN` are needed to communicate
and authenticate with the Slurm frontend. These variables can also be specified through the
command line interface like this

.. code:: bash

    ewoksjob worker --pool=slurm -Q slurm -n slurm@id00 \
        --slurm-url=http://... \
        --slurm-user=myname \
        --slurm-token=eyJhbGciO...
        --slurm-pre-script='module load myenv' \
        --slurm-log-directory='/tmp_14_days/{user_name}/slurm_logs'
        -sp time_limit=240
        -sp current_working_directory=/path/to/data

The option `--slurm-pre-script='module load myenv'` can be provided to activate a specific environment
on Slurm in which the execute the workflows. This can be any command like `conda activate myenv`,
`source /path/to/bin/activate`, ... The environment selected in this way needs to be setup like any
other worker environment.

The option `--slurm-log-directory='/tmp_14_days/{user_name}/slurm_logs'` can be provided when Slurm jobs
should be logged. The `{user_name}` is the only string template variable available.

Slurm job parameters can be provided with `-sp <name>=<value>`. A description of all possible Slurm
parameters can be found `here <https://pyslurmutils.readthedocs.io>`_.

Client side
-----------

The client does not have to do anything special. However you can overwrite Slurm job parameters
specified by the worker or add additional parameters with the `slurm_arguments` argument.

.. code:: python

    from ewoksjob.client import submit

    kwargs["slurm_arguments"] = {
        "parameters": {
            "time_limit": 360,
            "current_working_directory": "/other/path/to/data",
        },
        "pre_script": "module load myotherenv",
    }

    future = submit(args=("/path/to/workflow.json",), kwargs=kwargs)
    result = future.result(timeout=None)
