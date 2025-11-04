from argparse import Namespace
from typing import Literal
from typing import Optional

import click
from ewoksutils.cli_utils import cli_cancel_utils
from ewoksutils.cli_utils.cli_click import add_click_options

from .. import client


@click.command("cancel")
@add_click_options(cli_cancel_utils.cancel_arguments(shell=True))
def cancel(cli_args: Namespace) -> Optional[Literal[0, 1]]:
    """Abort an Ewoks job."""
    result = command_cancel(cli_args, shell=True)
    if result:
        click.get_current_context().exit(result)


def command_cancel(cli_args, shell: bool = False) -> Optional[Literal[0, 1]]:
    for job_id in cli_args.job_ids:
        print(f"Cancel Job {job_id!r}")
        client.cancel(job_id)
    if shell:
        return 0
    return None
