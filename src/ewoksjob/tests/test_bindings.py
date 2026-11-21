import json
from copy import deepcopy

import pytest

from ..bindings import _load_graph
from ..bindings import submit_graph

_GRAPH = {
    "graph": {"id": "max"},
    "nodes": [{"id": "max", "task_type": "method", "task_identifier": "builtins.max"}],
}


@pytest.mark.parametrize("source", ["dict", "file"])
def test_load_graph(tmp_path, source):
    if source == "dict":
        graph = deepcopy(_GRAPH)
    else:
        graph = str(tmp_path / "graph.json")
        with open(graph, "w") as f:
            json.dump(_GRAPH, f)
    graph = _load_graph(graph, load_options={"root_dir": str(tmp_path)})
    assert graph["graph"]["id"] == "max"


def test_submit_graph_convert_graph(ewoks_worker):
    future = submit_graph(
        "max",
        _convert_graph=lambda graph, load_options: _GRAPH,
        inputs=[
            {"id": "max", "name": 0, "value": 1},
            {"id": "max", "name": 1, "value": 5},
        ],
        outputs=[{"all": True}],
        merge_outputs=True,
    )
    assert future.result(timeout=10) == {"return_value": 5}
