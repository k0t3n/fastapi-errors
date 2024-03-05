from fastapi import Request
from fastapi.exceptions import ValidationException

from fastapi_errors.policies import RFC9457JSONResponseData


async def validation_exception_handler(request: Request, exc: ValidationException):
    data = RFC9457JSONResponseData(exc=exc, request=request)

    return data.to_response()
