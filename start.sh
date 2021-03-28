#!/bin/sh

pid=$(pgrep -f virtual_controller.py)
if [ -z "$pid" ]
then
  (python3 ./virtual_controller.py "$@") &
else
  echo "Virtual Z-Wave controller already running"
  exit 1
fi
