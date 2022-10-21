from ewoksjob.client import submit

# Define a workflow with default inputs
nodes = [
    {
        "id": "task1",
        "task_type": "method",
        "task_identifier": "time.sleep",
        "default_inputs": [{"name": 0, "value": 0}],
    },
    {
        "id": "task2",
        "task_type": "method",
        "task_identifier": "time.sleep",
        "default_inputs": [{"name": 0, "value": "fail"}],
    },
]
links = [{"source": "task1", "target": "task2"}]
workflow = {"graph": {"id": "testworkflow"}, "nodes": nodes, "links": links}

# Execute a workflow (use a proper Ewoks task scheduler in production)
future = submit(args=(workflow,))
try:
    future.get(timeout=5)
except RuntimeError as e:
    assert str(e) == "Task 'task2' failed"
else:
    assert False, "Job did not fail"
