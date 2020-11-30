#!/usr/bin/env bash

source tests/test.env

docker stop tariffs-minio
docker run \
    -p 9000:9000 \
    -e "MINIO_ACCESS_KEY=${AWS_ACCESS_KEY_ID}" \
    -e "MINIO_SECRET_KEY=${AWS_SECRET_ACCESS_KEY}" \
    --name tariffs-minio \
    --rm \
    -d \
    --entrypoint sh \
    minio/minio \
    -c "mkdir -p /data/${AWS_BUCKET_NAME} && minio server /data"
