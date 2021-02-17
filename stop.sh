#!/bin/sh

pid=$(pgrep -f virtual_zwave.py)
if [ -n "$pid" ]
then
  kill -15 "$pid"
else
  echo "Virtual Z-Wave controller isn't running"
  exit 1
fi
