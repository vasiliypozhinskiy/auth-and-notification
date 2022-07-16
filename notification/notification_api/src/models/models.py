from typing import Any
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(value: list | dict, *, default: list | dict) -> Any:
    return orjson.dumps(value, default=default).decode()


class BaseOrJSONModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class AuthRequest(BaseOrJSONModel):
    event: str
    user_id: UUID
    confirmation_link: str


class UgcRequest(BaseOrJSONModel):
    event: str
    user_id: UUID
    content_id: UUID


class AdminRequest(BaseOrJSONModel):
    event: str
    user_id: list[UUID]
    template_id: str
