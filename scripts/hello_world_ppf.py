import time

if True:
    from multiprocessing import get_context
    from multiprocessing import Value
    from multiprocessing import current_process
else:
    from billiard import get_context
    from billiard import Value
    from multiprocessing import current_process
from ewokscore import Task


def test_func(arg, sleep_time):
    if sleep_time:
        time.sleep(sleep_time)
    arg.value = 10


class TestTask(Task, optional_input_names=["sleep_time"], output_names=["result"]):
    def run(self):
        result = Value("i", 0)
        if current_process().daemon:
            print(
                "Task process is daemonic (cannot launch a subprocess unless using Billiard)"
            )
        else:
            print("Task process is non-daemonic (can launch a subprocess)")
        p = get_context().Process(
            target=test_func, args=(result, self.inputs.sleep_time)
        )
        p.start()
        p.join()
        self.outputs.result = result.value


if __name__ == "__main__":
    from ewoksjob.client import submit

    # Define a workflow with default inputs
    nodes = [
        {
            "id": "task1",
            "task_type": "class",
            "task_identifier": "hello_world_ppf.TestTask",
            "default_inputs": [{"name": "sleep_time", "value": 0}],
        },
    ]
    links = []
    workflow = {"graph": {"id": "testworkflow"}, "nodes": nodes, "links": links}

    # Define task inputs
    inputs = []

    # Execute a workflow (use a proper Ewoks task scheduler in production)
    varinfo = {}  # optionally save all task outputs

    future = submit(
        args=(workflow,),
        kwargs={"varinfo": varinfo, "inputs": inputs, "binding": "ppf"},
    )
    assert future.get(timeout=3) == {"result": 10}
