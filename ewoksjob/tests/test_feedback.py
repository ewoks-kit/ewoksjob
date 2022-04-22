import pytest
from ewokscore import Task
from ewokscore.utils import qualname
from ewoks import execute_graph
from .utils import has_redis_server


class AddNumbers(Task, input_names=["a", "b"], output_names=["sum"]):
    def run(self):
        self.outputs.sum = self.inputs.a + self.inputs.b


def generate_graph():
    return {
        "graph": {"id": "test"},
        "nodes": [
            {
                "id": "task",
                "task_identifier": qualname(AddNumbers),
                "task_type": "class",
            }
        ],
    }


@pytest.mark.skipif(not has_redis_server(), reason="redis-server not installed")
@pytest.mark.parametrize("scheme", ("nexus", "json"))
def test_redis(scheme, redis_ewoks_events, tmpdir):
    handlers, reader = redis_ewoks_events
    assert_feedback(scheme, handlers, reader, tmpdir)


def assert_feedback(scheme, handlers, reader, tmpdir):
    execinfo = {"handlers": handlers}
    graph = generate_graph()

    result = execute_graph(
        graph,
        execinfo=execinfo,
        varinfo={"root_uri": str(tmpdir), "scheme": scheme},
        inputs=[
            {"id": "task", "name": "a", "value": 1},
            {"id": "task", "name": "b", "value": 2},
        ],
        outputs=[{"id": "task", "name": "sum"}],
    )
    assert result == {"sum": 3}

    result_event = list(reader.get_events_with_variables(node_id="task", type="start"))
    assert len(result_event) == 1

    results = result_event[0]["outputs"]
    assert results.variable_values == {"sum": 3}
