from abc import abstractmethod, ABC
import uuid

import redis

from app.utils.utils import get_now_ms, trace_it
from app.utils.exceptions import InvalidToken
from app.db.redis import (
    redis_revoked_tokens,
    redis_log_out_all,
    redis_upd_roles
)
from app.core.config import REFRESH_TOKEN_EXP, ACCESS_TOKEN_EXP
from app.services.auth_services.jwt_service import JWT_SERVICE


class BaseBlackList(ABC):
    @abstractmethod
    def add(self, **kwargs) -> None:
        pass

    @abstractmethod
    def is_ok(self, **kwargs) -> bool:
        pass


class TokenBlackList(BaseBlackList):
    def __init__(self, storage: redis.Redis, exp_time: int, reason: str = ""):
        self.reason = reason
        self.storage = storage
        self.exp_time = exp_time

    @trace_it
    def add(self, token: str) -> None:
        if token != "":
            self.storage.setex(
                token,
                self.exp_time,
                self.reason
            )

    @trace_it
    def is_ok(self, token: str) -> bool:
        return not bool(self.storage.exists(token))


class UserIDBlackList(BaseBlackList):
    def __init__(self, storage: redis.Redis, exp_time: int):
        self.storage = storage
        self.exp_time = exp_time

    @trace_it
    def add(self, user_id: uuid.UUID) -> None:
        
        self.storage.setex(
            str(user_id),
            REFRESH_TOKEN_EXP,
            get_now_ms(),
        )

    @trace_it
    def is_ok(self, access_token: str) -> bool:
        payload = JWT_SERVICE.get_access_payload(access_token)
        if payload is None:
            raise InvalidToken
        else:
            set_time = self.storage.get(str(payload.user_id))
            if set_time is None:
                return True  # no request to logout for this user
            set_time = int(set_time.decode())
            if payload.iat < set_time:
                return False  # logged in after request on logout
            return True


REVOKED_ACCESS = TokenBlackList(
    storage=redis_revoked_tokens,
    exp_time=ACCESS_TOKEN_EXP,
    reason='revoked',
)
LOG_OUT_ALL = UserIDBlackList(
    storage=redis_log_out_all,
    exp_time=REFRESH_TOKEN_EXP,
)
ROLES_UPDATE = UserIDBlackList(
    storage=redis_upd_roles,
    exp_time=REFRESH_TOKEN_EXP,
)