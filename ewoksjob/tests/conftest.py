import pytest
from ewoksjob.events.readers import RedisEwoksEventReader


@pytest.fixture()
def redis_ewoks_events(redisdb):
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [{"name": "url", "value": url}],
        }
    ]
    reader = RedisEwoksEventReader(url)
    return handlers, reader
