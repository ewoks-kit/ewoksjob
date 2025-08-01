# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[unreleased]: https://gitlab.esrf.fr/workflow/ewoks/ewoksjob/compare/v1.1.0...HEAD
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