import pytest
from ewokscore.tests.examples.graphs import get_graph
from ..apps import ewoks


@pytest.fixture(scope="module")
def celery_app(request):
    ewoks.app.conf.update(CELERY_ALWAYS_EAGER=True)
    return ewoks.app


def test_execute_graph(celery_app):
    graph, expected = get_graph("acyclic1")
    future = ewoks.execute_graph.delay(graph, results_of_all_nodes=True)
    results = {
        node_id: task.output_values for node_id, task in future.get(timeout=3).items()
    }
    assert results == expected
