import ewoks

try:
    from pyicat_plus.client.main import IcatClient
except ImportError:
    IcatClient = None
from typing import Dict, List, Optional

__all__ = ["execute_and_upload_graph"]


def execute_and_upload_graph(
    source,
    inputs: Optional[List[dict]] = None,
    load_options: Optional[List[dict]] = None,
    upload_kwargs: Optional[Dict] = None,
    **kwargs
) -> Dict:
    workflow = ewoks.convert_graph(
        source,
        None,
        inputs=inputs,
        load_options=load_options,
        save_options={"representation": "json_string"},
    )
    result = ewoks.execute_graph(workflow, **kwargs)
    if IcatClient is None:
        raise RuntimeError("requires pyicat-plus")
    if upload_kwargs is None:
        upload_kwargs = dict()
    metadata_urls = upload_kwargs.pop(
        "metadata_urls", ["bcu-mq-01.esrf.fr:61613", "bcu-mq-02.esrf.fr:61613"]
    )
    client = IcatClient(metadata_urls=metadata_urls)
    client.store_processed_data(**upload_kwargs)
    return result
