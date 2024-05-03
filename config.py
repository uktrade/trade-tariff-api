import os

from .asim_formatter import ASIMFormatter
from .utils import strtobool, strtolist

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
PORT = int(os.environ.get("PORT", 8080))

AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_BUCKET_NAME = os.environ["AWS_BUCKET_NAME"]

API_ROOT = os.environ.get("API_ROOT", "http://localhost:8080/api/v1/")

APIKEYS = strtolist(os.environ.get("APIKEYS"))
APIKEYS_UPLOAD = strtolist(os.environ.get("APIKEYS_UPLOAD"))

TARIC_FILES_FOLDER = os.environ.get("TARIC_FILES_FOLDER", "taricfiles")
TARIC_FILES_INDEX = os.environ.get("TARIC_FILES_INDEX", "taricdeltas.json")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "asim_formatter": {
            "()": ASIMFormatter,
        }
    },
    "handlers": {
        "wsgi": {
            "class": "logging.StreamHandler",
            "stream": "ext://flask.logging.wsgi_errors_stream",
            "formatter": "asim_formatter",
        }
    },
    "root": {"level": "INFO", "handlers": ["wsgi"]},
    "taricapi": {"level": "INFO", "handlers": ["wsgi"]},
    "flask": {"level": "INFO", "handlers": ["wsgi"]},
}

STREAM_CHUNK_SIZE = 1024 * 512  # ~0.5mb

# This only needs to be set under testing conditions to use MinIO - in local and deployed envs, we use AWS S3.
S3_ENDPOINT_URL = os.environ.get("S3_ENDPOINT_URL", None)

NUM_PROXIES = int(os.environ.get("NUM_PROXIES", 0))
SENTRY_DSN = os.environ.get("SENTRY_DSN")

REQUIRE_AUTH_FOR_READS = strtobool(os.environ.get("REQUIRE_AUTH_FOR_READS", "true"))

ELASTIC_APM_URL = os.environ.get("ELASTIC_APM_URL", None)
ELASTIC_APM_TOKEN = os.environ.get("ELASTIC_APM_TOKEN", None)

GA_TRACKING_ID = os.environ.get("GA_TRACKING_ID", None)
GA_ENDPOINT = os.environ.get("GA_ENDPOINT", "https://www.google-analytics.com/collect")
