from .base import *  # noqa F401
from .sqlite3 import Sqlite3EwoksEventReader  # noqa F401

try:
    from .redis import RedisEwoksEventReader  # noqa F401
except ImportError:
    pass


def instantiate_reader(url: str, **kw) -> EwoksEventReader:  # noqa F405
    s = url.lower()
    if any(s.startswith(scheme) for scheme in ("redis:", "rediss:", "unix:")):
        return RedisEwoksEventReader(url, **kw)
    elif s.startswith("file:"):
        return Sqlite3EwoksEventReader(url, **kw)
    else:
        raise ValueError(f"unknown scheme for '{url}'")
