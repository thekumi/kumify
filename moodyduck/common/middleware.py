import logging
import traceback as tb

from django.core.exceptions import PermissionDenied
from django.http import Http404

from .models import ErrorLog

logger = logging.getLogger(__name__)


class ErrorLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, (Http404, PermissionDenied)):
            return

        try:
            ErrorLog.objects.create(
                path=request.path,
                method=request.method,
                user=request.user if request.user.is_authenticated else None,
                exception_type=type(exception).__qualname__,
                exception_value=str(exception),
                traceback="".join(
                    tb.format_exception(
                        type(exception), exception, exception.__traceback__
                    )
                ),
            )
        except Exception as e:  # noqa: BLE001
            logger.debug("ErrorLoggingMiddleware: failed to persist exception: %s", e)
