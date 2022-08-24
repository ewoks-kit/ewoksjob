import os
from ewokscore import Task

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))


class SumTask(
    Task, input_names=["a"], optional_input_names=["b"], output_names=["result"]
):
    def run(self):
        result = self.inputs.a
        if self.inputs.b:
            result += self.inputs.b
        self.outputs.result = result


if __name__ == "__main__":
    from ewoksjob.client import submit

    os.environ["CELERY_LOADER"] = "ewoksjob.config.EwoksLoader"
    os.environ["CELERY_CONFIG_URI"] = os.path.join(SCRIPT_DIR, "celeryconfig.py")

    # Define a workflow with default inputs
    nodes = [
        {
            "id": "task1",
            "task_type": "class",
            "task_identifier": "hello_world.SumTask",
            "default_inputs": [{"name": "a", "value": 1}],
        },
        {
            "id": "task2",
            "task_type": "class",
            "task_identifier": "hello_world.SumTask",
            "default_inputs": [{"name": "b", "value": 1}],
        },
        {
            "id": "task3",
            "task_type": "class",
            "task_identifier": "hello_world.SumTask",
            "default_inputs": [{"name": "b", "value": 1}],
        },
    ]
    links = [
        {
            "source": "task1",
            "target": "task2",
            "data_mapping": [{"source_output": "result", "target_input": "a"}],
        },
        {
            "source": "task2",
            "target": "task3",
            "data_mapping": [{"source_output": "result", "target_input": "a"}],
        },
    ]
    workflow = {"graph": {"id": "testworkflow"}, "nodes": nodes, "links": links}

    # Define task inputs
    inputs = [{"id": "task1", "name": "a", "value": 10}]

    # Execute a workflow (use a proper Ewoks task scheduler in production)
    varinfo = {"root_uri": "/tmp/myresults"}  # optionally save all task outputs
    future = submit(args=(workflow,), kwargs={"varinfo": varinfo, "inputs": inputs})
    print(future.get(timeout=3))
