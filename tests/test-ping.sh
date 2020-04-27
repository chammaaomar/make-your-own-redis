#!/bin/bash
PING="$(redis-cli PING)"
if [[ "$PING" == "PONG" ]];
then
    exit 0
else
    echo "Test failed: Expected PONG, got back $PING"
    exit 1
fi
