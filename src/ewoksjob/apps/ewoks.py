import sys
from functools import wraps
from typing import Dict, List, Union
import celery
import ewoks
from ewokscore import task_discovery
from .. import tasks

app = celery.Celery("ewoks")


def _add_job_id(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        execinfo = kwargs.setdefault("execinfo", dict())
        if "job_id" not in execinfo:
            execinfo["job_id"] = self.request.id
        return method(self, *args, **kwargs)

    return wrapper


def _add_working_directory(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if "" not in sys.path:
            sys.path.append("")
        return method(self, *args, **kwargs)

    return wrapper


@app.task(bind=True)
@_add_job_id
@_add_working_directory
def execute_workflow(self, *args, **kwargs) -> Dict:
    return ewoks.execute_graph(*args, **kwargs)


@app.task()
@_add_working_directory
def convert_workflow(*args, **kwargs) -> Union[str, dict]:
    return ewoks.convert_graph(*args, **kwargs)


@app.task(bind=True)
@_add_job_id
@_add_working_directory
def convert_and_execute_workflow(self, *args, **kwargs) -> Dict:
    return tasks.convert_and_execute_graph(*args, **kwargs)


@app.task(bind=True)
@_add_job_id
@_add_working_directory
def execute_and_upload_workflow(self, *args, **kwargs) -> Dict:
    return tasks.execute_and_upload_graph(*args, **kwargs)


@app.task()
@_add_working_directory
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return list(task_discovery.discover_tasks_from_modules(*args, **kwargs))
