from typing import Optional, Any, Union, Mapping

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, computed_field
from starlette.background import BackgroundTask

BASE_VALIDATION_ERROR_TYPE = 'https://errors.pydantic.dev/2.4/v/'


class RFC9457Error(BaseModel):
    loc: list[Union[str, int]]
    detail: str


class RFC9457JSONResponseData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    request: Request
    exc: RequestValidationError
    status_code: int = Field(alias='status_code', default=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @computed_field
    def type(self) -> str:
        return f"{self._single_error['url'] if self._single_error else BASE_VALIDATION_ERROR_TYPE}"

    @computed_field
    def title(self) -> str:
        return f"{self._single_error['msg'] if self._single_error else 'Payload validation failed'}"

    @computed_field
    def instance(self) -> str:
        return self.request.url.path

    @computed_field
    def errors(self) -> list[RFC9457Error]:
        return [RFC9457Error(loc=list(error['loc']), detail=error['msg']) for error in self.exc.errors()]

    @property
    def _single_error(self) -> Optional[dict[str, Any]]:
        errors = self.exc.errors()
        if type(errors) is list and len(errors) == 1:
            return errors[0]  # type: ignore[no-any-return]
        return None

    def to_response(self, headers: Union[Mapping[str, str], None] = None,
                    media_type: Union[str, None] = None,
                    background: Union[BackgroundTask, None] = None, ) -> JSONResponse:
        return JSONResponse(
            content=self.model_dump(include={'type', 'title', 'status_code', 'instance', 'errors'}),
            status_code=self.status_code,
            headers=headers,
            media_type=media_type,
            background=background
        )
