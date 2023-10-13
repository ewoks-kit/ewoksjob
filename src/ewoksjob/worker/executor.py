from typing import Callable, Optional


ExecutorType = Optional[Callable]
_GET_EXECUTOR: Optional[Callable[[], ExecutorType]] = None


def set_executor_getter(get_executor: Callable[[], ExecutorType]) -> None:
    """Worker pools that need to wrap their tasks can implement a
    `get_executor` function and register it here.
    """
    global _GET_EXECUTOR
    _GET_EXECUTOR = get_executor


def get_executor() -> ExecutorType:
    if _GET_EXECUTOR is None:
        return
    return _GET_EXECUTOR()
