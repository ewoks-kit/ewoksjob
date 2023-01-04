"""Remote worker pool managed by Celery
"""
import os
from billiard.exceptions import Terminated
from celery.exceptions import TaskRevokedError as CancelledError

CancelledErrors = CancelledError, Terminated
from .tasks import *  # noqa F403
from .utils import *  # noqa F403
from .tasks import execute_graph as submit  # noqa F401
from .tasks import execute_test_graph as submit_test  # noqa F401

# For clients (workers need it in the environment before stating the python process)
os.environ.setdefault("CELERY_LOADER", "ewoksjob.config.EwoksLoader")
