#!/bin/sh

export AWS_BUCKET_NAME=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.bucket_name')
export AWS_ACCESS_KEY_ID=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.aws_access_key_id')
export AWS_SECRET_ACCESS_KEY=$(echo $VCAP_SERVICES | jq -r '.["aws-s3-bucket"][0].credentials.aws_secret_access_key')

exec $@
