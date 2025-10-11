Submit an Ewoks workflow
========================

Example workflow
----------------

.. code-block:: python

    workflow = {
        "graph": {"id": "mygraph"},
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

Job arguments
-------------

Handler configuration for sending/receiving Ewoks events through Redis

.. code-block:: python

    import os

    # Redis backend
    events_url = "redis://localhost:10003/2"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [{"name": "url", "value": events_url}],
        }
    ]

    # SQLite backend (does not support task monitoring or cancelling)
    events_url = f"file://{os.path.join(..., 'ewoks_events.db')}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": events_url}],
        }
    ]

Job arguments are the same as the arguments of `ewoks.execute_graph`

.. code-block:: python

    varinfo = {"root_uri": ..., "scheme": "nexus"}
    inputs = [
        {"id": "task1", "name": 0, "value": 1},
        {"id": "task1", "name": 1, "value": 2},
        {"id": "task2", "name": 1, "value": 3},
    ]
    execinfo = {"handlers": handlers}
    args = (workflow,)
    kwargs = {
        "engine": None,
        "execinfo": execinfo,
        "inputs": inputs,
        "varinfo": varinfo,
        "outputs": [{"all": False}],
    }

Submit workflow
---------------

Execute workflow and get results

.. code-block:: python

    from ewoksjob.client import submit

    future = submit(args=args, kwargs=kwargs)
    job_id = future.uuid
    # events could be received in the mean time (see below)
    workflow_results = future.result(timeout=3)
    assert workflow_results == {"return_value": 6}

Monitor Ewoks events
--------------------

Get intermediate results from Ewoks events

.. code-block:: python

    from ewoksjob.events.readers import read_ewoks_events

    with read_ewoks_events(events_url) as reader:
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
