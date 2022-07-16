from typing import Any
from uuid import UUID

from pydantic import BaseModel
import orjson


def orjson_dumps(value: list | dict, *, default: list | dict) -> Any:
    return orjson.dumps(value, default=default).decode()


class BaseOrJSONModel(BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class AdminRequest(BaseOrJSONModel):
    user_id: list[UUID]
    template: str
    variables: list[str]
