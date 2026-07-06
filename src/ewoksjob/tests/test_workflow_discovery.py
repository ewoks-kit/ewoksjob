from ..client import celery
from ..client import local


def test_submit(ewoks_worker):
    expected = [
        "ewoksjob.tests._loadtest.graph",
        "ewoksjob.tests._loadtest.subgraph",
    ]
    assert_submit(celery, [])
    assert_submit(celery, expected, "ewoksjob.tests._loadt*.*")


def test_submit_local(local_ewoks_worker):
    expected = [
        "ewoksjob.tests._loadtest.graph",
        "ewoksjob.tests._loadtest.subgraph",
    ]
    assert_submit(local, [])
    assert_submit(local, expected, "ewoksjob.tests._loadt*.*")


def test_submit_local_patched(local_patched_ewoks_worker):
    expected = [
        "ewoksjob.tests._loadtest.graph",
        "ewoksjob.tests._loadtest.subgraph",
    ]

    assert_submit(local, expected)
    assert_submit(local, expected, "ewoksjob.tests._loadt*.*")


def assert_submit(mod, expected, *modules):
    if modules:
        future = mod.discover_workflows_from_modules(args=modules)
    else:
        future = mod.discover_all_workflows()

    results = future.result(timeout=60)

    if modules:
        assert set(results) == set(expected)
    else:
        assert set(expected).issubset(results), results
