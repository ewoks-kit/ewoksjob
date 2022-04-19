import os
from celery import Celery
from ewoks import execute_graph as _execute_graph


app = Celery("ewoks")
if os.environ.get("CELERY_CONFIG_MODULE"):
    app.config_from_envvar("CELERY_CONFIG_MODULE", force=True)


@app.task
def execute_graph(*args, **kwargs):
    return _execute_graph(*args, **kwargs)
