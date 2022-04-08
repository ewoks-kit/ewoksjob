from ewoks import execute_graph
from ewokscore.tests.examples.graphs import get_graph
from ewoksbliss.events.reader import RedisEwoksEventReader


def test_redis_event_handler(redisdb):
    job_id = "1234"
    url = f"unix://{redisdb.connection_pool.connection_kwargs['path']}"

    execinfo = {
        "job_id": job_id,
        "handlers": [
            {
                "class": "ewoksbliss.events.handlers.EwoksRedisEventHandler",
                "arguments": [{"name": "url", "value": url}],
            }
        ],
    }

    graph, _ = get_graph("acyclic1")
    execute_graph(graph, execinfo=execinfo)

    reader = RedisEwoksEventReader(url)

    events = {
        (event["job_id"], event["workflow_id"], event["node_id"], event["type"])
        for event in reader.get_job_events(job_id)
    }

    expected = {
        ("1234", None, None, "start"),
        ("1234", "acyclic1", None, "start"),
        ("1234", "acyclic1", None, "end"),
        ("1234", None, None, "end"),
    }
    expected |= {("1234", "acyclic1", f"task{i}", "start") for i in range(1, 7)}
    expected |= {("1234", "acyclic1", f"task{i}", "end") for i in range(1, 7)}

    assert events == expected
