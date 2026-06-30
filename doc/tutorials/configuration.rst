Configuration
=============

Location
--------

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

Sections
--------

Celery
++++++

Both the client and the worker(s) must be configured to use the same
message broker and result backend.

The **broker** transports task messages from the client to the worker,
while the **result backend** stores task states and return values for
retrieval by the client.

.. code-block:: python

    # SQLite
    CELERY = {
        "broker_url": "sqla+sqlite:///path/to/celery.db",
        "result_backend": "db+sqlite:///path/to/celery_results.db",
    }

    # Redis
    CELERY = {
        "broker_url": "redis://localhost:10003/3",
        "result_backend": "redis://localhost:10003/4",
    }

    # RabbitMQ
    CELERY = {
        "broker_url": "pyamqp://guest@localhost//",
        "result_backend": "rpc://",
        "result_persistent": True,
    }

Celery supports many other broker and result backend implementations,
including MongoDB and Memcached.

The following example shows a recommended configuration when Python
objects such as tuples must be preserved. In this case, tasks and
results are serialized using ``pickle`` while remaining compatible
with clients or workers that still use JSON.

.. code-block:: python

    CELERY = {
        "broker_url": "...",
        "result_backend": "...",
        "task_serializer": "pickle",
        "result_serializer": "pickle",
        "accept_content": [
            "application/json",
            "application/x-python-serialize",
        ],
        "result_accept_content": [
            "application/json",
            "application/x-python-serialize",
        ],
        "result_expires": 600,
        "task_remote_tracebacks": True,
        "broker_connection_retry_on_startup": True,
        "enable_utc": False,
    }

The following Celery settings are commonly used:

- ``broker_url`` *(Client ↔ Broker ↔ Worker)*
  Connection URL of the message broker used to transport task messages.

- ``result_backend`` *(Worker ↔ Result Backend ↔ Client)*
  Connection URL of the backend used to store task states and return values.

- ``task_serializer`` *(Client → Broker)*
  Serializes outgoing task messages. ``"pickle"`` preserves Python types such as tuples.

- ``accept_content`` *(Broker → Worker)*
  List of MIME types that workers are allowed to deserialize and execute. The example accepts both JSON and pickle messages.

- ``result_serializer`` *(Worker → Result Backend)*
  Serializes task return values before storing them in the result backend. ``"pickle"`` preserves Python types.

- ``result_accept_content`` *(Result Backend → Client)*
  List of MIME types that clients are allowed to deserialize when retrieving task results.

- ``result_expires`` *(Result Backend)*
  Time-to-live (TTL), in seconds, for stored task results before they are automatically removed.

- ``task_remote_tracebacks`` *(Worker → Client)*
  Includes the worker's Python traceback in task failures, making debugging easier.

- ``broker_connection_retry_on_startup`` *(Client / Worker)*
  Retries connecting to the message broker during startup if it is temporarily unavailable.

- ``enable_utc`` *(Global)*
  Whether Celery uses UTC internally. Set to ``False`` to use the local timezone instead.

See the `Celery configuration documentation
<https://docs.celeryq.dev/en/stable/userguide/configuration.html>`_
for a complete list of configuration options.

Ewoks execution
+++++++++++++++

Workflow execution parameters can be defined through the `EWOKS_EXECUTION` variable.

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

Job scheduler
+++++++++++++

Ewoksjob options can be defined through the `EWOKSJOB_OPTIONS` variable.

.. code-block:: python

    EWOKSJOB_OPTIONS = {
        "log_memory_usage": True,
        "detect_memory_leaks": True,
    }
