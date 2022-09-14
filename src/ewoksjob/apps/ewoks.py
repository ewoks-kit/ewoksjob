import sys
from functools import wraps
from typing import Dict, List, Union

import celery
import ewoks

from .. import tasks
from ..worker.preload import add_workers
from ..worker.submit import submit

app = celery.Celery("ewoks")
add_workers(app)


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
def execute_workflow(self, *args, **kwargs) -> Dict:
    return submit(ewoks.execute_graph, *args, **kwargs)


@app.task()
@_allow_cwd_imports
def convert_workflow(*args, **kwargs) -> Union[str, dict]:
    return submit(ewoks.convert_graph, *args, **kwargs)


@app.task(bind=True)
@_ensure_ewoks_job_id
@_allow_cwd_imports
def convert_and_execute_workflow(self, *args, **kwargs) -> Dict:
    return submit(tasks.convert_and_execute_graph, *args, **kwargs)


@app.task(bind=True)
@_ensure_ewoks_job_id
@_allow_cwd_imports
def execute_and_upload_workflow(self, *args, **kwargs) -> Dict:
    return submit(tasks.execute_and_upload_graph, *args, **kwargs)


@app.task()
@_allow_cwd_imports
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return submit(tasks.discover_tasks_from_modules, *args, **kwargs)
