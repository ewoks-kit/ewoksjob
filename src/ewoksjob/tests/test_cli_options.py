import logging

from ..worker import options as options_mod


def test_extract_slurm_options(monkeypatch, caplog):
    options = {
        # SLURM_NAME_MAP coverage
        "slurm_url": "http://test",
        "slurm_user": "user",
        "slurm_token": "token",
        "slurm_log_directory": "/logs",
        "slurm_data_directory": "/data",
        "slurm_pre_script": "pre.sh",
        "slurm_post_script": "post.sh",
        "slurm_python_cmd": "python3",
        "slurm_cleanup_job_artifacts": True,
        # Parameters (including environment)
        "slurm_parameters": [
            "time_limit=60",
            'environment={"FOO": "bar_from_params", "HELLO": "world_from_params", "KEEP": "keep_from_params"}',
        ],
        # Environment variables (mix of cases)
        "slurm_environment": [
            "FOO=bar_from_cli",  # override parameters
            "BAR=baz_from_cli",  # not in parameters
            "HELLO",  # override parameters from env
            "MISSING",  # should trigger warning
        ],
    }

    monkeypatch.setenv("FOO", "bar_from_env")
    monkeypatch.setenv("HELLO", "world_from_env")
    monkeypatch.delenv("MISSING", raising=False)

    with caplog.at_level(logging.WARNING, logger="options"):
        result = options_mod._extract_slurm_options(options)

    expected = {
        "url": "http://test",
        "user_name": "user",
        "token": "token",
        "log_directory": "/logs",
        "data_directory": "/data",
        "pre_script": "pre.sh",
        "post_script": "post.sh",
        "python_cmd": "python3",
        "cleanup_job_artifacts": True,
        "parameters": {
            "time_limit": 60,
            "environment": {
                "FOO": "bar_from_cli",
                "BAR": "baz_from_cli",
                "HELLO": "world_from_env",
                "KEEP": "keep_from_params",
            },
        },
    }

    assert result == expected

    message = "Environment variable 'MISSING' is not defined (not passed to Slurm)"
    assert any(record.message == message for record in caplog.records)
