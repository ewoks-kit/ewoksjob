#!/bin/bash
#
# Start the Celery monitor.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ $1 == "--redis" ]];then
    echo "RUN REDIS MONITOR"
    export EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig_redis.py
else
    echo "RUN SQL MONITOR"
    export EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig_sql.py
fi

export FLOWER_UNAUTHENTICATED_API=true

(cd $SCRIPT_DIR; ewoksjob monitor "${@:2}")
