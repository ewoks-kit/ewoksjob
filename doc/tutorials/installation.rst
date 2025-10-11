Installation
============

Install on the client side

.. code-block:: bash

    pip install ewoksjob[redis,sql]

Install on the worker side

.. code-block:: bash

    pip install ewoksjob[worker,redis,sql]

Install on the monitor side

.. code-block:: bash

    pip install ewoksjob[monitor,redis,sql]

The `redis` and `sql` options are needed for the Celery message broker and result backend.

Install Celery brokers
----------------------

Redis can be installed using the system package manager or conda

.. code-block:: bash

    apt install redis-server    # system package
    conda install redis-server  # conda package
    redis-server

RabbitMQ can be installed using the system package manager or conda

.. code-block:: bash

    apt install rabbitmq-server    # system package
    conda install rabbitmq-server  # conda package
    rabbitmq-server
