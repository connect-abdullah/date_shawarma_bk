from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool = Field(default=True)
    message: str = Field(default="")
    data: T | None = Field(default=None)
    errors: Any | None = Field(default=None)


def ok(data: Any = None, message: str = "") -> APIResponse[Any]:
    return APIResponse(success=True, message=message, data=data)


def fail(message: str, errors: Any | None = None) -> APIResponse[Any]:
    return APIResponse(success=False, message=message, errors=errors)
