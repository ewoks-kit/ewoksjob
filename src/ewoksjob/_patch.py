import functools
import os
from typing import List
from typing import Optional


def patch_environment(argv: List[str]) -> None:
    """Patch before importing celery.

    This issue when celery patches:

    - Gevent's monkey-patching inspects existing locks and objects.
    - One of those objects is a Celery LocalProxy.
    - Resolving that LocalProxy forces Celery to load its full config.
    - `EwoksLoader.read_configuration` gets called which imports things
      that should not be imported before monkey-patching.
    """
    if "multi" in argv:
        return
    pool = _find_option_with_arg(argv, ["-P"], ["--pool"])
    if pool in _PATCHES:
        _PATCHES[pool]()
        # Disable patching by celery
        import celery

        celery.maybe_patch_concurrency = functools.partial(
            celery.maybe_patch_concurrency, patches={"__ewoksjob_dummy__": None}
        )


def _find_option_with_arg(argv, short_opts=None, long_opts=None) -> Optional[str]:
    """Return the value of a short or long option found in argv."""
    short_opts = short_opts or []
    long_opts = long_opts or []

    for i, arg in enumerate(argv):
        # Long options: --opt=value or --opt value
        if arg.startswith("--"):
            name, sep, val = arg.partition("=")
            if name in long_opts:
                return val if sep else argv[i + 1]

        # Short options: -o value
        if arg in short_opts:
            return argv[i + 1]


def _patch_eventlet():
    import eventlet.debug

    eventlet.monkey_patch()
    blockdetect = float(os.environ.get("EVENTLET_NOBLOCK", 0))
    if blockdetect:
        eventlet.debug.hub_blocking_detection(blockdetect, blockdetect)


def _patch_gevent():
    import gevent.monkey
    import gevent.signal

    gevent.monkey.patch_all()


_PATCHES = {
    "eventlet": _patch_eventlet,
    "gevent": _patch_gevent,
    "slurm": _patch_gevent,
}
