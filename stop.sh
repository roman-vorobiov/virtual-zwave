#!/bin/sh

pid_controller=$(pgrep -f virtual_controller.py)
pid_network=$(pgrep -f virtual_network.py)
if [ -n "$pid_controller" ] && [ -n "$pid_network" ]
then
  kill -15 "$pid_controller"
  kill -15 "$pid_network"
else
  echo "Virtual Z-Wave network isn't running"
  exit 1
fi
