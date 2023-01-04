import time
from ewoksjob.client import submit, CancelledErrors

# Define a workflow with default inputs
nodes = [
    {
        "id": "task1",
        "task_type": "method",
        "task_identifier": "time.sleep",
        "default_inputs": [{"name": 0, "value": 5}],
    },
    {
        "id": "task2",
        "task_type": "method",
        "task_identifier": "time.sleep",
        "default_inputs": [{"name": 0, "value": 0}],
    },
]
links = [{"source": "task1", "target": "task2"}]
workflow = {"graph": {"id": "testworkflow"}, "nodes": nodes, "links": links}

# Execute a workflow (use a proper Ewoks task scheduler in production)
future = submit(args=(workflow,))
time.sleep(1)

future.revoke(terminate=True)

try:
    future.get(timeout=5)
except CancelledErrors:
    pass
else:
    assert False, "Failed to cancel the job"
