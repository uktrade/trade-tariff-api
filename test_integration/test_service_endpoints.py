from datetime import datetime
from hashlib import sha512
from typing import Generator

import os
import pytest

from dotenv import find_dotenv
from dotenv.main import DotEnv
from playwright.sync_api import APIRequestContext
from playwright.sync_api import Playwright


API_V1_PATH = "/api/v1"
DELTAS_URL_PATH = f"{API_V1_PATH}/taricdeltas"
FILES_URL_PATH = f"{API_V1_PATH}/taricfiles"

SEQUENCE_ID = 180251
ENVELOPE_FILE_NAME = "DIT123456.xml"
MODTIME = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
DATE = datetime.now().strftime("%Y-%m-%d")


@pytest.fixture(scope="session")
def init_from_dotenv(pytestconfig) -> None:
    """
    Load config variables from a `.env` file into environment variables for use
    by fixtures and tests.

    The `.env` should be located in this module's directory.
    """

    env_filename = pytestconfig.getoption("--env-file")
    dotenv_path = find_dotenv(filename=env_filename)

    assert dotenv_path

    dotenv = DotEnv(dotenv_path=dotenv_path)

    assert dotenv.set_as_environment_variables()


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
    API endpoints. The returned APIRequestContext is disposed of during fixture
    teardown."""

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
def envelope_file_content() -> str:
    """Return the contents of a valid envelope file."""

    return """<?xml version="1.0" encoding="UTF-8"?>
        <env:envelope
          xmlns="urn:publicid:-:DGTAXUD:TARIC:MESSAGE:1.0"
          xmlns:env="urn:publicid:-:DGTAXUD:GENERAL:ENVELOPE:1.0"
          id="12345"
        >
        <env:transaction id="123"></env:transaction>
        </env:envelope>"""


@pytest.fixture
def posted_envelope(
    api_request_context: APIRequestContext,
    envelope_file_content: str,
) -> Generator[None, None, None]:
    """Post an envelope to the service. Used for tests that require an envelope
    to retrieve. The envelope is deleted (via the API) during fixture
    teardown."""

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
    api_request_context: APIRequestContext,
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
    to an endpoint that requires an API key."""

    request_context = playwright.request.new_context(base_url=service_base_url)
    response = request_context.get(DELTAS_URL_PATH)

    assert response.status == 403

    request_context.dispose()


def test_post_envelope(
    api_request_context: APIRequestContext,
    envelope_file_content: str,
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
    api_request_context: APIRequestContext,
    posted_envelope: None,
    envelope_file_content: str,
):
    """Test getting a list of envelopes from the service."""

    response = api_request_context.get(f"{DELTAS_URL_PATH}/{DATE}")
    assert response.ok

    deltas = response.json()
    file_count = len(deltas) if deltas else 0

    # If files were recently loaded onto the service, then the fixture file may
    # not be the only one returned, but it should be the last one.
    assert file_count > 0
    assert deltas[file_count - 1]["id"] == SEQUENCE_ID
    assert deltas[file_count - 1]["issue_date"] == MODTIME
    assert (
        deltas[file_count - 1]["sha512"]
        == sha512(envelope_file_content.encode("utf-8")).hexdigest()
    )


def test_get_envelope(
    api_request_context: APIRequestContext,
    posted_envelope: None,
    envelope_file_content: str,
):
    """Test getting a specific envelope from the service."""

    response = api_request_context.get(f"{FILES_URL_PATH}/{SEQUENCE_ID}")
    assert response.ok

    assert response.body() == str.encode(envelope_file_content)
