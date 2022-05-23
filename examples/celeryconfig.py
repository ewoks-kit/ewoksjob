if False:
    # Redis backend
    broker_url = "redis://localhost:6379/3"
    result_backend = "redis://localhost:6379/4"
else:
    # SQLite backend (does not support task monitoring or cancelling)
    import os

    SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(SCRIPT_DIR, "results")
    os.makedirs(DATA_DIR, exist_ok=True)
    broker_url = f"sqla+sqlite:///{os.path.join(DATA_DIR, 'celery.db')}"
    result_backend = f"db+sqlite:///{os.path.join(DATA_DIR ,'celery_results.db')}"

result_serializer = "pickle"
accept_content = ["application/json", "application/x-python-serialize"]
