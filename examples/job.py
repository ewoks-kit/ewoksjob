"""Send a workflow to the ewoks Celery application and recieve the
intermediate results (ewoks events) or final result (job return value)
"""

import os
from ewoksjob.client import submit
from ewoksjob.events.readers import instantiate_reader

# Results directory
SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "results")
os.makedirs(DATA_DIR, exist_ok=True)

# Load configuration ("celeryconfig" is the default)
# from celery import current_app
# current_app.config_from_object("celeryconfig")

# Events during execution
if False:
    # Redis backend
    events_url = "redis://localhost:10003/2"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [{"name": "url", "value": events_url}],
        }
    ]
else:
    # SQLite backend (flower will not work)
    events_url = f"file://{os.path.join(DATA_DIR, 'ewoks_events.db')}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": events_url}],
        }
    ]


reader = instantiate_reader(events_url)

# Test workflow
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

# Job arguments
varinfo = {"root_uri": DATA_DIR, "scheme": "nexus"}
inputs = [
    {"id": "task1", "name": 0, "value": 1},
    {"id": "task1", "name": 1, "value": 2},
    {"id": "task2", "name": 1, "value": 3},
]
execinfo = {"handlers": handlers}
args = (workflow,)
kwargs = {
    "binding": None,
    "execinfo": execinfo,
    "inputs": inputs,
    "varinfo": varinfo,
    "outputs": [{"all": False}],
}


# Execute workflow and get results
future = submit(*args, **kwargs)
job_id = future.task_id
# events could be received in the mean time (see below)
workflow_results = future.get(timeout=3, interval=0.1)
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
assert results.variable_values["return_value"] == 3
