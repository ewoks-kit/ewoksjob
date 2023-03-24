import gc
import os
import pytest

from ewokscore import events
from ewokscore.events import cleanup
from ewoksjob.events.readers import instantiate_reader
from ewoksjob.worker import options as worker_options

from .utils import has_redis_server
from ..client import local

try:
    from pyslurmutils.tests.conftest import slurm_data_directory  # noqa F401
    from pyslurmutils.tests.conftest import slurm_log_directory  # noqa F401
    from pyslurmutils.tests.conftest import data_directory  # noqa F401
    from pyslurmutils.tests.conftest import log_directory  # noqa F401
    from pyslurmutils.tests.conftest import slurm_env  # noqa F401
    from pyslurmutils.tests.conftest import slurm_config
except ImportError:

    @pytest.fixture(scope="session")
    def slurm_config() -> None:
        pytest.skip("requires pyslurmutils")


if has_redis_server():
    import redis

    @pytest.fixture(scope="session")
    def celery_config(redis_proc):
        url = f"redis://{redis_proc.host}:{redis_proc.port}"
        # celery -A ewoksjob.apps.ewoks --broker={url}/0 --result-backend={url}/1 inspect stats -t 5
        return {
            "broker_url": f"{url}/0",
            "result_backend": f"{url}/1",
            "result_serializer": "pickle",
            "accept_content": ["application/json", "application/x-python-serialize"],
            "task_remote_tracebacks": True,
        }

else:

    @pytest.fixture(scope="session")
    def celery_config(tmpdir_factory):
        tmpdir = tmpdir_factory.mktemp("celery")
        return {
            "broker_url": "memory://",
            # "broker_url": f"sqla+sqlite:///{tmpdir / 'celery.db'}",
            "result_backend": f"db+sqlite:///{tmpdir / 'celery_results.db'}",
            "result_serializer": "pickle",
            "accept_content": ["application/json", "application/x-python-serialize"],
            "task_remote_tracebacks": True,
        }


@pytest.fixture(scope="session")
def celery_includes():
    return ("ewoksjob.apps.ewoks",)


@pytest.fixture(scope="session")
def celery_worker_parameters(slurm_config):
    if _use_slurm_pool():
        rmap = {v: k for k, v in worker_options.SLURM_NAME_MAP.items()}
        options = {rmap[k]: v for k, v in slurm_config.items()}
        worker_options.apply_worker_options(options)
    return {"loglevel": "debug"}


@pytest.fixture(scope="session")
def celery_worker_pool():
    if os.name == "nt":
        # "prefork" nor "process" works on windows
        return "solo"
    elif _use_slurm_pool():
        return "slurm"
    else:
        return "process"


def _use_slurm_pool() -> bool:
    return gevent_patched()


def gevent_patched() -> bool:
    try:
        from gevent.monkey import is_anything_patched
    except ImportError:
        return False

    return is_anything_patched()


@pytest.fixture()
def skip_if_gevent():
    if gevent_patched():
        pytest.skip("not supported with gevent yet")


@pytest.fixture()
def ewoks_worker(celery_session_worker, celery_worker_pool):
    yield celery_session_worker
    if celery_worker_pool == "solo":
        events.cleanup()


@pytest.fixture(scope="session")
def local_ewoks_worker(slurm_config):
    kw = {"max_workers": 8}
    if _use_slurm_pool():
        pool_type = "slurm"
        kw.update(slurm_config)
    else:
        pool_type = None
    with local.pool_context(pool_type=pool_type, **kw) as pool:
        yield
        while gc.collect():
            pass
        assert len(pool._tasks) == 0


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
    yield handlers, reader
    reader.close()
    cleanup()


@pytest.fixture()
def redis_ewoks_events(redisdb):
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"
    handlers = [
        {
            "class": "ewoksjob.events.handlers.RedisEwoksEventHandler",
            "arguments": [
                {"name": "url", "value": url},
                {"name": "ttl", "value": 3600},
            ],
        }
    ]
    reader = instantiate_reader(url)
    yield handlers, reader

    connection = redis.Redis.from_url(url)
    for key in connection.keys("ewoks:*"):
        assert connection.ttl(key) >= 0, key

    reader.close()
    cleanup()
