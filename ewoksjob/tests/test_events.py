from ewokscore.tests.test_events import assert_event_reader


def test_redis(redis_ewoks_events):
    handlers, reader = redis_ewoks_events
    assert_event_reader(handlers, reader)
