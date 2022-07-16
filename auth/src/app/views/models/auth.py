from typing import List, Optional

from pydantic.main import BaseModel


class AuthReqView(BaseModel):
    login: str
    password: str
    code: Optional[str]


class AuthRespView(BaseModel):
    access_token: str
    refresh_token: str


class AuthRefreshReqView(BaseModel):
    refresh_token: str


class AuthRefreshRespView(BaseModel):
    access_token: str
    refresh_token: str


class AuthorizeResponse(BaseModel):
    roles: List[str]
    is_superuser: bool
