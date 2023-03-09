import sys
from functools import wraps
from typing import Dict, List, Union

import celery

from .. import tasks
from ..worker.options import add_options
from ..worker.task import worker_task

app = celery.Celery("ewoks")
add_options(app)


def _ensure_ewoks_job_id(method):
    """Use celery task ID as ewoks job ID when not ewoks job ID is provided"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        execinfo = kwargs.setdefault("execinfo", dict())
        if not execinfo.get("job_id"):
            execinfo["job_id"] = self.request.id
        return method(self, *args, **kwargs)

    return wrapper


def _allow_cwd_imports(method):
    """Allows import from the current working directory"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if "" not in sys.path:
            sys.path.append("")
        return method(self, *args, **kwargs)

    return wrapper


@app.task(bind=True)
@_ensure_ewoks_job_id
@_allow_cwd_imports
@worker_task
def execute_graph(self, *args, **kwargs) -> Dict:
    return tasks.execute_graph(*args, **kwargs)


@app.task()
@_allow_cwd_imports
@worker_task
def convert_graph(*args, **kwargs) -> Union[str, dict]:
    return tasks.convert_graph(*args, **kwargs)


@app.task()
@_allow_cwd_imports
@worker_task
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return tasks.discover_tasks_from_modules(*args, **kwargs)
