# CHANGELOG.md

## 0.3.0 (unreleased)

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
