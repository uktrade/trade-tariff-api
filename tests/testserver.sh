#!/usr/bin/env bash

source tests/test.env

# assume running from project root folder - and virtualenv already setup
python taricapi.py &

until curl localhost:${PORT} > /dev/null; do sleep 1; done

echo "Uploading test fixture"
curl -s -i -H "X-API-KEY: def456" -H "X-Forwarded-For: 1.2.3.4, 127.0.0.1" --form file=@tests/DIT123456.xml -w "%{http_code}" -o /dev/null http://localhost:${PORT}/api/v1/taricfiles/180251?modtime=2019-02-05T12:00:00.000
