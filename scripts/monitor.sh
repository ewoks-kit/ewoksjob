#!/bin/bash
#
# Start the Celery monitor.
#
# scripts/monitor.sh --redis

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ $1 == "--redis" ]];then
    echo "RUN REDIS MONITOR"
    export EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig_redis.py
else
    echo "UNKNOWN argument $1"
    exit 1
fi

export FLOWER_UNAUTHENTICATED_API=true

(cd $SCRIPT_DIR; ewoksjob monitor "${@:2}")
