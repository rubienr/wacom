#!/bin/env bash

# Live plot the current pressure curve mapped from 0 to 65536.
#
# Usage:
# ./pressure-plot.sh
# ./pressure-plot.sh <device hint>
# ./pressure-plot.sh stylus
# ./pressure-plot.sh "Pen stylus"
#
# The pressure plot does not appear until the first pressure value is reported.
#
# Required: xinput, feedgnuplot

device_hint="pen stylus"

if [ -n "$1" ] ; then
  device_hint="$1"
fi

device_info=`xinput --list | grep -i "$device_hint"`
declare -a device_ids
device_ids=(`echo "$device_info" | grep -i "$device_hint" | grep --perl-regexp --only-matching "(?<=id=).*(?=\[)" | tr --delete "[:blank:]"`)
device_id=${device_ids[0]}

if [ -z "$device_id" ] ; then
  echo "no device found with hint \"$device_hint\""
  exit 1
else
  echo -e "found device(s):\n$device_info"
  echo "chosen id: $device_id"
fi

xinput --test "$device_id" \
  | awk -F '[[:blank:]]*a\\[[[:digit:]]+\\]=' '{ if ($4 > 0) {print $4 ; fflush()} }' \
  | feedgnuplot --exit --stream 0.25 --lines --unset grid --xlen 500 --ymax 65536
