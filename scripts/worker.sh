#!/bin/bash
#
# Start a Celery worker pool (processes by default) that serves the ewoks application.
#
# rm -rf scripts/results;scripts/worker.sh --redis --pool=process --loglevel=info
# rm -rf scripts/results;scripts/worker.sh --sql --pool=process --loglevel=info

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export CELERY_LOADER=ewoksjob.config.EwoksLoader

if [[ $1 == "--redis" ]];then
    export CELERY_CONFIG_URI=$SCRIPT_DIR/celeryconfig_redis.py
else
    export CELERY_CONFIG_URI=$SCRIPT_DIR/celeryconfig_sql.py
fi

celery -A ewoksjob.apps.ewoks worker "${@:2}"