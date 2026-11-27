"""Patch of the Celery prefork pool for billiard start methods other than fork."""

import os
from importlib.metadata import version
from typing import Any

import billiard
from celery.concurrency import prefork
from celery.concurrency.prefork import process_initializer as _process_initializer
from packaging.version import Version


def patch_prefork_pool() -> None:
    """Make the prefork pool set up the Celery worker optimizations in child processes that are not forked.

    Celery 5.7.0 fixes this upstream: https://github.com/celery/celery/issues/10683
    """
    if Version(version("celery")) >= Version("5.7.0"):
        return
    prefork.process_initializer = _patched_process_initializer


def _patched_process_initializer(*args: Any) -> None:
    if billiard.get_start_method() != "fork":
        # Celery only sets up the worker optimizations in the child process when this variable is set.
        os.environ["FORKED_BY_MULTIPROCESSING"] = "1"
    _process_initializer(*args)
