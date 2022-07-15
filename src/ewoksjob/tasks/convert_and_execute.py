import ewoks
from typing import Dict, List, Optional

__all__ = ["convert_and_execute_graph"]


def convert_and_execute_graph(
    source,
    destination,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[dict] = None,
    save_options: Optional[dict] = None,
    **kwargs
) -> Dict:
    workflow = ewoks.convert_graph(
        source,
        destination,
        inputs=inputs,
        load_options=load_options,
        save_options=save_options,
    )
    if workflow is None:  # TODO: deprecated, never returns None
        workflow = destination
    return ewoks.execute_graph(workflow, **kwargs)
