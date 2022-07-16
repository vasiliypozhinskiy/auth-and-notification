import time
from math import floor
from typing import Optional

from flask import request
from pydantic import BaseModel

from app.core.config import Config
from app.db.redis import redis_rate_limits
from app.utils.exceptions import RequestLimitReached
from app.services.auth_services.jwt_service import JWT_SERVICE
from app.utils.exceptions import InvalidToken


config = Config()


class TokenBucketInfo(BaseModel):
    tokens: int
    last_time_stamp: float


class TokenBucket:
    def __init__(
        self,
        rpm: int,
        session_length_sec: int = config.RATE_LIMIT_SESSION_LEN
    ):
        self.rpm = rpm
        self.storage = redis_rate_limits
        self.session_len = session_length_sec

    def _get_from_storage(self, key: str) -> Optional[TokenBucketInfo]:
        token_info = self.storage.get(key)
        out = None
        if token_info is not None:
            out = TokenBucketInfo.parse_raw(token_info)
        return out

    def pop_token(self, key: str) -> bool:

        token_info = self._get_from_storage(key)
        if token_info is None:
            token_info = self._create_session(key)
            
        if token_info.tokens < 1:
            has_tokens = self._check_and_refill(key)
            if has_tokens < 1:
                return False
        else:
            token_info.tokens = token_info.tokens - 1
            self.storage.setex(key, self.session_len, token_info.json())
        return True

    def _create_session(self, key: str) -> TokenBucketInfo:
        to_storage = TokenBucketInfo(
            tokens=self.rpm,
            last_time_stamp=time.time(),
        )
        self.storage.setex(key, self.session_len, to_storage.json())

        return to_storage

    def _check_and_refill(self, key) -> int:
        token_info = self._get_from_storage(key)
        if token_info is None:
            return 0
        last_token_upd = token_info.last_time_stamp
        sec_passed = time.time() - last_token_upd
        new_tokens = min(
            floor(sec_passed / 60 * self.rpm),
            self.rpm
        )
        if new_tokens > 0:
            token_info.tokens = new_tokens
            self.storage.setex(key, self.session_len, token_info.json())
        return new_tokens


token_bucket = TokenBucket(rpm=config.RATE_LIMIT)


def check_rate_limit(user_id):

    if not token_bucket.pop_token(key=str(user_id)):
        raise RequestLimitReached


def limit_rate(func):
    def wrapper(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        if not access_token:
            return func(*args, **kwargs)
        try:
            payload = JWT_SERVICE.get_access_payload(access_token)
            check_rate_limit(user_id=payload.user_id)
        except InvalidToken:
            pass
        return func(*args, **kwargs)
    return wrapper

