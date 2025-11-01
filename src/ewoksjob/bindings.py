import json
import logging
from typing import Any
from typing import Callable
from typing import Optional

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
    """Submit a workflow to be executed remotely. The workflow is
    resolved on the client-side by default (e.g. load from a file)
    but can optionally be resolved remotely.
    """
    if submit is None:
        raise RuntimeError("requires the 'ewoksjob' package")
    if _celery_options is None:
        _celery_options = dict()

    if resolve_graph_remotely:
        deserialized_graph = None
    else:
        if _convert_graph is None:
            _convert_graph = _load_graph
        try:
            deserialized_graph = _load_graph(graph, load_options=load_options)
            ex = None
        except Exception as e:
            ex = e
            deserialized_graph = None
        if deserialized_graph is None:
            if ex:
                logger.warning(
                    "Failed loading the graph on the client side (%s). Try loading it remotely.",
                    ex,
                )
            else:
                logger.warning(
                    "Failed loading the graph on the client side. Try loading it remotely."
                )

    if deserialized_graph is None:
        options["load_options"] = load_options
    else:
        graph = deserialized_graph

    return submit(args=(graph,), kwargs=options, **_celery_options)


def _load_graph(graph, load_options: Optional[dict] = None) -> Any:
    if not isinstance(graph, str):
        return
    if not graph.endswith((".json", ".yml", ".yaml")):
        return
    with open(graph, "r") as f:
        if graph.endswith(".json"):
            return json.load(f, **load_options)
        else:
            return yaml.safe_load(f, **load_options)
