#!/usr/bin/env bash

export DB_HOST
export DB_PORT
export DB_NAME
export DB_USESSL

echo "Getting fulfilment count (timestamp 2019-10-22T16:00:00+01:00)"

echo "time from: "
read FULFILMENT_FROM

echo "time to"
read FULFILMENT_TO

echo "database username: "
read USERNAME

echo "Database Password"
read -s PASSWORD

python fulfilment_count.py $FULFILMENT_FROM $FULFILMENT_TO $USERNAME $PASSWORD