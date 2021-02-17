#!/bin/sh

pid=$(pgrep -f virtual_zwave.py)
if [ -z "$pid" ]
then
  (python3.8 ./virtual_zwave.py "$@") &
else
  echo "Virtual Z-Wave controller already running"
  exit 1
fi
