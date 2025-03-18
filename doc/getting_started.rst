Getting started
===============

Installation
------------

Install on the client side

.. code:: bash

    pip install ewoksjob[redis,sql]

Install on the worker side

.. code:: bash

    pip install ewoksjob[worker,redis,sql]

The `redis` and `sql` options are needed when using either for messaging or data transfer.

Configuration
-------------

Both the client and the worker(s) need to know where the *celery* messages
and results are stored

.. code:: python

    # SQLite backend
    broker_url = f"sqla+sqlite:///path/to/celery.db"
    result_backend = f"db+sqlite:///path/to/celery_results.db"

    # Redis backend
    broker_url = "redis://localhost:10003/3"
    result_backend = "redis://localhost:10003/4"

    # RabbitMQ backend
    broker_url = f"pyamqp://guest@localhost//"
    result_backend = "rpc://"
    result_persistent = True

Other backends for results are supported (mongo, memcached). Other configurations as available,
like the serialization of results (json by default)

.. code:: python

    result_serializer = "pickle"
    accept_content = ["application/json", "application/x-python-serialize"]
    result_expires = 600
    task_remote_tracebacks = True
    broker_connection_retry_on_startup = True
    enable_utc = False

The `Celery documentation <https://docs.celeryq.dev/en/stable/userguide/configuration.html>`_
describes the different parameters available.

In addition to celery arguments, workflow execution arguments can be defined through the `ewoks_execute_arguments` variable.

.. code:: python

    ewoks_execute_arguments = {
        "engine": "ppf"
        "execinfo": {
            "handlers": [
                {
                    "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
                    "arguments": [{"name": "url", "value": "redis://localhost:6379/2"}],
                }
            ]
        }
    }

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

The configuration URI can be provided as an environment variable

.. code:: bash

    export EWOKS_CONFIG_URI=myproject.config

In case of a Beacon URL that has `/ewoks/config.yml`

.. code:: bash

    export EWOKS_CONFIG_URI=beacon://hostname:25000/ewoks/config.yml

it is enough to specify the `BEACON_HOST` environment variable

.. code:: bash

    export BEACON_HOST=hostname:25000

On the worker side, the configuration URI can also be provided as a CLI argument

.. code:: bash

    ewoksjob --config=myproject.config worker

Worker side
-----------

Launch a worker which serves the ewoks application

.. code:: bash

    ewoksjob worker

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
    assert results["return_value"].value == 3

Install brokers
---------------

Redis can be installed using the system package manager or conda

.. code:: bash

    apt install redis-server    # system package
    conda install redis-server  # conda package
    redis-server

RabbitMQ can be installed using the system package manager or conda

.. code:: bash

    apt install rabbitmq-server    # system package
    conda install rabbitmq-server  # conda package
    rabbitmq-server
