import pytest
from ewokscore.tests.examples.graphs import get_graph
from ..apps import ewoks
from ..server import workflow_worker_pool
from ..client import submit_local, get_local_future


@pytest.fixture(scope="module")
def celery_app():
    ewoks.app.conf.update(CELERY_ALWAYS_EAGER=True)
    yield
    ewoks.app.conf.update(CELERY_ALWAYS_EAGER=False)


def test_submit(celery_app):
    # TODO: test `submit` directly
    graph, expected = get_graph("acyclic1")
    future = ewoks.execute_graph.delay(graph, results_of_all_nodes=True)
    results = {
        node_id: task.output_values for node_id, task in future.get(timeout=3).items()
    }
    assert results == expected


def test_submit_local():
    with workflow_worker_pool():
        graph, expected = get_graph("acyclic1")
        expected = expected["task6"]
        future = submit_local(graph, outputs=[{"all": False}])
        assert get_local_future(future.job_id) is future
        results = future.result(timeout=3)
        assert results == expected
