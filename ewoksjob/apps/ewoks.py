from functools import wraps
from typing import Dict, List, Union
import celery
import ewoks
from ewokscore import task_discovery
from .. import tasks
from ..config import configure_app

app = celery.Celery("ewoks")
configure_app(app)


def _add_job_id(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        execinfo = kwargs.setdefault("execinfo", dict())
        if "job_id" not in execinfo:
            execinfo["job_id"] = self.request.id
        return method(self, *args, **kwargs)

    return wrapper


@app.task(bind=True)
@_add_job_id
def execute_workflow(self, *args, **kwargs) -> Dict:
    return ewoks.execute_graph(*args, **kwargs)


@app.task()
def convert_workflow(*args, **kwargs) -> Union[str, dict]:
    return ewoks.convert_graph(*args, **kwargs)


@app.task(bind=True)
@_add_job_id
def convert_and_execute_workflow(self, *args, **kwargs) -> Dict:
    return tasks.convert_and_execute_graph(*args, **kwargs)


@app.task()
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return list(task_discovery.discover_tasks_from_modules(*args, **kwargs))
