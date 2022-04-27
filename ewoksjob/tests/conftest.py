import pytest
from ewoksjob.events.readers import instantiate_reader


@pytest.fixture(scope="session")
def celery_config(tmpdir_factory):
    tmpdir = tmpdir_factory.mktemp("celery")
    return {
        "broker_url": "memory://",
        # "broker_url": f"sqla+sqlite:///{tmpdir / 'celery.db'}",
        "result_backend": f"db+sqlite:///{tmpdir / 'celery_results.db'}",
        "result_serializer": "pickle",
        "accept_content": ["application/json", "application/x-python-serialize"],
    }


@pytest.fixture(scope="session")
def celery_includes():
    return ("ewoksjob.apps.ewoks",)


@pytest.fixture()
def sqlite3_ewoks_events(tmpdir):
    uri = f"file:{tmpdir / 'ewoks_events.db'}"
    handlers = [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]
    reader = instantiate_reader(uri)
    return handlers, reader


@pytest.fixture()
def redis_ewoks_events(redisdb):
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [{"name": "url", "value": url}],
        }
    ]
    reader = instantiate_reader(url)
    return handlers, reader
