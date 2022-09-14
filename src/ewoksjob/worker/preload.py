import click
from celery import bootsteps
from celery import concurrency
from celery.bin import worker
from .slurm import TaskPool


concurrency.ALIASES["slurm"] = f"{TaskPool.__module__}:{TaskPool.__name__}"
worker.WORKERS_POOL.choices = list(worker.WORKERS_POOL.choices) + ["slurm"]


def add_workers(app):
    app.user_options["preload"].add(
        click.Option(
            ["--slurm-url"],
            required=False,
            help="SLURM REST URL",
        )
    )
    app.user_options["preload"].add(
        click.Option(
            ["--slurm-token"],
            required=False,
            help="SLURM REST access token",
        )
    )
    app.user_options["preload"].add(
        click.Option(
            ["--slurm-user"],
            required=False,
            help="SLURM user name",
        )
    )
    app.user_options["preload"].add(
        click.Option(
            ["--slurm-log-directory"],
            required=False,
            help="Directory for SLURM to store the STDOUT and STDERR files",
        )
    )
    app.user_options["preload"].add(
        click.Option(
            ["--slurm-data-directory"],
            required=False,
            help="Directory for SLURM data transfer over files (TCP otherwise)",
        )
    )
    app.user_options["preload"].add(
        click.Option(
            ["--slurm-pre-script"],
            required=False,
            help="Script to be executes before each SLURM job (e.g. activate python environment)",
        )
    )
    app.user_options["preload"].add(
        click.Option(
            ["--slurm-post-script"],
            required=False,
            help="Script to be executes after each SLURM job",
        )
    )
    app.steps["worker"].add(CustomWorkersBootStep)


class CustomWorkersBootStep(bootsteps.Step):
    def __init__(self, parent, **options):
        namemap = {
            "slurm_url": "url",
            "slurm_user": "user_name",
            "slurm_token": "token",
            "slurm_log_directory": "log_directory",
            "slurm_data_directory": "data_directory",
            "slurm_pre_script": "pre_script",
            "slurm_post_script": "post_script",
            "slurm_parameters": "parameters",
        }
        # SLURM job parameters: https://slurm.schedmd.com/rest_api.html#v0.0.38_job_properties
        #
        #   slurm_parameters = {
        #       "environment": ...,
        #       "partition": ...,
        #       "memory_per_cpu", ...
        #   }
        TaskPool.slurm_executor_options = {
            name: options.get(option) for option, name in namemap.items()
        }
        super().__init__(parent, **options)
