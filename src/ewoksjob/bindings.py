import os
import warnings
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Optional
from typing import Tuple

from .client import submit
from .client.futures import FutureInterface


def submit_graph(
    graph,
    _convert_graph: Optional[Callable] = None,
    _celery_options: Optional[dict] = None,
    resolve_graph_remotely: Optional[bool] = None,
    load_options: Optional[dict] = None,
    **options,
) -> FutureInterface:
    """Submit a workflow to be executed remotely.

    A JSON or YAML workflow file that exists on the client is sent by content,
    unless ``resolve_graph_remotely`` is true. The worker loads the workflow
    with ``load_options``.
    """
    if _convert_graph is not None:
        warnings.warn(
            "The '_convert_graph' argument is deprecated and ignored.",
            DeprecationWarning,
            stacklevel=2,
        )
    if _celery_options is None:
        _celery_options = dict()
    if not resolve_graph_remotely:
        graph, load_options = _read_local_file(graph, load_options)
    options["load_options"] = load_options
    return submit(args=(graph,), kwargs=options, **_celery_options)


_STRING_REPRESENTATIONS = {
    ".json": "json_string",
    ".yml": "yaml_string",
    ".yaml": "yaml_string",
}


def _read_local_file(
    graph: Any, load_options: Optional[dict]
) -> Tuple[Any, Optional[dict]]:
    """Return the content of a workflow file that exists on the client and the
    load options for this content. Return the arguments unchanged for any other workflow.
    """
    if not isinstance(graph, (str, Path)):
        return graph, load_options
    representation = _STRING_REPRESENTATIONS.get(Path(graph).suffix.lower())
    if representation is None:
        return graph, load_options
    if load_options is None:
        load_options = dict()
    path = os.path.join(load_options.get("root_dir") or "", graph)
    if not os.path.isfile(path):
        return graph, load_options
    with open(path, "r") as f:
        content = f.read()
    return content, {**load_options, "representation": representation}
