from ewoks import execute_graph
from ewokscore.tests.examples.graphs import get_graph


def test_redis_event_handler(ewoksevents):
    reader, execinfo = ewoksevents
    execinfo["job_id"] = job_id = 1234

    graph, _ = get_graph("acyclic1")
    execute_graph(graph, execinfo=execinfo)

    events = {
        (event["job_id"], event["workflow_id"], event["node_id"], event["type"])
        for event in reader.get_events(job_id=job_id)
    }

    expected = {
        (1234, None, None, "start"),
        (1234, "acyclic1", None, "start"),
        (1234, "acyclic1", None, "end"),
        (1234, None, None, "end"),
    }
    expected |= {(1234, "acyclic1", f"task{i}", "start") for i in range(1, 7)}
    expected |= {(1234, "acyclic1", f"task{i}", "end") for i in range(1, 7)}

    assert events == expected
