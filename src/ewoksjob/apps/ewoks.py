"""Celery ewoks application executed on the worker side."""

from typing import Dict
from typing import List
from typing import Union

import celery

from ..worker.options import add_options
from ._decorators import ewoks_config
from ._decorators import ewoks_job_id
from ._decorators import ewoks_tasks

app = celery.Celery("ewoks")
add_options(app)


@app.task(bind=True)
@ewoks_job_id.ensure_ewoks_job_id
@ewoks_config.merge_execute_arguments
@ewoks_tasks.ewoks_task
def execute_graph(self, *args, **kwargs) -> Dict:
    return ewoks_tasks.get_native_ewoks_task("execute_graph")(*args, **kwargs)


@app.task(bind=False)
@ewoks_tasks.ewoks_task
def convert_graph(*args, **kwargs) -> Union[str, dict]:
    return ewoks_tasks.get_native_ewoks_task("convert_graph")(*args, **kwargs)


@app.task(bind=False)
@ewoks_tasks.ewoks_task
def discover_tasks_from_modules(*args, **kwargs) -> List[dict]:
    return ewoks_tasks.get_native_ewoks_task("discover_tasks_from_modules")(
        *args, **kwargs
    )


@app.task(bind=False)
@ewoks_tasks.ewoks_task
def discover_all_tasks(*args, **kwargs) -> List[dict]:
    return ewoks_tasks.get_native_ewoks_task("discover_all_tasks")(*args, **kwargs)
