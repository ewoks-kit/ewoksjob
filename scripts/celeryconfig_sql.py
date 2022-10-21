# Does not support task monitoring or cancelling
import os

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
_DATA_DIR = os.path.join(_SCRIPT_DIR, "results", "celery")
os.makedirs(_DATA_DIR, exist_ok=True)
broker_url = f"sqla+sqlite:///{os.path.join(_DATA_DIR, 'celery.db')}"
result_backend = f"db+sqlite:///{os.path.join(_DATA_DIR ,'celery_results.db')}"

result_serializer = "pickle"
accept_content = ["application/json", "application/x-python-serialize"]
result_expires = 600
