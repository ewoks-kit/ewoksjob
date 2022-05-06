import os
import celery
import ewoks


app = celery.Celery("ewoks")

# Celery does this automatically on the client side but not on the worker side:
_module = os.environ.get("CELERY_CONFIG_MODULE")
if _module:
    app.config_from_envvar("CELERY_CONFIG_MODULE", force=True)
else:
    app.config_from_object("celeryconfig", force=True, silent=True)


@app.task(bind=True)
def execute_graph(self, *args, execinfo=None, **kwargs):
    if execinfo is None:
        execinfo = dict()
    if "job_id" not in execinfo:
        execinfo["job_id"] = self.request.id
    return ewoks.execute_graph(*args, execinfo=execinfo, **kwargs)
