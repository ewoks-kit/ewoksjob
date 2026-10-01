import os
import signal
from typing import Optional

import pytest

from ..client import local
from .conftest import gevent_patched

pytestmark = pytest.mark.skipif(
    gevent_patched(), reason="process pool hangs on exit with gevent"
)


def test_process_worker_sigint():
    with local.pool_context(max_workers=1) as pool:
        future = pool.submit(_sigint_handler_is_default)
        assert future.result(timeout=60)


def test_process_worker_initializer():
    with local.pool_context(
        max_workers=1, initializer=_set_env, initargs=("EWOKSJOB_TEST", "1")
    ) as pool:
        future = pool.submit(_get_env, args=("EWOKSJOB_TEST",))
        assert future.result(timeout=60) == "1"


def _sigint_handler_is_default() -> bool:
    return signal.getsignal(signal.SIGINT) is signal.default_int_handler


def _set_env(name: str, value: str) -> None:
    os.environ[name] = value


def _get_env(name: str) -> Optional[str]:
    return os.environ.get(name)
