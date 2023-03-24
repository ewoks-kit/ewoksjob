import os
import getpass
from typing import Dict
from multiprocessing import get_context
from multiprocessing import get_all_start_methods

from click import Choice
from celery import Celery
from celery import bootsteps
from celery import concurrency
from celery.bin import worker
from celery.bin.base import CeleryOption

from .slurm import TaskPool as SlurmTaskPool
from .process import TaskPool as ProcessTaskPool

ALL_MP_CONTEXTS = list(get_all_start_methods())
DEFAULT_MP_CONTEXT = get_context()._name

concurrency.ALIASES[
    "process"
] = f"{ProcessTaskPool.__module__}:{ProcessTaskPool.__name__}"
concurrency.ALIASES["slurm"] = f"{SlurmTaskPool.__module__}:{SlurmTaskPool.__name__}"
worker.WORKERS_POOL.choices = list(worker.WORKERS_POOL.choices) + ["process", "slurm"]


def add_options(app: Celery) -> None:
    _add_slurm_pool_options(app)
    _add_process_pool_options(app)
    app.steps["worker"].add(CustomWorkersBootStep)


class CustomWorkersBootStep(bootsteps.Step):
    def __init__(self, parent, **options):
        apply_worker_options(options)
        super().__init__(parent, **options)


def apply_worker_options(options):
    SlurmTaskPool.EXECUTOR_OPTIONS = _extract_slurm_options(options)
    ProcessTaskPool.EXECUTOR_OPTIONS = _extract_process_options(options)


def _add_slurm_pool_options(app: Celery) -> None:
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-url"],
            required=False,
            default=os.environ.get("SLURM_URL"),
            help="SLURM REST URL",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-token"],
            required=False,
            default=os.environ.get("SLURM_TOKEN"),
            help="SLURM REST access token",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-user"],
            required=False,
            default=os.environ.get("SLURM_USER", getpass.getuser()),
            help="SLURM user name",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-log-directory"],
            required=False,
            help="Directory for SLURM to store the STDOUT and STDERR files",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-data-directory"],
            required=False,
            help="Directory for SLURM data transfer over files (TCP otherwise)",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-pre-script"],
            required=False,
            help="Script to be executes before each SLURM job (e.g. activate python environment)",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-post-script"],
            required=False,
            help="Script to be executes after each SLURM job",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["-sp", "--slurm-parameters"],
            required=False,
            multiple=True,
            help="SLURM job parameters (-sp NAME=VALUE). See https://slurm.schedmd.com/rest_api.html#v0.0.38_job_properties",
            help_group="Slurm Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--slurm-python-cmd"],
            required=False,
            help="Python command (Default: python3)",
            help_group="Slurm Pool Options",
        )
    )


def _add_process_pool_options(app: Celery) -> None:
    app.user_options["preload"].add(
        CeleryOption(
            ["--process-context"],
            required=False,
            type=Choice(ALL_MP_CONTEXTS, case_sensitive=False),
            default=DEFAULT_MP_CONTEXT,
            show_default=True,
            help="Child process creation",
            help_group="Process Pool Options",
        )
    )
    app.user_options["preload"].add(
        CeleryOption(
            ["--process-no-precreate"],
            required=False,
            default=False,
            help="Child processes not created on startup",
            help_group="Process Pool Options",
        )
    )


SLURM_NAME_MAP = {
    "slurm_url": "url",
    "slurm_user": "user_name",
    "slurm_token": "token",
    "slurm_log_directory": "log_directory",
    "slurm_data_directory": "data_directory",
    "slurm_pre_script": "pre_script",
    "slurm_post_script": "post_script",
    "slurm_parameters": "parameters",
    "slurm_python_cmd": "python_cmd",
}


def _extract_slurm_options(options: Dict) -> dict:
    slurm_options = {
        name: options.get(option) for option, name in SLURM_NAME_MAP.items()
    }
    parameters = slurm_options.pop("parameters", None)
    if parameters:
        parameters = [s.partition("=") for s in parameters]
        slurm_options["parameters"] = {p[0]: p[2] for p in parameters if p[2]}
    return slurm_options


PROCESS_NAME_MAP = {
    "process_context": "context",
    "process_no_precreate": "precreate",
}


def _extract_process_options(options: Dict) -> dict:
    process_options = {
        name: options.get(option) for option, name in PROCESS_NAME_MAP.items()
    }
    process_options["precreate"] = not process_options["precreate"]
    return process_options
