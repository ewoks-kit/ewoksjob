from typing import Any
from . import slurm


def submit(func, *args, **kwargs) -> Any:
    """Execute directly or submit to a worker pool"""
    _submit = slurm.get_submit_function()
    if _submit is None:
        return func(*args, **kwargs)
    future = _submit(func, *args, **kwargs)
    return future.result()
