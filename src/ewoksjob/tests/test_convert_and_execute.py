from ewokscore.tests.examples.graphs import get_graph
from ..client import celery
from ..client import local


def test_submit(ewoks_worker, tmpdir):
    assert_submit(celery, tmpdir)
    assert_submit_test(celery, tmpdir)


def test_submit_local(local_ewoks_worker, tmpdir):
    assert_submit(local, tmpdir)
    assert_submit_test(local, tmpdir)


def assert_submit(mod, tmpdir):
    graph, expected = get_graph("acyclic1")
    expected = expected["task6"]
    filename = tmpdir / "test.json"
    args = (graph,)
    kwargs = {"save_options": {"indent": 2}, "convert_destination": str(filename)}
    future1 = mod.submit(args=args, kwargs=kwargs)
    future2 = mod.get_future(future1.uuid)
    results = future1.result(timeout=60)
    assert results == expected
    results = future2.result(timeout=0)
    assert results == expected
    assert filename.exists()


def assert_submit_test(mod, tmpdir):
    filename = tmpdir / "test.json"
    kwargs = {"save_options": {"indent": 2}, "convert_destination": str(filename)}
    future1 = mod.submit_test(kwargs=kwargs)
    future2 = mod.get_future(future1.uuid)
    results = future1.result(timeout=60)
    assert results == {"return_value": True}
    results = future2.result(timeout=0)
    assert results == {"return_value": True}
    assert filename.exists()
