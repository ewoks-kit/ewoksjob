"""Send a workflow to the ezoks Celery application and recieve the
intermediate results (ewoks events) or final result (job return value)
"""

import os
from time import time
from celery.execute import send_task
from ewoksbliss.events.reader import RedisEwoksEventReader


# Configure celery in case celeryconfig.py is missing
#
# from celery import current_app
# current_app.conf.broker_url = "redis://localhost:10003/3"
# current_app.conf.result_backend = "redis://localhost:10003/4"
# current_app.conf.result_serializer = "pickle"
# current_app.conf.accept_content = ["application/json", "application/x-python-serialize"]


# Job arguments
job_id = time()
events_url = "redis://localhost:10003/2"
workflow = {
    "graph": {"id": "mygraph"},
    "nodes": [{"id": "task1", "task_type": "method", "task_identifier": "numpy.add"}],
}
varinfo = {"root_uri": os.path.join(os.getcwd(), "results"), "scheme": "nexus"}
inputs = [
    {"id": "task1", "name": 0, "value": 1},
    {"id": "task1", "name": 1, "value": 2},
]
execinfo = {
    "job_id": job_id,
    "handlers": [
        {
            "class": "ewoksbliss.events.handlers.EwoksRedisEventHandler",
            "arguments": [{"name": "url", "value": events_url}],
        }
    ],
}
args = (workflow,)
kwargs = {
    "binding": None,
    "execinfo": execinfo,
    "inputs": inputs,
    "varinfo": varinfo,
    "outputs": [{"all": False}],
}


# Execute workflow and get results
reader = RedisEwoksEventReader(events_url)
future = send_task("ewoksbliss.apps.ewoks.execute_graph", args=args, kwargs=kwargs)
workflow_results = future.get(
    timeout=3
)  # events could be received in the mean time (see below)
assert workflow_results == {"return_value": 3}

# Get intermediate results from ewoks events
results_during_execution = list(reader.get_events(job_id=job_id))
assert len(results_during_execution) == 6  # start/stop for job, workflow and node

# Get start event of node "task1"
result_event = list(
    reader.get_events_with_variables(job_id=job_id, node_id="task1", type="start")
)
assert len(result_event) == 1
result_event = result_event[0]

# Get the value of the first output variable of "task1"
result = result_event["output_variables"]["return_value"]
assert result.value == 3

# Get access to all output variables of "task1"
results = result_event["outputs"]
assert results.variable_values["return_value"] == 3
