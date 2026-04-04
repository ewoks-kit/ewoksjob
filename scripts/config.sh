#!/bin/bash
#
# Start a Celery worker pool (processes by default) that serves the ewoks application.
#
# source scripts/config.sh --redis
# source scripts/config.sh --sql

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ $1 == "--redis" ]];then
    export EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig_redis.py
elif [[ $1 == "--sql" ]];then
    export EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig_sql.py
else
    echo "UNKNOWN argument $1"
    exit 1
fi

echo "EWOKS_CONFIG_URI=$EWOKS_CONFIG_URI"