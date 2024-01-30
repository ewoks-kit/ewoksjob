"""Remote worker pool managed by Celery
"""

import os
from billiard.exceptions import Terminated

try:
    from gevent.monkey import is_anything_patched
    from gevent.monkey import is_module_patched
except ImportError:
    pass
else:
    if is_anything_patched() and not is_module_patched("threading"):
        # Make Celery use `celery.backends.asynchronous.Drainer`
        # instead of `celery.backends.asynchronous.geventDrainer`.
        # The later causes CTRL-C to not be raised and other things
        # like Bliss scans to hang when calling `AsyncResult.get`.
        from kombu.utils import compat

        compat._environment = "default"

        # The real solution is to patch threads.

from celery.exceptions import TaskRevokedError as CancelledError

CancelledErrors = CancelledError, Terminated
from .tasks import *  # noqa F403
from .utils import *  # noqa F403
from .tasks import execute_graph as submit  # noqa F401
from .tasks import execute_test_graph as submit_test  # noqa F401

# For clients (workers need it in the environment before stating the python process)
os.environ.setdefault("CELERY_LOADER", "ewoksjob.config.EwoksLoader")
