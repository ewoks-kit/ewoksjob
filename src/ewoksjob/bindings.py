import json
import logging
import os
import warnings
from pathlib import Path
from typing import Any
from typing import Callable
from typing import Mapping
from typing import Optional
from typing import Tuple

import yaml

from .client import submit
from .client.futures import FutureInterface

logger = logging.getLogger(__name__)


def submit_graph(
    graph,
    _convert_graph: Optional[Callable] = None,
    _celery_options: Optional[dict] = None,
    resolve_graph_remotely: Optional[bool] = None,
    load_options: Optional[dict] = None,
    **options,
) -> FutureInterface:
    """Submit a workflow to be executed remotely.

    Unless ``resolve_graph_remotely`` is true, the client loads the workflow with
    ``ewoks`` when ``ewoks`` is installed. Without ``ewoks``, or when ``ewoks``
    cannot load the workflow, a JSON or YAML workflow file that exists on the client
    is sent by content. The worker loads a workflow that the client did not load,
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
        graph, load_options = _resolve_on_client(graph, load_options)
    options["load_options"] = load_options
    return submit(args=(graph,), kwargs=options, **_celery_options)


def _resolve_on_client(
    graph: Any, load_options: Optional[dict]
) -> Tuple[Any, Optional[dict]]:
    """Return the workflow to send to the worker and the load options for it."""
    try:
        # Not at the module top: ewoks is optional and imports this module.
        from ewoks import convert_graph
    except ImportError:
        graph, load_options = _read_local_file(graph, load_options)
        if _has_subgraphs(graph, load_options):
            logger.warning(
                "The worker loads the sub-workflows. Install ewoks on the client "
                "to load them on the client."
            )
        return graph, load_options
    try:
        graph = convert_graph(
            graph, None, load_options=load_options, save_requirements=False
        )
    except Exception as e:
        logger.warning(
            "Failed loading the workflow on the client (%s). The worker loads it.", e
        )
        return _read_local_file(graph, load_options)
    return graph, None


def _has_subgraphs(graph: Any, load_options: Optional[dict]) -> bool:
    """Return True when the workflow, or the content of a workflow file, has nodes
    of type ``graph``."""
    representation = (load_options or dict()).get("representation")
    if representation == "json_string":
        graph = json.loads(graph)
    elif representation == "yaml_string":
        graph = yaml.safe_load(graph)
    if not isinstance(graph, Mapping):
        return False
    return any(node.get("task_type") == "graph" for node in graph.get("nodes", []))


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
