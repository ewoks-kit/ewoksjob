#!/bin/bash
#
# Start the Celery monitor.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
EWOKS_CONFIG_URI=$SCRIPT_DIR/celeryconfig.py ewoksjob monitor $@
