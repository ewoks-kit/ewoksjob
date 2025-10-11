.. _cli:

CLI reference
=============

The ``ewoksjob`` command line interface is a wrapper of the `Celery command line interface <https://docs.celeryq.dev/en/stable/reference/cli.html>`_.

We document below the commands that behave slightly differently or are specifically interesting for Ewoks. 

For the rest, see the `Celery command line interface documentation <https://docs.celeryq.dev/en/stable/reference/cli.html>`_.

.. tip::

    All commands below accept Celery options as ``[OPTIONS]``

ewoksjob monitor
----------------

.. code-block::

    ewoksjob [OPTIONS] monitor [FLOWER OPTIONS]


Starts a `Flower <https://flower.readthedocs.io/en/latest/index.html>`_ instance to monitor jobs.

Alias of ``celery flower``. Full details in the `Flower documentation <https://flower.readthedocs.io/en/latest/config.html#command-line>`_.

ewoksjob worker
---------------

.. code-block::

    ewoksjob worker [OPTIONS]


Starts an Ewoks worker. Wrapper of `celery worker <https://docs.celeryq.dev/en/stable/reference/cli.html#celery-worker>`_

The Ewoks worker is a Celery worker for the `ewoksjob.apps.ewoks` app (i.e. the `app CLI option <https://docs.celeryq.dev/en/stable/reference/cli.html#cmdoption-celery-A>`_ ``-A/--app`` is automatically set to `ewoksjob.apps.ewoks`).

In addition, the log level is set to `INFO` by default (``-l/--loglevel``).

In short, this is equivalent of running

.. code-block::

    celery worker -A ewoksjob.apps.ewoks -l INFO


ewoksjob purge
---------------

.. code-block::

    ewoksjob purge [OPTIONS]

Alias of `celery purge <https://docs.celeryq.dev/en/stable/reference/cli.html#celery-purge>`_. Erases all messages from all known task queues.

.. warning::

    There is no undo operation for this command.
