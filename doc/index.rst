ewoksjob |release|
===================

ewoksjob provides utilities for job scheduling of `ewoks <https://ewoks.readthedocs.io/>`_ workflows.

ewoksjob has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_ of the `European Synchrotron <https://www.esrf.eu/>`_.

Getting started
---------------

Install on the client side

.. code:: bash

    pip install ewoksjob[redis]

Install on the worker side

.. code:: bash

    pip install ewoksjob[worker,redis,monitor]

The communication between client and worker goes through *Redis*, *RabbitMQ* or *Sqlite3*.
Depending on which one you choose, the `redis` installation option may vary. Both client and
worker need access to a configuration that specifies the URL of the database and/or broker.

Start a worker that can execute *ewoks* graphs

.. code:: bash

    ewoksjob worker

Start a workflow from python, possible from another machine

.. code:: python

    from ewoksjob.client import submit

    workflow = {"graph": {"id": "mygraph"}}
    future = submit(args=(workflow,))
    result = future.get()

Start a web server for monitoring jobs

.. code:: bash

    ewoksjob monitor

Run the tests

.. code:: bash

    pip install ewoksjob[test]
    pytest --pyargs ewoksjob.tests

Documentation
-------------

.. toctree::
    :maxdepth: 2

    getting_started
    routing
    bliss
    api
