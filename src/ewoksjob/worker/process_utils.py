import os
import signal

from billiard.common import reset_signals
from celery.concurrency import prefork


def process_initializer(*args):
    os.environ["FORKED_BY_MULTIPROCESSING"] = "1"
    prefork.process_initializer(*args)
    reset_signals(full=True)
    try:
        signal.signal(signal.SIGINT, signal.SIG_IGN)
    except AttributeError:
        pass


process_destructor = prefork.process_destructor
