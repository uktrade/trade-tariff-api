from typing import Generator

import os
import pytest

from dotenv import load_dotenv
from playwright.sync_api import APIRequestContext
from playwright.sync_api import expect
from playwright.sync_api import Playwright
from playwright.sync_api import Page


DELTAS_URL_PATH = "/api/v1/taricdeltas"
FILES_URL_PATH = "/api/v1/taricfiles"


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

    headers = {}
    if service_api_key:
        headers["X-API-KEY"] = service_api_key

    request_context = playwright.request.new_context(
        base_url=service_base_url,
        extra_http_headers=headers,
    )
    yield request_context
    request_context.dispose()


def test_root_path(
    playwright: Playwright,
    service_base_url: str,
):
    """Test that the application's root path responds correctly with a
    `200 OK` response."""

    request_context = playwright.request.new_context(base_url=service_base_url)
    response = request_context.get(url="")
    assert response.ok
    request_context.dispose()


def test_fail_with_no_api_key(
    api_request_context,
):
    """
    TODO:

    test "No API KEY -> expect 403"
    out=$(curl -s -w "%{http_code}" -o /dev/null $APIURLLIST)
    assert "403" "$out"
    """
