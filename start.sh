#!/bin/sh

pid_controller=$(pgrep -f virtual_controller.py)
pid_network=$(pgrep -f virtual_network.py)
if [ -z "$pid_controller" ] && [ -z "$pid_network" ]
then
  (python3 ./virtual_controller.py "$@" > /dev/null 2>&1) &
  (python3 ./virtual_network.py "$@" > /dev/null 2>&1) &

  exit 0
else
  echo "Virtual Z-Wave network already running"
  exit 1
fi
