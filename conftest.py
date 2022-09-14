def pytest_addoption(parser):
    parser.addoption(
        "--slurm-log-directory",
        type=str,
        default=None,
        help="Directory for SLURM job log files ('tmpdir' for pytest temporary directory)",
    )
    parser.addoption(
        "--slurm-data-directory",
        type=str,
        default=None,
        help="Directory for SLURM communication ('tmpdir' for pytest temporary directory)",
    )
