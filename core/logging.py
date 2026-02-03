import logging
import threading
from contextlib import contextmanager

_thread_locals = threading.local()

def get_request_id():
    """Return the current request ID or None."""
    return getattr(_thread_locals, 'request_id', None)

def set_request_id(request_id):
    """Set the current request ID in thread locals."""
    _thread_locals.request_id = request_id

def clear_request_id():
    """Clear the current request ID."""
    if hasattr(_thread_locals, 'request_id'):
        del _thread_locals.request_id

class RequestIdFilter(logging.Filter):
    """
    Log filter that injects the current request ID into the log record.
    """
    def filter(self, record):
        record.request_id = get_request_id() or 'no-request-id'
        return True
