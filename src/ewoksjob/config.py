import importlib
import logging
import os
import sys
import types
from pathlib import Path
from typing import Tuple

from celery import Celery
from celery.loaders.default import Loader
from ewoksutils import uri_utils

# WARNING: import as little as possible because gevent-patching might be done too late

logger = logging.getLogger(__name__)


class EwoksLoader(Loader):
    """Celery loader based on a configuration URI: python file, python module, yaml file, Beacon URL.

    Requires the environment variable CELERY_LOADER=ewoksjob.config.EwoksLoader
    """

    def __init__(self, app: Celery) -> None:
        self.app = app
        super().__init__(app)

    def read_configuration(self) -> dict:
        if "" not in sys.path:
            # This happens when the python process was launched
            # through a python console script
            sys.path.append("")

        cfg_uri = get_cfg_uri()
        if not cfg_uri:
            # Load from the module "celeryconfig" if available
            return super().read_configuration()

        file_type = get_cfg_type(cfg_uri)
        try:
            logger.info(f"Loading celery configuration '{cfg_uri}' (type: {file_type})")
            return read_configuration(cfg_uri=cfg_uri)
        except Exception as e:
            raise RuntimeError(
                f"Cannot load celery configuration from '{cfg_uri}' (type: {file_type})"
            ) from e


def get_cfg_uri() -> str:
    """Returns the celery configuration URI based on environment variables."""
    cfg_uri = os.environ.get("EWOKS_CONFIG_URI")
    if cfg_uri:
        return cfg_uri
    cfg_uri = os.environ.get("CELERY_CONFIG_URI")  # deprecate?
    if cfg_uri:
        return cfg_uri
    beacon_host = os.environ.get("BEACON_HOST", None)
    if beacon_host:
        return "beacon:///ewoks/config.yml"
    cfg_uri = os.environ.get("CELERY_CONFIG_MODULE")
    # the CLI option --config sets this environment variable
    if cfg_uri:
        return cfg_uri
    return ""


def get_cfg_type(cfg_uri: str) -> str:
    parsed = uri_utils.parse_uri(cfg_uri)
    if parsed.scheme == "beacon":
        return "yaml"
    if parsed.scheme in "file":
        file_path = uri_utils.path_from_uri(cfg_uri)
        if file_path.suffix in (".yaml", ".yml"):
            return "yaml"
        return "python"
    return parsed.scheme


def read_configuration(cfg_uri: str) -> dict:
    """Different types of URI's are supported:

    - Python module:
       - myproject.config
    - Python file:
       - /tmp/ewoks/config.py
    - Yaml file:
       - /tmp/ewoks/config.yml
    - Beacon yaml file:
       - beacon:///ewoks/config.yml  (this requires the BEACON_HOST environment variable)
       - beacon://id22:25000/ewoks/config.yml
    """
    file_type = get_cfg_type(cfg_uri)
    if file_type == "yaml":
        config = _read_yaml_config(cfg_uri)
    elif file_type == "python":
        config = _read_py_config(cfg_uri)
    else:
        raise ValueError(f"Configuration URL '{cfg_uri}' is not supported")

    # `celery.app.utils.Settings` converts all parameters to lower-case
    # but we are here before that happens.
    config = {k.lower(): v for k, v in config.items()}
    # Celery parameters need to be on the top level for `celery.app.utils.Settings`.
    if "celery" in config:
        celery_config = config.pop("celery")
        config = {**config, **celery_config}
    return config


def _read_yaml_config(resource: str) -> dict:
    try:
        from blissdata.beacon.files import read_config as bliss_read_config
    except ImportError as e:
        raise RuntimeError(
            f"Cannot get celery configuration '{resource}' from Beacon: blissdata is not installed"
        ) from e
    if sys.platform == "win32" and resource.startswith("file:///"):
        # Bug in blissdata. See https://gitlab.esrf.fr/bliss/blissdata/-/issues/22.
        resource = resource.replace("file:///", "file://")
    return bliss_read_config(resource)


def _read_py_config(cfg_uri: str) -> dict:
    """Warning: this is not thread-safe and it has side-effects during execution"""
    file_path = uri_utils.path_from_uri(cfg_uri)
    sys_path, module = _get_config_module(file_path)

    keep_sys_path = list(sys.path)
    sys.path.insert(0, sys_path)
    try:
        config = vars(importlib.import_module(module))
    finally:
        sys.path = keep_sys_path

    config = {
        k: v
        for k, v in config.items()
        if not k.startswith("_") and not isinstance(v, types.ModuleType)
    }
    return config


def _get_config_module(path: Path) -> Tuple[str, str]:
    if path.is_file():
        return str(path.parent.resolve()), path.stem
    return os.getcwd(), str(path)
