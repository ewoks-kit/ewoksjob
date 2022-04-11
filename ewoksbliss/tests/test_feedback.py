from ewokscore import Task
from ewokscore.variable import Variable, VariableContainer
from ewokscore.utils import qualname
from ewoks import execute_graph


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


def test_redis_feedback(ewoksevents, tmpdir):
    reader, execinfo = ewoksevents
    graph = generate_graph()

    result = execute_graph(
        graph,
        execinfo=execinfo,
        varinfo={"root_uri": str(tmpdir)},
        inputs=[
            {"id": "task", "name": "a", "value": 1},
            {"id": "task", "name": "b", "value": 2},
        ],
        outputs=[{"id": "task", "name": "sum"}],
    )
    assert result == {"sum": 3}

    result_event = list(reader.get_events(node_id="task", type="start"))
    assert len(result_event) == 1

    assert len(result_event[0]["output_uris"]) == 1
    result = Variable(data_uri=result_event[0]["output_uris"][0]["value"])
    assert result.value == 3

    results = VariableContainer(data_uri=result_event[0]["task_uri"])
    assert results.variable_values == {"sum": 3}
