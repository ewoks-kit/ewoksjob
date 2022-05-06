import celery
import ewoks
from .config import configure_app

app = celery.Celery("ewoks")
configure_app(app)


@app.task(bind=True)
def execute_graph(self, *args, execinfo=None, **kwargs):
    if execinfo is None:
        execinfo = dict()
    if "job_id" not in execinfo:
        execinfo["job_id"] = self.request.id
    return ewoks.execute_graph(*args, execinfo=execinfo, **kwargs)
