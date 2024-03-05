from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, computed_field
from typing import Optional, Any

BASE_VALIDATION_ERROR_TYPE = 'https://errors.pydantic.dev/2.4/v/'


class RFC9457Error(BaseModel):
    loc: list[str | int]
    detail: str


class RFC9457JSONResponseData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    request: Request
    exc: RequestValidationError
    status_code: Optional[int] = Field(alias='status_code', default=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @computed_field
    @property
    def type(self) -> str:
        return f"{self._single_error['url'] if self._single_error else BASE_VALIDATION_ERROR_TYPE}"

    @computed_field
    @property
    def title(self) -> str:
        return f"{self._single_error['msg'] if self._single_error else 'Payload validation failed'}"

    @computed_field
    @property
    def instance(self) -> str:
        return self.request.url.path

    @computed_field
    @property
    def errors(self) -> list[RFC9457Error]:
        return [RFC9457Error(loc=list(error['loc']), detail=error['msg']) for error in self.exc.errors()]

    @property
    def _single_error(self) -> Optional[dict[str, Any]]:
        if len(self.exc.errors()) == 1:
            return self.exc.errors()[0]

    def to_response(self, *args, **kwargs) -> JSONResponse:
        return JSONResponse(
            content=self.model_dump(include={'type', 'title', 'status_code', 'instance', 'errors'}),
            status_code=self.status_code,
            *args, **kwargs,
        )
