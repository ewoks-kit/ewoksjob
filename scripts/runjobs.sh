#!/bin/bash
#
# Start a Celery worker pool (processes by default) that serves the ewoks application.
#
# scripts/runjobs.sh --redis

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [[ $1 == "--redis" ]];then
    echo "RUN REDIS JOBS"
    export EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig_redis.py
else
    echo "RUN SQL JOBS"
    export EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig_sql.py
fi

echo "RUN example_with_events.py"
python $SCRIPT_DIR/example_with_events.py
if [[ $? -ne 0 ]] ; then
    exit 1
fi

if [[ $1 == "--redis" ]];then
    echo "RUN example_with_events.py --celery --redis"
    python $SCRIPT_DIR/example_with_events.py --celery --redis
    if [[ $? -ne 0 ]] ; then
        exit 1
    fi
else
    echo "RUN example_with_events.py --celery"
    python $SCRIPT_DIR/example_with_events.py --celery
    if [[ $? -ne 0 ]] ; then
        exit 1
    fi
fi

if [[ $1 == "--redis" ]];then
    echo "RUN hello_world_cancel.py"
    python $SCRIPT_DIR/hello_world_cancel.py
    if [[ $? -ne 0 ]] ; then
        exit 1
    fi
fi

echo "RUN hello_world.py"
python $SCRIPT_DIR/hello_world.py
if [[ $? -ne 0 ]] ; then
    exit 1
fi

echo "RUN hello_world_fail.py"
python $SCRIPT_DIR/hello_world_fail.py
if [[ $? -ne 0 ]] ; then
    exit 1
fi

if [[ $1 == "--redis" ]];then
    echo "RUN hello_world_ppf_cancel.py"
    python $SCRIPT_DIR/hello_world_ppf_cancel.py
    if [[ $? -ne 0 ]] ; then
        exit 1
    fi
fi

echo "RUN hello_world_ppf.py"
python $SCRIPT_DIR/hello_world_ppf.py
if [[ $? -ne 0 ]] ; then
    echo "FAILED hello_world_ppf.py"
    exit 1
fi

echo "RUN hello_world_ppf_fail.py"
python $SCRIPT_DIR/hello_world_ppf_fail.py
if [[ $? -ne 0 ]] ; then
    exit 1
fi

echo "FINISHED"