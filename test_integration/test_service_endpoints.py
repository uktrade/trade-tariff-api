from datetime import datetime
from typing import Generator

import os
import pytest

from dotenv import load_dotenv
from playwright.sync_api import APIRequestContext
from playwright.sync_api import Playwright


DELTAS_URL_PATH = "/api/v1/taricdeltas"
FILES_URL_PATH = "/api/v1/taricfiles"

SEQUENCE_ID = "180251"
ENVELOPE_FILE_NAME = "DIT123456.xml"
MODTIME = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
DATE = datetime.now().strftime("%Y-%m-%d")


@pytest.fixture(scope="session")
def init_from_dotenv() -> None:
    """
    Load config variables from a `.env` file into environment variables for use
    by fixtures and tests.

    The `.env` may be located in this module's directory or higher up the
    application's directory hierarchy.
    """
    assert load_dotenv()


@pytest.fixture(scope="session")
def service_base_url(init_from_dotenv) -> str:
    """Retrieve the base URL of the service under test from the
    env var `SERVICE_BASE_URL`."""

    return os.environ.get("SERVICE_BASE_URL")


@pytest.fixture(scope="session")
def service_api_key(init_from_dotenv) -> str:
    """Retrieve the API key of the service under test from the env var
    `SERVICE_API_KEY`."""

    return os.environ.get("SERVICE_API_KEY")


@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright,
    service_api_key: str,
    service_base_url: str,
) -> Generator[APIRequestContext, None, None]:
    """Generator yeilding a Playwright APIRequestContext for use when calling
    API endpoints."""

    headers = {
        "Accept": "*/*",
    }
    if service_api_key:
        headers["X-API-KEY"] = service_api_key

    request_context = playwright.request.new_context(
        base_url=service_base_url,
        extra_http_headers=headers,
    )
    yield request_context
    request_context.dispose()


@pytest.fixture
def envelope_file_content():
    return (
        """<?xml version="1.0" encoding="UTF-8"?>
        <env:envelope
          xmlns="urn:publicid:-:DGTAXUD:TARIC:MESSAGE:1.0"
          xmlns:env="urn:publicid:-:DGTAXUD:GENERAL:ENVELOPE:1.0"
          id="12345"
        >
        <env:transaction id="123"></env:transaction>
        </env:envelope>"""
    )


@pytest.fixture
def posted_envelope(
    api_request_context,
    envelope_file_content,
):
    """Post an envelope to the service. Used for tests that require an envelope to retrieve."""
    response = api_request_context.post(
        f"{FILES_URL_PATH}/{SEQUENCE_ID}",
        params={
            "modtime": MODTIME,
        },
        multipart={
            "file": {
                "name": ENVELOPE_FILE_NAME,
                "mimeType": "application/xml",
                "buffer": str.encode(envelope_file_content),
            },
        },
    )
    assert response.ok
    yield
    response = api_request_context.delete(f"{FILES_URL_PATH}/{SEQUENCE_ID}")
    assert response.ok


def test_root_path(
    api_request_context,
):
    """Test that the application's root path responds correctly with a
    `200 OK` response."""

    response = api_request_context.get(url="")

    assert response.ok


def test_fail_with_no_api_key(
    playwright: Playwright,
    service_base_url: str,
):
    """Test that the application correctly returns a 403 response (not allowed)
    to an endpoint that requires an API key.
    """

    request_context = playwright.request.new_context(base_url=service_base_url)
    response = request_context.get(DELTAS_URL_PATH)

    assert response.status == 403

    request_context.dispose()


def test_post_envelope(
    api_request_context,
    envelope_file_content,
):
    """Test posting a valid envelope file to the service."""

    response = api_request_context.post(
        f"{FILES_URL_PATH}/{SEQUENCE_ID}",
        params={
            "modtime": MODTIME,
        },
        multipart={
            "file": {
                "name": ENVELOPE_FILE_NAME,
                "mimeType": "application/xml",
                "buffer": str.encode(envelope_file_content),
            },
        },
    )

    assert response.ok


def test_get_deltas(
    api_request_context,
    posted_envelope,
):
    """Test getting a list of envelopes from the service."""

    response = api_request_context.get(f"{DELTAS_URL_PATH}/{DATE}")

    assert response.ok
