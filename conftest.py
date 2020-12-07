import contextlib
import os
import subprocess
import time
import uuid
from typing import Optional

import boto3
import pytest
import requests


@pytest.fixture(scope='session', autouse=True)
def aws_s3_client():
    s3_client = boto3.client(
        's3',
        endpoint_url='http://localhost:9000',
        aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
        aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
    )
    yield s3_client


@pytest.fixture(scope='session', autouse=True)
def aws_bucket(aws_s3_client):
    aws_bucket_name = str(uuid.uuid4())
    aws_s3_client.create_bucket(Bucket=aws_bucket_name)
    yield aws_bucket_name


def upload_file(aws_s3_client, aws_bucket, key, target):
    with open(target, 'rb') as f:
        aws_s3_client.upload_fileobj(f, aws_bucket, key)


@contextlib.contextmanager
def create_application(aws_bucket, env: Optional[dict] = None):
    PORT = 8080
    app_env = {
        **os.environ,
        'PORT': str(PORT),
        'NUM_PROXIES': '2',
        'STREAM_CHUNK_SIZE': '64',
        'APIKEYS_UPLOAD': '',
        'WHITELIST_UPLOAD': '',
        'AWS_BUCKET_NAME': aws_bucket,
        'AWS_ACCESS_KEY_ID': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_ACCESS_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'S3_ENDPOINT_URL': 'http://localhost:9000',
    }
    if env:
        app_env.update(env)

    processes = {
        name: subprocess.Popen(cmds, env=app_env)
        for name, cmds in {
            'api': ['python', 'taricapi.py'],
            'ga': ['python', 'mock_google_analytics_app.py'],
            'sentry': ['python', 'mock_sentry_app.py'],
        }.items()
    }

    attempts = 0
    while attempts < 400:
        try:
            resp = requests.get(f"http://localhost:{PORT}/healthcheck")
            if resp.status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass
        attempts += 1
        time.sleep(0.25)
    else:
        raise Exception("App did not come alive in time.")

    yield processes

    for proc in processes.values():
        proc.kill()

    for proc in processes.values():
        proc.wait(timeout=5)

    output_errors = {name: proc.communicate() for name, proc in processes.items()}

    # for proc in processes.values():
    #     proc.stdout.close()
    #     proc.stderr.close()

    return output_errors
