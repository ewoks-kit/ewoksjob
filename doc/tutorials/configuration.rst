Configuration
=============

Celery scheduler
----------------

Both the client and the worker(s) need to know where the *celery* messages
and results are stored

.. code-block:: python

    # SQLite backend
    CELERY = {
        "broker_url": "sqla+sqlite:///path/to/celery.db"
        "result_backend": "db+sqlite:///path/to/celery_results.db"
    }

    # Redis backend
    CELERY = {
        "broker_url": "redis://localhost:10003/3
        "result_backend": "redis://localhost:10003/4"
    }

    # RabbitMQ backend
    CELERY = {
        "broker_url": "pyamqp://guest@localhost//"
        "result_backend": "rpc://"
        "result_persistent": True
    }

Other backends for results are supported (mongo, memcached). Other configuration parameters
are available, like for data serialization (json by default)

.. code-block:: python

    CELERY = {
        "broker_url": "...",
        "result_backend": "...",
        "result_serializer": "pickle",
        "accept_content: ["application/json", "application/x-python-serialize"],
        "result_expires": 600,
        "task_remote_tracebacks": True,
        "broker_connection_retry_on_startup": True,
        "enable_utc": False,
    }

The `Celery documentation <https://docs.celeryq.dev/en/stable/userguide/configuration.html>`_
describes the different parameters available.

In addition to Celery parameters, workflow execution parameters can be defined through the `EWOKS_EXECUTION` variable.

.. code-block:: python

    EWOKS_EXECUTION = {
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

.. code-block:: bash

    export EWOKS_CONFIG_URI=myproject.config

In case of a Beacon URL that has `/ewoks/config.yml`

.. code-block:: bash

    export EWOKS_CONFIG_URI=beacon://hostname:25000/ewoks/config.yml

it is enough to specify the `BEACON_HOST` environment variable

.. code-block:: bash

    export BEACON_HOST=hostname:25000

On the worker side, the configuration URI can also be provided as a CLI argument

.. code-block:: bash

    ewoksjob --config=myproject.config worker

.. note::

    The ``ewoksjob`` command line interface is a wrapper of the `Celery command line interface <https://docs.celeryq.dev/en/stable/reference/cli.html>`_.

    For more information, see the :ref:`Ewoksjob commands reference <cli>`
