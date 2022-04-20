import pytest
from ewoksjob.events.reader import RedisEwoksEventReader


@pytest.fixture()
def ewoksevents(redisdb):
    job_id = 1234
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"
    reader = RedisEwoksEventReader(url)

    execinfo = {
        "job_id": job_id,
        "handlers": [
            {
                "class": "ewoksjob.events.handlers.EwoksRedisEventHandler",
                "arguments": [{"name": "url", "value": url}],
            }
        ],
    }

    return reader, execinfo
