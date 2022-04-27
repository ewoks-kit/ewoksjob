#!/bin/bash
#
# Start a Celery worker pool (processes by default) that serves the ewoks application.
# Not all configurations can be provided through the CLI (e.g. `result_serializer`)
#

# celery -A ewoksjob.apps.ewoks worker --broker redis://localhost:10003/3 --result-backend redis://localhost:10003/4

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export CELERY_CONFIG_MODULE=celeryconfig  # python module name which can be imported
( cd $SCRIPT_DIR; celery -A ewoksjob.apps.ewoks worker )