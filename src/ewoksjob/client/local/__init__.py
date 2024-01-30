"""Client side pool managed in the current process
"""

from concurrent.futures import CancelledError  # noqa F401

CancelledErrors = (CancelledError,)
from .tasks import *  # noqa F403
from .utils import *  # noqa F403
from .pool import *  # noqa F403
from .tasks import execute_graph as submit  # noqa F401
from .tasks import execute_test_graph as submit_test  # noqa F401

try:
    from gevent.monkey import is_anything_patched
    from gevent.monkey import is_module_patched
except ImportError:
    pass
else:
    if is_anything_patched() and not is_module_patched("threading"):
        raise RuntimeError("gevent patching needs to include 'threading'")
