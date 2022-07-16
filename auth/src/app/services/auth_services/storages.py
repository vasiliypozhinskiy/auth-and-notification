from abc import ABC, abstractmethod
import uuid

import redis

from app.db.redis import redis_ref_tokens


class BaseRefreshTokenStorage(ABC):

    exp_time: int
    
    @abstractmethod
    def add_token(self, token):
        pass
    
    @abstractmethod
    def revoke_token(self, token):
        pass

    @abstractmethod
    def get_token(self, **kwargs):
        pass


class RedisRefreshTokenStorage(BaseRefreshTokenStorage):

    def __init__(self, exp_time: int, storage: redis.Redis):
        self.exp_time = exp_time
        self.storage = storage
    
    
    def get_token(self, user_id: uuid.UUID, agent: str, ) -> dict:
        value = self.storage.get(self._encode(user_id=user_id, agent=agent))
        return value.decode() if value is not None else None
    
    def add_token(self, user_id: uuid.UUID, agent: str, token: str):
        self.storage.setex(
            self._encode(user_id=user_id, agent=agent),
            self.exp_time,
            token,
        )
    
    def revoke_token(self, user_id: uuid.UUID, agent: str):
        self.storage.delete(self._encode(user_id=user_id, agent=agent))

    @staticmethod
    def _encode(user_id: uuid.UUID, agent: str) -> str:
        return "__".join([agent, str(user_id)])


REF_TOK_STORAGE = RedisRefreshTokenStorage(exp_time=600, storage = redis_ref_tokens)