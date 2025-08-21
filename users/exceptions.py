from typing import Any

from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework import status
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    response = exception_handler(exc, context)

    default_message = "An error occurred"

    if response is not None:
        errors: Any
        if isinstance(exc, ValidationError):
            message = "Validation failed"
            errors = response.data
        elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
            message = "Authentication failed"
            errors = response.data
        elif isinstance(exc, (PermissionDenied, DjangoPermissionDenied)):
            message = "Permission denied"
            errors = response.data
        elif isinstance(exc, NotFound):
            message = "Not found"
            errors = response.data
        else:
            # Generic APIException or others already handled by DRF
            if isinstance(response.data, dict) and "detail" in response.data:
                message = str(response.data.get("detail"))
            else:
                message = default_message
            errors = response.data

        # Wrap into a consistent envelope
        wrapped = {"message": message}
        if errors is not None:
            wrapped["errors"] = errors
        response.data = wrapped
        return response

    # Unhandled exceptions → fall back to 500 with a generic message
    return Response({"message": default_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


