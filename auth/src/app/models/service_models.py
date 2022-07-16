import re
from typing import Optional, List
from uuid import UUID

from datetime import date, datetime
from pydantic import validator
from pydantic.main import BaseModel

from app.utils.exceptions import BadEmailError, BadPasswordError, BadLengthError

PASSWORD_REGEXP = re.compile(
    r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$"
)

# https://html.spec.whatwg.org/multipage/input.html#valid-e-mail-address
EMAIL_REGEXP = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
)


class UserCreds(BaseModel):
    id: Optional[UUID]
    login: str
    password: str
    is_superuser: Optional[bool]
    email: str

    history_entries: Optional[List[UUID]]
    roles: Optional[List[str]]

    @validator("password")
    def validate_password(cls, password):
        if not re.fullmatch(PASSWORD_REGEXP, password):
            raise BadPasswordError
        return password

    @validator("email")
    def validate_email(cls, email):
        if not re.fullmatch(EMAIL_REGEXP, email):
            raise BadEmailError
        return email

    @validator("login")
    def validate_length(cls, field):
        if len(field) > 100:
            raise BadLengthError(message="Wrong length of field. Max 100 characters")
        return field


class UserData(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    birthdate: Optional[date]
    roles: Optional[List[str]]


    @validator("first_name", "last_name")
    def validate_length(cls, field):
        if len(field) > 100:
            raise BadLengthError(message="Wrong length of field. Max 100 characters")
        return field


class User(UserCreds, UserData):
    pass
    

class HistoryEntry(BaseModel):
    id: UUID
    user_agent: str
    created_at: datetime


class LoginTokens(BaseModel):
    access_token: str
    refresh_token: str


class OauthAccess(BaseModel):
    access_token: str
    user_id: Optional[str] = None
    refresh_token: Optional[str] = None


class OauthUserData(BaseModel):
    user_id: str
