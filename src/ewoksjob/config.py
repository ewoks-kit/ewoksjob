import os
import sys
import logging
import importlib
from pathlib import Path
from typing import Optional, Tuple

from celery.loaders.base import BaseLoader
from celery import Celery

logger = logging.getLogger(__name__)


class EwoksLoader(BaseLoader):
    """Celery loader based on a configuration URI: python file, python module, yaml file, Beacon URL.

    Requires the environment variable CELERY_LOADER=ewoksjob.config.EwoksLoader
    """

    def __init__(self, app: Celery) -> None:
        self.app = app
        super().__init__(app)

    def read_configuration(self) -> dict:
        config = read_configuration(_get_cfg_uri())

        # Warning: calling with silent=True causes sphinx doc
        # building to fail.
        self.app.config_from_object(config, force=True)

        return config


def _get_cfg_uri() -> str:
    if os.environ.get("BEACON_HOST", None):
        default_cfg = "beacon:///ewoks/config.yml"
    else:
        default_cfg = ""
    return os.environ.get("CELERY_CONFIG_URI", default_cfg)


def read_configuration(cfg_uri: Optional[str] = None) -> dict:
    """Examples:

    - Beacon URL:
        - beacon:///ewoks/config.yml
        - beacon://id22:25000/ewoks/config.yml
    - Yaml file:
        - /tmp/ewoks/config.yml
    - Python file:
        - /tmp/ewoks/config.py
    - Python module:
        - myproject.config
    """
    if cfg_uri and (
        cfg_uri.startswith("beacon:") or cfg_uri.split(".")[-1] in ("yml", "yaml")
    ):
        config = _read_yaml_config(cfg_uri)
        if "celery" in config:
            config = config["celery"]
        elif "CELERY" in config:
            config = config["CELERY"]
    else:
        config = _read_py_config(cfg_uri)
    return config


def _read_yaml_config(resource: str) -> dict:
    from blissdata.beacon.files import read_config

    return read_config(resource)


def _read_py_config(cfg_uri: Optional[str] = None) -> dict:
    sys_path, module = _get_config_module(cfg_uri)
    keep_sys_path = sys.path
    sys.path.insert(0, sys_path)
    try:
        config = vars(importlib.import_module(module))
        mtype = type(os)
        config = {
            k: v
            for k, v in config.items()
            if not k.startswith("_") and not isinstance(v, mtype)
        }
        return config
    finally:
        sys.path = keep_sys_path


def _get_config_module(cfg_uri: Optional[str] = None) -> Tuple[str, str]:
    if not cfg_uri:
        cfg_uri = os.environ.get("CELERY_CONFIG_MODULE")
    if not cfg_uri:
        return os.getcwd(), "celeryconfig"
    path = Path(cfg_uri)
    if path.is_file():
        parent = str(path.parent.absolute())
        return parent, path.stem
    return os.getcwd(), cfg_uri
