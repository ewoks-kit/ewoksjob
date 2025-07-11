# CHANGELOG.md

## (unreleased)

New features:

- Add `--slurm-cleanup-job-artifacts` worker arguments.

Changes:

- Do not cleanup slurm job logs by defaults.

Bug fixes:

- Add deprecated `AsyncResult` method `failed` to `FutureInterface`.

## 1.0.0

New features:

- Custom ewoksjob future interface independent of the backend technology.
- Support cancelling jobs executed by `--pool=slurm` workers.

## 0.7.0

Changes:

- Drop support for python 3.7

New features:

- Add ewoks execute parameters to the worker configuration under `EWOKS_EXECUTION`.

## 0.6.1

Changes:

- `get_workers` is deprecated in favor of `get_queues`.
- Remove `sqlalchemy` and `redis` version bounds.

## 0.6.0

Changes:

- Deprecate `ewoksjob.client.convert_workflow` in favor of `ewoksjob.client.convert_graph`
- Pip `blissworker` extra installs `blissdata[tango]`

Bug Fixes:

- Fix `SlurmRestExecutor` exit call bug

## 0.5.0

Changes:

- Use new `pyslurmutils` API

## 0.4.0

Changes:

- Default log level of an ewoks worker is `INFO`

## 0.3.3

- Update documentation

## 0.3.2

Bug fixes:

- Support pip 24.1

## 0.3.1

Bug fixes:

- Support `.yml` configuration files in addition to `.yaml`
- Support not fully patched gevent environment

## 0.3.0

Bug fixes:

- Fix exception type for pypushflow >= 0.6

New features:

- `ewoksjob.client`: Add `get_workers` util to retrieve Celery workers
- Use local timezone instead of UTC in Celery

## 0.2.5

New features:

- Add automatic task discovery to the ewoks celery API

## 0.2.4

Bug fixes:

- blacklist broken kombu version

## 0.2.3

Bug fixes:

- blacklist broken kombu version

## 0.2.2

Changes:

- CLI JSON encoding of slurm parameters

## 0.2.1

Bug fixes:

- Install `gevent` when installing with the [slurm] option

## 0.2.0

Changes:

- Refactor Slurm pool to use gevent

New features:

- add console script `ewoksjob` to start worker and monitor

## 0.1.1

Bug fixes:

- Worker fails when configuration is missing

## 0.1.0

New features:

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
