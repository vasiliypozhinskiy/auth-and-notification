import bcrypt
import math
import time

from opentelemetry import trace
tracer = trace.get_tracer(__name__)


def hide_password(dict_):
    if dict_.get("password"):
        dict_.update({"password": "****"})
    return dict_


def hash_password(password: str) -> bytes:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt)


def check_password(password: str, hashed_password: str) -> bool:
    if bcrypt.checkpw(password.encode(), hashed_password.encode()):
        return True
    else:
        return False


def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d


def get_now_ms() -> int:
    return math.floor((time.time() * 1000))


def trace_it(func):
    def wrapper(*args, **kwargs):
        with tracer.start_as_current_span(
            f"{func.__module__}:{func.__name__}"
        ):
            return func(*args, **kwargs)
    return wrapper