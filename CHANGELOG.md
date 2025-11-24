# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.3] - 2025-11-24

### Fixed

- Fix `gevent` patching done too late for `gevent` and `slurm` workers with `blissdata 2.3.0`.

## [1.3.2] - 2025-11-04

### Fixed

- `ewoksjob submit`: uses `click.get_current_context().exit(result)` for failure.

## [1.3.1] - 2025-11-02

### Fixed

- `ewoksjob submit`: exit code is now 1 when the workflow fails.

## [1.3.0] - 2025-11-01

### Added

- Add `ewoksjob submit` and `ewoksjob cancel` CLI commands.

## [1.2.0] - 2025-08-20

### Added

- Support celery worker option `--max-tasks-per-child` in "slurm" and "process" pool.

### Fixed

- Prevent “warm” shutdown of Slurm workers from hanging by avoiding blocking
  the gevent loop on worker exit.
- Handle `interval=None` in `CeleryFuture.result` and `EwoksEventReader.poll_events`.

## [1.1.2] - 2025-08-08

### Fixed

- `EWOKS_EXECUTION` was not taken into account with `--pool=slurm`.

## [1.1.1] - 2025-08-02

### Fixed

- Add deprecated `queue` attribute to `FutureInterface`.

## [1.1.0] - 2025-07-13

### Added

- Add `--slurm-cleanup-job-artifacts` worker arguments.

### Changed

- Do not cleanup slurm job logs by defaults.

### Fixed

- Add deprecated `AsyncResult` method `failed` to `FutureInterface`.
- Fix typo in `LocalFuture.exception`.

## [1.0.0] - 2025-04-28

### Added

- Custom ewoksjob future interface independent of the backend technology.
- Support cancelling jobs executed by `--pool=slurm` workers.

## [0.7.0] - 2025-03-25

### Changed

- Drop support for python 3.7

### Added

- Add ewoks execute parameters to the worker configuration under `EWOKS_EXECUTION`.

## [0.6.1] - 2024-12-21

### Changed

- `get_workers` is deprecated in favor of `get_queues`.
- Remove `sqlalchemy` and `redis` version bounds.

## [0.6.0] - 2024-10-09

### Changed

- Deprecate `ewoksjob.client.convert_workflow` in favor of `ewoksjob.client.convert_graph`
- Pip `blissworker` extra installs `blissdata[tango]`

### Fixed

- Fix `SlurmRestExecutor` exit call bug

## [0.5.0] - 2024-09-16

### Changed

- Use new `pyslurmutils` API

## [0.4.0] - 2024-07-24

### Changed

- Default log level of an ewoks worker is `INFO`

## [0.3.3] - 2024-06-25

- Update documentation

## [0.3.2] - 2024-06-23

### Fixed

- Support pip 24.1

## [0.3.1] - 2024-05-29

### Fixed

- Support `.yml` configuration files in addition to `.yaml`
- Support not fully patched gevent environment

## [0.3.0] - 2024-01-30

### Fixed

- Fix exception type for pypushflow >= 0.6

### Added

- `ewoksjob.client`: Add `get_workers` util to retrieve Celery workers
- Use local timezone instead of UTC in Celery

## [0.2.5] - 2023-06-12

### Added

- Add automatic task discovery to the ewoks celery API

## [0.2.4] - 2023-06-01

### Fixed

- blacklist broken kombu version

## [0.2.3] - 2023-05-25

### Fixed

- blacklist broken kombu version

## [0.2.2] - 2023-05-18

### Changed

- CLI JSON encoding of slurm parameters

## [0.2.1] - 2023-03-24

### Fixed

- Install `gevent` when installing with the [slurm] option

## [0.2.0] - 2023-03-24

### Changed

- Refactor Slurm pool to use gevent

### Added

- add console script `ewoksjob` to start worker and monitor

## [0.1.1] - 2023-01-26

### Fixed

- Worker fails when configuration is missing

## [0.1.0] - 2023-01-04

### Added

- Job queue pool:
  - celery
  - local process pool
  - local thread pool
  - local SLURM pool
- Supported jobs
  - workflow execution (+ saving and uploading)
  - workflow conversion
  - task discovery
- Redis handler for ewoks events

[unreleased]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.3.3...HEAD
[1.3.3]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.3.2...v1.3.3
[1.3.2]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.3.1...v1.3.2
[1.3.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.3.0...v1.3.1
[1.3.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.2.0...v1.3.0
[1.2.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.1.2...v1.2.0
[1.1.2]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.1.1...v1.1.2
[1.1.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.1.0...v1.1.1
[1.1.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.0.0...v1.1.0
[1.0.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.7.0...v1.0.0
[0.7.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.6.1...v0.7.0
[0.6.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.6.0...v0.6.1
[0.6.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.5.0...v0.6.0
[0.5.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.4.0...v0.5.0
[0.4.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.3.3...v0.4.0
[0.3.3]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.3.2...v0.3.3
[0.3.2]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.3.1...v0.3.2
[0.3.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.3.0...v0.3.1
[0.3.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.2.5...v0.3.0
[0.2.5]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.2.4...v0.2.5
[0.2.4]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.2.3...v0.2.4
[0.2.3]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.2.2...v0.2.3
[0.2.2]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.2.1...v0.2.2
[0.2.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.2.0...v0.2.1
[0.2.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.1.1...v0.2.0
[0.1.1]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v0.1.0...v0.1.1
[0.1.0]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/-/tags/v0.1.0