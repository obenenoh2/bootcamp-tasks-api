import logging
import uuid
from pythonjsonlogger import jsonlogger
from fastapi import Request
from contextvars import ContextVar

# Use a different name to avoid confusion
_logger = logging.getLogger(__name__)

trace_id_var: ContextVar[str] = ContextVar('trace_id', default='')

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['level'] = record.levelname
        log_record['name'] = record.name
        log_record['trace_id'] = trace_id_var.get()

# Configure logger
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s %(trace_id)s')
logHandler.setFormatter(formatter)
_logger.addHandler(logHandler)
_logger.setLevel(logging.INFO)

async def logging_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id", str(uuid.uuid4()))
    token = trace_id_var.set(trace_id)
    try:
        _logger.info(f"Request started", extra={'method': request.method, 'path': request.url.path})
        response = await call_next(request)
        _logger.info(f"Request completed", extra={'status_code': response.status_code})
        return response
    finally:
        trace_id_var.reset(token)
