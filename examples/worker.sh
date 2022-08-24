#!/bin/bash
#
# Start a Celery worker pool (processes by default) that serves the ewoks application.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CELERY_LOADER=ewoksjob.config.EwoksLoader CELERY_CONFIG_URI=$SCRIPT_DIR/celeryconfig.py celery -A ewoksjob.apps.ewoks worker $@