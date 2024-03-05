from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import Response

from fastapi_errors.policies import RFC9457JSONResponseData


def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    data = RFC9457JSONResponseData(exc=exc, request=request)

    return data.to_response()
