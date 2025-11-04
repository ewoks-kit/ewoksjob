import traceback
from argparse import Namespace
from pprint import pprint
from typing import Callable
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

import click
from ewoksutils.cli_utils import cli_submit_utils
from ewoksutils.cli_utils.cli_click import add_click_options

from ..bindings import submit_graph


@click.command("submit")
@add_click_options(cli_submit_utils.submit_arguments(shell=True))
def submit(cli_args: Namespace) -> Union[List[dict], Literal[0, 1]]:
    """Submit an Ewoks workflow."""
    result = command_submit(cli_args, shell=True)
    if result:
        click.get_current_context().exit(result)


def command_submit(
    cli_args: Namespace, _convert_graph: Optional[Callable] = None, shell: bool = False
) -> Union[List[dict], Literal[0, 1]]:
    cli_submit_utils.parse_submit_arguments(cli_args, shell=shell)

    return_code = 0
    keep_results = []

    futures = list()
    for workflow, graph in zip(cli_args.workflows, cli_args.graphs):
        future = submit_graph(
            graph,
            _convert_graph=_convert_graph,
            engine=cli_args.engine,
            resolve_graph_remotely=cli_args.resolve_graph_remotely,
            **cli_args.execute_options,
            _celery_options=cli_args.cparameters,
        )
        print(f"Workflow '{workflow}' submitted (ID: {future.uuid})")
        futures.append(future)
    if cli_args.wait < 0:
        if shell:
            return return_code
        return keep_results

    print("Waiting for results ...")
    print()
    for workflow, future in zip(cli_args.workflows, futures):
        print(
            "###########################################################################"
        )
        print(f"# Result of workflow '{workflow}' (ID: {future.uuid})")
        print(
            "###########################################################################"
        )
        try:
            results = future.result(timeout=cli_args.wait)
        except Exception as ex:
            if _is_timeout(ex):
                print(f"Not finished after {cli_args.wait}s")
            else:
                traceback.print_exc()
                print("FAILED")
            results = ex
            return_code = 1
        else:
            if cli_args.outputs == "none":
                if results is None:
                    print("FAILED")
                else:
                    print("FINISHED")
            else:
                pprint(results)
                print("FINISHED")
            if results is None:
                return_code = 1
        finally:
            print()
        if not shell:
            keep_results.append(results)

    if shell:
        return return_code
    return keep_results


def _is_timeout(exception: Optional[Exception]) -> bool:
    if exception is None:
        return False
    if isinstance(exception, TimeoutError):
        return True
    if _is_timeout(exception.__cause__):
        return True
    if _is_timeout(exception.__context__):
        return True
    return False
