import pytest
from ewokscore.tests.test_events import assert_event_reader
from .utils import has_redis_server


@pytest.mark.skipif(not has_redis_server(), reason="redis-server not installed")
def test_redis(redis_ewoks_events):
    handlers, reader = redis_ewoks_events
    assert_event_reader(handlers, reader)
