import json

import pytest
import yaml

from ..bindings import _has_subgraphs
from ..bindings import _read_local_file
from ..bindings import _resolve_on_client
from ..bindings import submit_graph

_GRAPH = {
    "graph": {"id": "max"},
    "nodes": [{"id": "max", "task_type": "method", "task_identifier": "builtins.max"}],
}

_GRAPH_WITH_SUBGRAPH = {
    "graph": {"id": "outer"},
    "nodes": [{"id": "sub", "task_type": "graph", "task_identifier": "graph.json"}],
}

_INPUTS = [{"id": "max", "name": 0, "value": 1}, {"id": "max", "name": 1, "value": 5}]


def _write_graph(directory, filename: str) -> None:
    with open(directory / filename, "w") as f:
        if filename.endswith(".json"):
            json.dump(_GRAPH, f)
        else:
            yaml.safe_dump(_GRAPH, f)


@pytest.mark.parametrize(
    "filename,representation",
    [("graph.json", "json_string"), ("graph.yml", "yaml_string")],
)
def test_read_local_file(tmp_path, filename, representation):
    _write_graph(tmp_path, filename)
    load_options = {"root_dir": str(tmp_path)}

    content, new_load_options = _read_local_file(filename, load_options)

    assert content == (tmp_path / filename).read_text()
    assert new_load_options == {**load_options, "representation": representation}


@pytest.mark.parametrize("graph", [_GRAPH, "demo", "missing.json"])
def test_read_local_file_unchanged(graph):
    load_options = {"representation": "test_core"}
    assert _read_local_file(graph, load_options) == (graph, load_options)


@pytest.mark.parametrize("filename", ["graph.json", "graph.yaml"])
def test_submit_graph_local_file(ewoks_worker, tmp_path, filename):
    _write_graph(tmp_path, filename)
    future = submit_graph(
        str(tmp_path / filename),
        inputs=_INPUTS,
        outputs=[{"all": True}],
        merge_outputs=True,
    )
    assert future.result(timeout=10) == {"return_value": 5}


def test_submit_graph_convert_graph_deprecated(ewoks_worker):
    with pytest.warns(DeprecationWarning):
        future = submit_graph(
            _GRAPH,
            _convert_graph=lambda graph, load_options: None,
            inputs=_INPUTS,
            outputs=[{"all": True}],
            merge_outputs=True,
        )
    assert future.result(timeout=10) == {"return_value": 5}


def test_resolve_on_client_inlines_subgraphs(tmp_path):
    _write_graph(tmp_path, "graph.json")
    with open(tmp_path / "outer.json", "w") as f:
        json.dump(_GRAPH_WITH_SUBGRAPH, f)

    graph, load_options = _resolve_on_client("outer.json", {"root_dir": str(tmp_path)})

    assert [node["task_type"] for node in graph["nodes"]] == ["method"]
    assert load_options is None


def test_resolve_on_client_worker_file():
    load_options = {"root_dir": "/only/on/the/worker"}
    assert _resolve_on_client("graph.json", load_options) == (
        "graph.json",
        load_options,
    )


@pytest.mark.parametrize(
    "graph,representation,expected",
    [
        (_GRAPH_WITH_SUBGRAPH, None, True),
        (json.dumps(_GRAPH_WITH_SUBGRAPH), "json_string", True),
        (yaml.safe_dump(_GRAPH_WITH_SUBGRAPH), "yaml_string", True),
        (_GRAPH, None, False),
        ("demo", None, False),
    ],
)
def test_has_subgraphs(graph, representation, expected):
    assert _has_subgraphs(graph, {"representation": representation}) is expected
