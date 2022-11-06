"""Tasks to be executed in a celery or local pool."""

import logging
from typing import Dict

try:
    from pyicat_plus.client.main import IcatClient
except ImportError:
    IcatClient = None

import ewoks
from ewokscore import task_discovery

logger = logging.getLogger(__name__)

convert_graph = ewoks.convert_graph


def execute_graph(
    workflow, convert_destination=None, upload_parameters=None, **kwargs
) -> Dict:
    if upload_parameters or convert_destination is not None:
        workflow = ewoks.convert_graph(
            workflow,
            convert_destination,
            inputs=kwargs.pop("inputs", None),
            load_options=kwargs.pop("load_options", None),
            save_options=kwargs.pop("save_options", None),
        )
    result = ewoks.execute_graph(workflow, **kwargs)
    if upload_parameters:
        if IcatClient is None:
            raise RuntimeError("requires pyicat-plus")
        metadata_urls = upload_parameters.pop(
            "metadata_urls", ["bcu-mq-01.esrf.fr:61613", "bcu-mq-02.esrf.fr:61613"]
        )
        client = IcatClient(metadata_urls=metadata_urls)
        logger.info(
            "Sending processed dataset '%s' to ICAT: %s",
            upload_parameters.get("dataset"),
            upload_parameters.get("path"),
        )
        client.store_processed_data(**upload_parameters)
    return result


def discover_tasks_from_modules(*args, **kwargs):
    return list(task_discovery.discover_tasks_from_modules(*args, **kwargs))
