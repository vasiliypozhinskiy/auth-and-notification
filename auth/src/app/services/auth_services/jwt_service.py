import uuid
from abc import ABC, abstractmethod
from typing import Tuple, List

from pydantic import BaseModel, ValidationError
import jwt
from jwt.exceptions import DecodeError, InvalidSignatureError

from app.services.storage.storage import user_table
from app.utils.exceptions import InvalidToken
from app.utils.utils import get_now_ms
from app.core.config import (
    SECRET_SIGNATURE,
    REFRESH_TOKEN_EXP,
    ACCESS_TOKEN_EXP,
)


class BasePayload(BaseModel, ABC):
    iat: int
    exp: int
    user_id: uuid.UUID
    roles: List[str]
    is_superuser: bool


class RefreshPayload(BasePayload):
    pass


class AccessPayload(BasePayload):
    pass


class BaseServiceJWT(ABC):

    @abstractmethod
    def generate_tokens(self, user_id) -> Tuple[str, str]:
        pass

    @abstractmethod
    def get_access_payload(self, token) -> AccessPayload:
        pass
    
    @abstractmethod
    def get_refresh_payload(self, token) -> RefreshPayload:
        pass


class ServiceJWT(BaseServiceJWT):

    def __init__(self, access_timeout: int, refresh_timeout: int):
        self.access_timeout = access_timeout
        self.refresh_timeout = refresh_timeout
    
    def generate_tokens(self, user_id) -> Tuple[str, str]:
        return (
            self._get_access_jwt(user_id),
            self._get_refresh_jwt(user_id)
        )

    def get_access_payload(self, token) -> AccessPayload:
        payload = self.decode_token(token)
        try:
            return AccessPayload(**payload)
        except ValidationError:
            raise InvalidToken
    
    def get_refresh_payload(self, token) -> RefreshPayload:
        payload = self.decode_token(token)
        try:
            return RefreshPayload(**payload)
        except ValidationError:
            raise InvalidToken

    @staticmethod
    def decode_token(token) -> dict:
        try:
            payload = jwt.decode(token, SECRET_SIGNATURE, algorithms=["HS256"])
        except (
            DecodeError,
            InvalidSignatureError,
        ):
            raise InvalidToken
        return payload

    @staticmethod
    def encode(payload: BasePayload):
        payload_dict = payload.dict()
        payload_dict['user_id'] = str(payload_dict['user_id'])
        return jwt.encode(
            payload_dict,
            SECRET_SIGNATURE,
            algorithm="HS256",
        )
        
    def _get_refresh_jwt(self, user_id: uuid.UUID):
        roles, is_su = self._get_roles_and_su(user_id)
        now_ms = get_now_ms()
        payload = {
            "exp": now_ms + self.refresh_timeout * 1000,
            "iat": now_ms,
            "user_id": user_id,
            "roles": roles,
            "is_superuser": is_su
        }
        payload = AccessPayload(**payload)
        return self.encode(payload=payload)

    def _get_access_jwt(self, user_id: uuid.UUID) -> str:
        roles, is_su = self._get_roles_and_su(user_id)
        now_ms = get_now_ms()
        payload = {
            "exp": now_ms + self.access_timeout * 1000,
            "iat": now_ms,
            "user_id": user_id,
            "roles": roles,
            "is_superuser": is_su
        }
        payload = AccessPayload(**payload)
        return self.encode(payload=payload)
    
    def refresh_payloads(
        self,
        refresh: RefreshPayload,
        soft: bool = True
    ) -> Tuple[AccessPayload, RefreshPayload]:
        now = get_now_ms()
        # refresh refresh
        if refresh.exp > now:
            refresh.iat = now
            refresh.exp = now + REFRESH_TOKEN_EXP
        
        # build new access
        access = AccessPayload(
            iat=now,
            exp=now + ACCESS_TOKEN_EXP,
            user_id=refresh.user_id, 
            is_superuser=refresh.is_superuser,
            roles=refresh.roles
        )

        # on special key upd roles
        if not soft:
            roles, is_su = self._get_roles_and_su(refresh.user_id)
            access.roles = roles
            refresh.roles = roles
            access.is_superuser = is_su
            access.is_superuser = is_su

        return (access, refresh)

    @staticmethod
    def _get_roles_and_su(user_id: uuid.UUID) -> Tuple[List[str], bool]:
        return user_table.get_roles(user_id=user_id)



JWT_SERVICE = ServiceJWT(
    refresh_timeout=REFRESH_TOKEN_EXP,
    access_timeout=ACCESS_TOKEN_EXP,
)
