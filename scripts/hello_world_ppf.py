import time

if True:
    from multiprocessing import get_context
    from multiprocessing.pool import Pool
    from multiprocessing import current_process

    pool_type = "process"
else:
    from billiard import get_context
    from billiard.pool import Pool
    from billiard import current_process

    pool_type = "billiard"
from ewokscore import Task


def test_func(sleep_time):
    time.sleep(sleep_time)
    return 10


class TestTask(Task, optional_input_names=["sleep_time"], output_names=["result"]):
    def run(self):
        if current_process().daemon:
            print(
                "Task process is daemonic (cannot launch a subprocess unless using Billiard)"
            )
        else:
            print("Task process is non-daemonic (can launch a subprocess)")
        with Pool(processes=1, context=get_context()) as pool:
            sleep_time = self.get_input_value("sleep_time", 0)
            self.outputs.result = pool.apply(test_func, args=(sleep_time,))


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
        {
            "id": "task2",
            "task_type": "class",
            "task_identifier": "hello_world_ppf.TestTask",
            "default_inputs": [{"name": "sleep_time", "value": 0}],
        },
    ]
    links = [
        {
            "source": "task1",
            "target": "task2",
        },
    ]
    workflow = {"graph": {"id": "testworkflow"}, "nodes": nodes, "links": links}

    # Define task inputs
    inputs = []

    # Execute a workflow (use a proper Ewoks task scheduler in production)
    varinfo = {}  # optionally save all task outputs

    future = submit(
        args=(workflow,),
        kwargs={
            "varinfo": varinfo,
            "inputs": inputs,
            "outputs": [{"all": True}],
            "merge_outputs": True,
            "engine": "ppf",
            "pool_type": pool_type,
            "scaling_workers": True,
            "max_workers": 5,  # when scaling_workers=False
        },
    )
    result = future.get(timeout=3)
    assert result == {"result": 10}, result
