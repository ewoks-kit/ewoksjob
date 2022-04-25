import pytest
from ewoksjob.events.readers import instantiate_reader


@pytest.fixture()
def redis_ewoks_events(redisdb):
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [{"name": "url", "value": url}],
        }
    ]
    reader = instantiate_reader("ewoksjob.events.readers.RedisEwoksEventReader", url)
    return handlers, reader


@pytest.fixture()
def sqlite3_ewoks_events(tmpdir):
    uri = f"file:{tmpdir / 'ewoks_events.db'}"
    handlers = [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]
    reader = instantiate_reader("ewoksjob.events.readers.Sqlite3EwoksEventReader", uri)
    return handlers, reader
