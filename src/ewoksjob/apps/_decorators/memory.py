import functools
import gc
import logging
import os
import tracemalloc
from contextlib import contextmanager
from typing import Callable

import objgraph
import psutil

logger = logging.getLogger(__name__)


def log_memory_usage(celery_task: Callable) -> Callable:
    """
    Logs memory usage.
    """

    @functools.wraps(celery_task)
    def new_celery_task(self, *args, **kwargs):
        ewoksjob_options = self.app.conf.get("ewoksjob_options") or {}
        detect_memory_leaks = ewoksjob_options.get("detect_memory_leaks", False)
        log_memory_usage = detect_memory_leaks or ewoksjob_options.get(
            "log_memory_usage", False
        )

        with _memory_usage(log_memory_usage):
            return celery_task(self, *args, **kwargs)

    return new_celery_task


def log_memory_leaks(celery_task: Callable) -> Callable:
    """
    Logs garbage collection.
    """

    @functools.wraps(celery_task)
    def new_celery_task(self, *args, **kwargs):
        ewoksjob_options = self.app.conf.get("ewoksjob_options") or {}
        detect_memory_leaks = ewoksjob_options.get("detect_memory_leaks", False)

        with _trace_allocation(detect_memory_leaks):
            with _object_growth(detect_memory_leaks):
                return celery_task(self, *args, **kwargs)

    return new_celery_task


@contextmanager
def _object_growth(enable: bool):
    if enable:
        gc.collect()
        stats_before = objgraph.typestats()
    try:
        yield
    finally:
        if enable:
            gc.collect()
            stats_after = objgraph.typestats()

            diff = {
                k: stats_after.get(k, 0) - stats_before.get(k, 0)
                for k in set(stats_before) | set(stats_after)
            }
            increases = {k: v for k, v in diff.items() if v > 0}

            if increases:
                sorted_increases = sorted(increases.items(), key=lambda x: -x[1])
                top_ten = [
                    f" {obj_type}: +{count}"
                    for obj_type, count in sorted_increases[:10]
                ]

                logger.warning("[MEM] Top 10 object growth:\n %s", "\n ".join(top_ten))


@contextmanager
def _trace_allocation(enable: bool):
    if enable:
        gc.collect()
        tracemalloc.start()
        snapshot_before = tracemalloc.take_snapshot()
    try:
        yield
    finally:
        if enable:
            gc.collect()
            snapshot_after = tracemalloc.take_snapshot()
            top_stats = snapshot_after.compare_to(snapshot_before, "lineno")

            logger.warning(
                "[MEM] Top 10 allocations:\n %s", "\n ".join(map(str, top_stats[:10]))
            )


@contextmanager
def _memory_usage(enable: bool):
    if enable:
        process = psutil.Process(os.getpid())
        start_memory = process.memory_info().rss
        logger.info("[MEM] Start memory: %s", _format_bytes(start_memory))

    try:
        yield
    finally:
        if enable:
            end_memory = process.memory_info().rss
            logger.info("[MEM] End memory: %s", _format_bytes(end_memory))

            increase = end_memory - start_memory
            if increase > 0:
                logger.warning("[MEM] Memory increase: %s", _format_bytes(increase))


def _format_bytes(size: int) -> str:
    """Return human-readable memory size."""
    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    value = float(size)
    for unit in units:
        if value < 1024.0:
            return f"{value:.2f} {unit}"
        value /= 1024.0
    return f"{value:.2f} PiB"
