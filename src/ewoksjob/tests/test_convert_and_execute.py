from ewokscore.tests.examples.graphs import get_graph
from ..client import celery
from ..client import local
from .utils import get_result


def test_submit(ewoks_worker, tmpdir):
    assert_submit(celery, tmpdir)
    assert_submit_test(celery, tmpdir)


def test_submit_local(local_ewoks_worker, tmpdir):
    assert_submit(local, tmpdir)
    assert_submit_test(local, tmpdir)


def test_submit_local_slurm(local_slurm_ewoks_worker, tmpdir):
    assert_submit(local, tmpdir)
    assert_submit_test(local, tmpdir)


def assert_submit(mod, tmpdir):
    graph, expected = get_graph("acyclic1")
    expected = expected["task6"]
    filename = tmpdir / "test.json"
    args = (graph,)
    kwargs = {"save_options": {"indent": 2}, "convert_destination": str(filename)}
    future1 = mod.submit(args=args, kwargs=kwargs)
    future2 = mod.get_future(future1.task_id)
    results = get_result(future1, timeout=3)
    assert results == expected
    results = get_result(future2, timeout=0)
    assert results == expected
    assert filename.exists()


def assert_submit_test(mod, tmpdir):
    filename = tmpdir / "test.json"
    kwargs = {"save_options": {"indent": 2}, "convert_destination": str(filename)}
    future1 = mod.submit_test(kwargs=kwargs)
    future2 = mod.get_future(future1.task_id)
    results = get_result(future1, timeout=3)
    assert results == {"return_value": True}
    results = get_result(future2, timeout=0)
    assert results == {"return_value": True}
    assert filename.exists()
