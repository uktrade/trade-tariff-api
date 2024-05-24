import json
import logging
from datetime import datetime
from flask import request, Flask, Response

from asim_formatter import ASIMFormatter


def test_asim_formatter_get_log_dict():
    """Test that get_log_dict returns a correctly formatted log record"""
    formatter = ASIMFormatter()
    log_record = logging.LogRecord(
        name=__name__,
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="This is a test log message",
        args=(),
        exc_info=None,
    )
    log_time = datetime.utcfromtimestamp(log_record.created).isoformat()

    log_dict = formatter.get_log_dict(log_record)

    assert log_dict == {
        "EventMessage": log_record.msg,
        "EventCount": 1,
        "EventStartTime": log_time,
        "EventEndTime": log_time,
        "EventType": "HTTPsession",
        "EventSeverity": "Informational",
        "EventOriginalSeverity": log_record.levelname,  # duplicate of above?
        "EventSchema": "WebSession",
        "EventSchemaVersion": "0.2.6",
    }


def test_asim_formatter_get_request_dict():
    """Test that get_request_dict returns a correctly formatted dictionary of request data"""
    app = Flask(__name__)
    with app.test_request_context(
        method="GET",
        path="/example_route",
        query_string="param1=value1&param2=value2",
        headers={
            "Content-Type": "application/json",
            "X-Forwarded-For": "1.1.1.1",
            "X-Amzn-Trace-Id": "123testid",
        },
        data='{"key": "value"}',
    ):
        request_dict = ASIMFormatter().get_request_dict(request)

        assert request_dict == {
            "Url": request.url,
            "UrlOriginal": request.url,
            "HttpVersion": request.environ.get("SERVER_PROTOCOL"),
            "HttpRequestMethod": request.method,
            "HttpContentType": request.content_type,
            "HttpContentFormat": request.mimetype,
            "HttpReferrer": request.referrer,
            "HttpUserAgent": str(request.user_agent),
            "HttpRequestXff": request.headers["X-Forwarded-For"],
            "HttpResponseTime": "N/A",
            "HttpHost": request.host,
            "AdditionalFields": {
                "TraceHeaders": {"X-Amzn-Trace-Id": "123testid"},
            },
        }


def test_asim_formatter_get_response_dict():
    """Test that get_response_dict returns a correctly formatted dictionary of response data"""

    response = Response(
        status=200,
        headers={
            "Content-Type": "application/json",
            "Content-Disposition": "attachment; filename=dummy.rtf",
        },
        response='{"key": "value"}',
    )

    response_dict = ASIMFormatter().get_response_dict(response)

    assert response_dict == {
        "EventResult": "Success",
        "EventResultDetails": response.status_code,
        "FileName": "dummy.rtf",
        "HttpStatusCode": response.status_code,
    }


def test_asim_formatter_format():
    """Test full asim formatter including both request and response data"""
    log_record = logging.LogRecord(
        name=__name__,
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="This is a test log message",
        args=(),
        exc_info=None,
    )
    response = Response(
        status=200,
        headers={"Content-Type": "application/json"},
        response='{"key": "value"}',
    )
    log_record.response = response
    app = Flask(__name__)
    log_time = datetime.utcfromtimestamp(log_record.created).isoformat()

    with app.test_request_context(
        method="GET",
        path="/example_route",
        query_string="param1=value1&param2=value2",
        headers={"Content-Type": "application/json", "X-Forwarded-For": "1.1.1.1"},
        data='{"key": "value"}',
    ):
        formatted_log = ASIMFormatter().format(log_record)
        assert formatted_log == json.dumps(
            {
                "EventMessage": log_record.msg,
                "EventCount": 1,
                "EventStartTime": log_time,
                "EventEndTime": log_time,
                "EventType": "HTTPsession",
                "EventSeverity": "Informational",
                "EventOriginalSeverity": log_record.levelname,  # duplicate of above?
                "EventSchema": "WebSession",
                "EventSchemaVersion": "0.2.6",
                "Url": request.url,
                "UrlOriginal": request.url,
                "HttpVersion": request.environ.get("SERVER_PROTOCOL"),
                "HttpRequestMethod": request.method,
                "HttpContentType": request.content_type,
                "HttpContentFormat": request.mimetype,
                "HttpReferrer": request.referrer,
                "HttpUserAgent": str(request.user_agent),
                "HttpRequestXff": request.headers["X-Forwarded-For"],
                "HttpResponseTime": "N/A",
                "HttpHost": request.host,
                "AdditionalFields": {
                    "TraceHeaders": {"X-Amzn-Trace-Id": None},
                },
                "EventResult": "Success",
                "EventResultDetails": response.status_code,
                "FileName": "N/A",
                "HttpStatusCode": response.status_code,
            }
        )
