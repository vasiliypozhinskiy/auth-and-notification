import os

import redis

settings = {
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": os.getenv("REDIS_PORT", 6739),
}

if os.getenv("REDIS_PASSWORD"):
    settings.update({"password": os.getenv("REDIS_PASSWORD")})

redis_ref_tokens = redis.Redis(db=1, **settings)
redis_revoked_tokens = redis.Redis(db=2, **settings)
redis_log_out_all = redis.Redis(db=3, **settings)
redis_upd_roles = redis.Redis(db=4, **settings)
redis_rate_limits = redis.Redis(db=5, **settings)
redis = redis.Redis(**settings)

def get_redis():
    return redis
