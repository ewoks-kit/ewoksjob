Getting started
===============

Installation
------------

Install on the client side

.. code:: bash

    pip install ewoksjob[redis]

Install on the worker side

.. code:: bash

    pip install ewoksjob[worker,redis]

The `redis` option may vary, depending on which database/broker is choosen for messaging and data transfer.

Configuration
-------------

Both the client and the worker(s) need to know where the *celery* messages
and results are stored

.. code:: python

    # SQLite backend
    broker_url = f"sqla+sqlite:///{os.path.join(..., 'celery.db')}"
    result_backend = f"db+sqlite:///{os.path.join(... ,'celery_results.db')}"

    # Redis backend
    broker_url = "redis://localhost:10003/3"
    result_backend = "redis://localhost:10003/4"

Other configurations as available, like the serialization of results (json by default)

.. code:: python

    result_serializer = "pickle"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_expires = 600

The configuration can be declared in a

- Python module:
    - myproject.config
- Python file:
    - /tmp/ewoks/config.py
- Yaml file:
    - /tmp/ewoks/config.yml
- Beacon yaml file:
    - beacon:///ewoks/config.yml
    - beacon://id22:25000/ewoks/config.yml

If the *celery* configuration is a python module, you can select the configuration with this environment variable

.. code:: bash

    export CELERY_CONFIG_MODULE=myproject.celeryconfig

By default `CELERY_CONFIG_MODULE=celeryconfig`.

If the *celery* configuration is not a python module, you can select the configuration with these environment variables

.. code:: bash

    export CELERY_LOADER=ewoksjob.config.EwoksLoader
    export CELERY_CONFIG_URI=myproject.celeryconfig

When `CELERY_CONFIG_URI=beacon:///ewoks/config.yml` you can do this instead

.. code:: bash

    export CELERY_LOADER=ewoksjob.config.EwoksLoader
    export BEACON_HOST=localhost:25000

Note: the environment variable *CELERY_LOADER* is not required to be set manually on the client side because *ewoksjob* does it for you.

Worker side
-----------

Launch a worker which serves the ewoks application

.. code:: bash

    celery -A ewoksjob.apps.ewoks worker

Client side
-----------

Prepare for sending/receiving ewoks events

.. code:: python

    # Redis backend
    events_url = "redis://localhost:10003/2"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [{"name": "url", "value": events_url}],
        }
    ]

    # SQLite backend (does not support task monitoring or cancelling)
    events_url = f"file://{os.path.join(..., 'ewoks_events.db')}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": events_url}],
        }
    ]

    reader = instantiate_reader(events_url)

Test workflow

.. code:: python

    workflow = {
        "graph": {"id": "mygraph"},
        "nodes": [
            {"id": "task1", "task_type": "method", "task_identifier": "numpy.add"},
            {"id": "task2", "task_type": "method", "task_identifier": "numpy.add"},
        ],
        "links": [
            {
                "source": "task1",
                "target": "task2",
                "data_mapping": [{"source_output": "return_value", "target_input": 0}],
            }
        ],
    }

Job arguments are the same as the arguments of `ewoks.execute_graph`

.. code:: python

    varinfo = {"root_uri": ..., "scheme": "nexus"}
    inputs = [
        {"id": "task1", "name": 0, "value": 1},
        {"id": "task1", "name": 1, "value": 2},
        {"id": "task2", "name": 1, "value": 3},
    ]
    execinfo = {"handlers": handlers}
    args = (workflow,)
    kwargs = {
        "engine": None,
        "execinfo": execinfo,
        "inputs": inputs,
        "varinfo": varinfo,
        "outputs": [{"all": False}],
    }


Execute workflow and get results

.. code:: python

    future = submit(args=args, kwargs=kwargs)
    job_id = future.task_id
    # events could be received in the mean time (see below)
    workflow_results = future.get(timeout=3, interval=0.1)
    assert workflow_results == {"return_value": 6}


Get intermediate results from ewoks events

.. code:: python

    results_during_execution = list(reader.get_events(job_id=job_id))
    assert len(results_during_execution) == 8  # start/stop for job, workflow and node

    # Get start event of node "task1"
    result_event = list(
        reader.get_events_with_variables(job_id=job_id, node_id="task1", type="start")
    )
    assert len(result_event) == 1
    result_event = result_event[0]

    # Get access to all output variables of "task1"
    results = result_event["outputs"]
    assert results.variable_values["return_value"] == 3
