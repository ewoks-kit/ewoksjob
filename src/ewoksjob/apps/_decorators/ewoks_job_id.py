from functools import wraps
from typing import Callable


def ensure_ewoks_job_id(celery_task: Callable) -> Callable:
    """Use celery task ID as ewoks job ID when ewoks job ID is not provided"""

    @wraps(celery_task)
    def new_celery_task(self, *args, **kwargs):
        execinfo = kwargs.setdefault("execinfo", dict())
        if not execinfo.get("job_id"):
            execinfo["job_id"] = self.request.id
        return celery_task(self, *args, **kwargs)

    return new_celery_task
