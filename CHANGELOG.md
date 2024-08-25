# CHANGELOG.md

## (unreleased)

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
