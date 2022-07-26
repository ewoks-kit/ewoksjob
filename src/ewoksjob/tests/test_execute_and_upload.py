import time
import pytest
from ewokscore.tests.examples.graphs import get_graph
from ..client import celery
from ..client import process
from .utils import get_result


def test_submit(ewoks_worker):
    assert_submit(celery)


def test_submit_local(local_ewoks_worker):
    assert_submit(process)


def assert_submit(mod):
    graph, expected = get_graph("acyclic1")
    expected = expected["task6"]
    kwargs = {
        "upload_kwargs": {
            "metadata_urls": list(),
            "beamline": "id00",
            "proposal": f"id00{time.strftime('%y%m')}",
            "dataset": "testdataset",
            "path": "/path/to/processed/dataset",
            "sample": "testsample",
            "raw": "/path/to/raw/dataset",
        }
    }
    future1 = mod.trigger_and_upload_workflow(args=(graph,), kwargs=kwargs)
    with pytest.raises(RuntimeError, match="requires pyicat-plus"):
        get_result(future1, timeout=3)
