import gc
import os

import pytest
import socket
import traceback
from ewokscore import events
from ewoksjob.events.readers import read_ewoks_events
from ewoksjob.worker import options as worker_options

from .utils import has_redis
from ..client import local

_SOCKETS = []


@pytest.fixture(autouse=True, scope="session")
def track_socket_creation():
    yield
    return
    original_socket = socket.socket

    def tracked_socket(*args, **kwargs):
        sock = original_socket(*args, **kwargs)
        s = "".join(traceback.format_stack(limit=20))
        _SOCKETS.append(f"\n[Tracked Socket Created] {sock}:\n{s}")
        return sock

    socket.socket = tracked_socket
    yield
    socket.socket = original_socket


if has_redis():
    import redis

    @pytest.fixture(scope="session")
    def celery_config(redis_proc):
        url = f"redis://{redis_proc.host}:{redis_proc.port}"
        # celery -A ewoksjob.apps.ewoks --broker={url}/0 --result-backend={url}/1 inspect stats -t 5
        yield {
            "broker_url": f"{url}/0",
            "result_backend": f"{url}/1",
            "result_serializer": "pickle",
            "accept_content": ["application/json", "application/x-python-serialize"],
            "task_remote_tracebacks": True,
            "enable_utc": False,
        }
        # _wait_asyncresults_destroyed()

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
            "enable_utc": False,
        }


@pytest.fixture(scope="session")
def celery_includes():
    return ("ewoksjob.apps.ewoks",)


@pytest.fixture(scope="session")
def celery_worker_parameters(slurm_client_kwargs):
    if _use_slurm_pool():
        rmap = {v: k for k, v in worker_options.SLURM_NAME_MAP.items()}
        options = {rmap[k]: v for k, v in slurm_client_kwargs.items() if k in rmap}
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


def debug_asyncresults_on_teardown():
    import objgraph
    from celery.result import AsyncResult

    async_results = [obj for obj in gc.get_objects() if isinstance(obj, AsyncResult)]

    if not async_results:
        return

    output_dir = "asyncresult_graphs"
    os.makedirs(output_dir, exist_ok=True)

    for i, target in enumerate(async_results, 1):
        filename = os.path.join(output_dir, f"asyncresult_{i}.png")
        print(f"[leak debug] Saving backrefs graph: {filename}")
        try:
            objgraph.show_backrefs(
                [target], filename=filename, max_depth=5, too_many=10
            )
        except Exception as e:
            print(f"[error] Could not generate graph for AsyncResult #{i}: {e}")


def _wait_asyncresults_destroyed():
    # Garbage collection of `AsyncResult` tries to connect to
    # Redis to unsubscribe. When the Redis server is down,
    # `AsyncResult.__del__` will raise
    #
    #   redis.exceptions.ConnectionError: Connection refused
    #
    # So make sure all `AsyncResult` instances are garbage collected
    # before the Redis server gets shut down by exiting fixture `redis_proc`.
    try:
        while gc.collect():
            pass
    finally:
        print("_SOCKETS")
        for s in _SOCKETS:
            print(s)
    # debug_asyncresults_on_teardown()


def _todo_cleanup(app):
    # Close all Redis connections to avoid garbage collection
    # of unclosed sockets which gives a ResourceWarning and
    # with "-W error" pytest fails.
    _wait_asyncresults_destroyed()
    result_consumer = app.backend.result_consumer
    for mapping in result_consumer._pending_results:
        print("PENDING RESULTS", mapping)
    # app.backend.client.connection_pool.reset()


@pytest.fixture(scope="session")
def ewoks_session_worker(celery_session_worker, celery_session_app):
    yield celery_session_worker
    _todo_cleanup(celery_session_app)


@pytest.fixture()
def ewoks_worker(ewoks_session_worker, celery_worker_pool):
    yield ewoks_session_worker
    if celery_worker_pool == "solo":
        events.cleanup()


@pytest.fixture(scope="session")
def local_ewoks_worker(slurm_client_kwargs):
    kw = {"max_workers": 8}
    if _use_slurm_pool():
        pool_type = "slurm"
        kw.update(slurm_client_kwargs)
    else:
        pool_type = None
    with local.pool_context(pool_type=pool_type, **kw) as pool:
        yield

        if pool_type != "slurm":
            # TODO: Fails with Slurm for one test specifically:
            #       test_task_discovery.py::test_submit_local with slurm

            while gc.collect():
                pass

            assert len(pool._tasks) == 0, str(list(pool._tasks.values()))


@pytest.fixture()
def sqlite3_ewoks_events(tmp_path):
    uri = f"file:{tmp_path / 'ewoks_events.db'}"
    handlers = [
        {
            "class": "ewokscore.events.handlers.Sqlite3EwoksEventHandler",
            "arguments": [{"name": "uri", "value": uri}],
        }
    ]
    with read_ewoks_events(uri) as reader:
        yield handlers, reader
        events.cleanup()


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
    with read_ewoks_events(url) as reader:
        yield handlers, reader

        connection = redis.Redis.from_url(url)
        for key in connection.keys("ewoks:*"):
            assert connection.ttl(key) >= 0, key

        events.cleanup()
