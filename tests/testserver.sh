#!/usr/bin/env bash

source tests/test.env

# assume running from project root folder - and virtualenv already setup
python taricapi.py &

until curl localhost:${PORT} > /dev/null; do sleep 1; done
