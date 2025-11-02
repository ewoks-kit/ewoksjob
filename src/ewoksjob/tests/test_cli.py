import re
import sys

import click.testing
import pytest

from ..cli_utils.cancel import cancel
from ..cli_utils.submit import submit
from ..client import CancelledError
from ..client import get_future
from .conftest import gevent_patched


def test_submit(ewoks_worker) -> str:
    runner = click.testing.CliRunner()

    argv = ["demo", "--test", "--wait", "60"]
    result = runner.invoke(submit, argv)
    if result.exception:
        raise result.exception

    match = re.search(r"ID:\s*([0-9a-fA-F-]+)", result.stdout)
    if not match:
        raise ValueError("ewoks submit has unexpected output:\n{result.stdout}")
    job_id = match.group(1) if match else result.stdout.strip()
    future = get_future(job_id)
    assert future.done()


def test_submit_exit_code(ewoks_worker) -> str:
    runner = click.testing.CliRunner()

    argv = ["demo", "--test", "--wait", "60"]
    result = runner.invoke(submit, argv)
    assert result.exit_code == 0, result.stdout

    argv = ["demo", "--test", "--wait", "60", "-p", "a='wrong_type'"]
    result = runner.invoke(submit, argv)
    assert result.exit_code == 1, result.stdout


@pytest.mark.skipif(
    sys.platform == "win32", reason="Cancelling a Celery job on Windows does not work"
)
def test_cancel(ewoks_worker) -> str:
    if gevent_patched() and ewoks_worker.app.conf.broker_url.startswith("redis://"):
        # Only fails in combination with other tests
        pytest.skip("fails with the Redis broker and gevent patching")
    runner = click.testing.CliRunner()

    argv = ["demo", "--test", "-p", "delay=100"]
    result = runner.invoke(submit, argv)
    if result.exception:
        raise result.exception

    match = re.search(r"ID:\s*([0-9a-fA-F-]+)", result.stdout)
    if not match:
        raise ValueError("ewoks submit has unexpected output:\n{result.stdout}")
    job_id = match.group(1) if match else result.stdout.strip()
    future = get_future(job_id)
    assert not future.done()

    argv = [job_id]
    result = runner.invoke(cancel, argv)
    if result.exception:
        raise result.exception

    with pytest.raises(CancelledError):
        _ = future.result(timeout=20)
    assert future.aborted()
