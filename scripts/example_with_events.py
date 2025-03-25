"""Send a workflow to the ewoks Celery application and receive the
intermediate results (ewoks events) or final result (job return value)
"""

import os
import argparse
from typing import Optional

from ewoksjob.client import submit
from ewoksjob.client.local import submit as submit_local
from ewoksjob.client.local import pool_context
from ewoksjob.events.readers import instantiate_reader

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


def ewoks_event(celery: Optional[bool] = None, redis: bool = True):
    if celery:
        handlers = []  # in worker configuration
        if redis:
            events_url = "redis://localhost:6379/2"
        else:
            dbfile = os.path.join(SCRIPT_DIR, "results", "ewoks", "ewoks_events.db")
            events_url = f"file://{dbfile}"
    else:
        # SQLite backend
        dbfile = os.path.join(SCRIPT_DIR, "results", "ewoks", "ewoks_events.db")
        os.makedirs(os.path.dirname(dbfile), exist_ok=True)
        events_url = f"file://{dbfile}"
        handlers = [
            {
                "class": "ewoksjob.events.handlers.Sqlite3EwoksEventHandler",
                "arguments": [{"name": "uri", "value": events_url}],
            }
        ]

    reader = instantiate_reader(events_url)
    execinfo = {"handlers": handlers}
    return reader, execinfo


def test_workflow():
    workflow = {
        "graph": {"id": "mygraph", "version": "1.0"},
        "nodes": [
            {"id": "task1", "task_type": "method", "task_identifier": "numpy.add"},
            {"id": "task2", "task_type": "method", "task_identifier": "numpy.add"},
        ],
        "links": [
            {
                "source": "task1",
                "target": "task2",
                "data_mapping": [{"source_output": "return_value", "target_input": 0}],
            }
        ],
    }
    inputs = [
        {"id": "task1", "name": 0, "value": 1},
        {"id": "task1", "name": 1, "value": 2},
        {"id": "task2", "name": 1, "value": 3},
    ]
    varinfo = {
        "root_uri": os.path.join(SCRIPT_DIR, "results", "example_with_events"),
        "scheme": "nexus",
    }
    return workflow, inputs, varinfo


def job_argument(celery: Optional[bool] = None, redis: bool = True):
    reader, execinfo = ewoks_event(celery=celery, redis=redis)
    workflow, inputs, varinfo = test_workflow()
    args = (workflow,)
    kwargs = {
        "engine": None,
        "execinfo": execinfo,
        "inputs": inputs,
        "varinfo": varinfo,
    }
    return reader, args, kwargs


def assert_results(workflow_results, reader, job_id):
    # events could be received in the mean time (see below)
    assert workflow_results == {"return_value": 6}

    # Get intermediate results from ewoks events
    results_during_execution = list(reader.get_events(job_id=job_id))
    assert len(results_during_execution) == 8  # start/stop for job, workflow and node

    # Get start event of node "task1"
    result_event = list(
        reader.get_events_with_variables(job_id=job_id, node_id="task1", type="start")
    )
    assert len(result_event) == 1
    result_event = result_event[0]

    # Get access to all output variables of "task1"
    results = result_event["outputs"]
    assert results["return_value"].value == 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Launch XRPD workflow")
    parser.add_argument(
        "--celery",
        dest="celery",
        action="store_true",
        help="Use celery worker",
    )
    parser.add_argument(
        "--redis",
        dest="redis",
        action="store_true",
        help="Use celery with Redis",
    )
    options = parser.parse_args()

    reader, args, kwargs = job_argument(celery=options.celery, redis=options.redis)

    if options.celery:
        future = submit(args=args, kwargs=kwargs)
        workflow_results = future.get(timeout=3, interval=0.1)
    else:
        with pool_context():
            future = submit_local(args=args, kwargs=kwargs)
            workflow_results = future.result(timeout=3)

    assert_results(workflow_results, reader, future.task_id)
