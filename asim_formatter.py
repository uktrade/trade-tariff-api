import json
import logging
import os
from datetime import datetime

from flask import Request
from flask import Response
from flask import has_request_context
from flask import request


class ASIMFormatter(logging.Formatter):
    def _get_event_result(self, response: Response) -> str:
        event_result = "Success" if response.status_code < 400 else "Failure"

        return event_result

    def _get_file_name(self, response: Response) -> str:
        content_disposition = response.headers.get("Content-Disposition")
        if content_disposition:
            search_result = re.search("filename=(.*)[;]", content_disposition)
            if search_result:
                return search_result.group(1)
            else:
                return "N/A"

        return "N/A"

    def _get_event_severity(self, log_level: str) -> str:
        event_map = {
            "DEBUG": "Informational",
            "INFO": "Informational",
            "WARNING": "Low",
            "ERROR": "Medium",
            "CRITICAL": "High",
        }
        return event_map[log_level]

    def get_log_dict(self, record: logging.LogRecord) -> dict:
        log_time = datetime.utcfromtimestamp(record.created).isoformat()

        return {
            "EventMessage": record.msg,
            "EventCount": 1,
            "EventStartTime": log_time,
            "EventEndTime": log_time,
            "EventType": "HTTPsession",
            "EventSeverity": self._get_event_severity(record.levelname),
            "EventOriginalSeverity": record.levelname,  # duplicate of above?
            "EventSchema": "WebSession",
            "EventSchemaVersion": "0.2.6",
        }

    def get_request_dict(self, request: Request) -> dict:
        request_dict = {
            "Url": request.url,
            "UrlOriginal": request.url,
            "HttpVersion": request.environ.get("SERVER_PROTOCOL"),
            "HttpRequestMethod": request.method,
            "HttpContentType": request.content_type,
            "HttpContentFormat": request.mimetype,
            "HttpReferrer": request.referrer,
            "HttpUserAgent": str(request.user_agent),
            "HttpRequestXff": request.headers.get("X-Forwarded-For"),
            "HttpResponseTime": "N/A",
            "HttpHost": request.host,
            "AdditionalFields": {
                "TraceHeaders": {},
            },
        }

        for trace_header in os.environ.get("DLFA_TRACE_HEADERS", ("X-Amzn-Trace-Id",)):
            request_dict["AdditionalFields"]["TraceHeaders"][trace_header] = (
                request.headers.get(trace_header, None)
            )

        return request_dict

    def get_response_dict(self, response: Response) -> dict:
        return {
            "EventResult": self._get_event_result(response),
            "EventResultDetails": response.status_code,
            "FileName": self._get_file_name(response),
            "HttpStatusCode": response.status_code,
        }

    def format(self, record: logging.LogRecord) -> str:
        log_dict = self.get_log_dict(record)

        if has_request_context():
            request_dict = self.get_request_dict(request)
            log_dict = log_dict | request_dict

        if hasattr(record, "response"):
            response_dict = self.get_response_dict(record.response)
            log_dict = log_dict | response_dict

        return json.dumps(log_dict)
