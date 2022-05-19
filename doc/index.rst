ewoksjob |release|
===================

ewoksjob provides utilities for job scheduling of `Ewoks <https://gitlab.esrf.fr/workflow/ewoks/ewoks>`_workflows.

ewoksjob has been developed by the `Software group <http://www.esrf.eu/Instrumentation/software>`_ of the `European Synchrotron <https://www.esrf.eu/>`_.

Start a worker pool that can execute ewoks graphs

```bash
celery -A ewoksjob.apps.ewoks worker
```

Start a workflow on the client side

```bash
from ewoksjob.client import submit

workflow = {"graph": {"id": "mygraph"}}
future = submit(args=(workflow,))
result = future.get()
```

Note that both environements need to be able to import `celeryconfig` which
contains celery configuration (mainly the message broker and result backend URL's).

.. toctree::
    :maxdepth: 2

    getting_started
    routing
    api
