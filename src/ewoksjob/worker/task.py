from typing import Any
from functools import wraps
from .errors import replace_exception_for_client
from . import slurm


def worker_execute_wrapper(func):
    """Decorator all ewoks celery tasks"""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        """Worker pools that need to wrap their tasks
        can implement a `get_executor` function.
        """
        with replace_exception_for_client():
            _executor = slurm.get_executor()
            if _executor is None:
                return func(*args, **kwargs)
            return _executor(func, *args, **kwargs)

    return wrapper
