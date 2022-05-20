#!/bin/bash
#
# Start a Celery worker pool (processes by default) that serves the ewoks application.
# Not all configurations can be provided through the CLI (e.g. `result_serializer`)
#

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
( cd $SCRIPT_DIR; celery flower )