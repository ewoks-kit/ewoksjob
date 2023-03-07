import os
import pytest
from ..config import read_configuration

EXPECTED = {
    "broker_url": "redis://localhost:6379/3",
    "result_backend": "redis://localhost:6379/4",
    "result_serializer": "pickle",
    "accept_content": ["application/json", "application/x-python-serialize"],
    "result_expires": 600,
    "task_remote_tracebacks": True,
}


def test_pyfile_config(py_config: str):
    assert read_configuration(py_config) == EXPECTED
    assert read_configuration(f"file://{py_config}") == EXPECTED


def test_pymodule_config(py_config: str):
    keep = os.getcwd()
    module = os.path.splitext(os.path.basename(py_config))[0]
    os.chdir(os.path.dirname(py_config))
    try:
        assert read_configuration(module) == EXPECTED
    finally:
        os.chdir(keep)


def test_yaml_config(yaml_config: str):
    assert read_configuration(yaml_config) == EXPECTED
    assert read_configuration(f"file://{yaml_config}") == EXPECTED


def test_beacon_config(beacon_config: str):
    assert read_configuration(beacon_config) == EXPECTED


@pytest.fixture
def py_config(tmpdir) -> str:
    filename = str(tmpdir / "celeryconfig.py")
    lines = [
        "broker_url = 'redis://localhost:6379/3'\n",
        "result_backend = 'redis://localhost:6379/4'\n",
        "result_serializer = 'pickle'\n",
        "accept_content = ['application/json', 'application/x-python-serialize']\n",
        "result_expires = 600\n",
        "task_remote_tracebacks = True\n",
    ]
    with open(filename, "w") as f:
        f.writelines(lines)
    return filename


@pytest.fixture
def yaml_config(tmpdir) -> str:
    filename = str(tmpdir / "ewoks.yaml")
    lines = [
        "celery:\n",
        "  broker_url: 'redis://localhost:6379/3'\n",
        "  result_backend: 'redis://localhost:6379/4'\n",
        "  result_serializer: 'pickle'\n",
        "  accept_content: ['application/json', 'application/x-python-serialize']\n",
        "  result_expires: 600\n",
        "  task_remote_tracebacks: True\n",
    ]
    with open(filename, "w") as f:
        f.writelines(lines)
    return filename


@pytest.fixture
def beacon_config(mocker) -> str:
    url = "beacon://localhost:1234/config.yml"
    client = mocker.patch("ewoksjob.config.bliss_read_config")

    def read_config(_url):
        if _url == url:
            return EXPECTED

    client.side_effect = read_config
    return url
