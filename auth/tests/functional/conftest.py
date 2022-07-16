import asyncio
import os
import sys
from dataclasses import dataclass
from typing import AsyncGenerator, Optional

import aiohttp
import aiopg
import aioredis
import pytest
import pytest_asyncio

from .settings import Settings

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

SETTINGS = Settings()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="module")
async def pg_connection() -> AsyncGenerator[aiopg.connection.Connection, None]:
    # os.system("python3 main_build_tables.py")
    dsn = "dbname={dbname} user={user} password={password} host={host} port={port}".format(
        dbname=SETTINGS.pg_name,
        user=SETTINGS.pg_user,
        password=SETTINGS.pg_password,
        host=SETTINGS.pg_host,
        port=SETTINGS.pg_port
    )
    async with aiopg.create_pool(dsn) as pool:
        async with pool.acquire() as conn:

            yield conn

            async with conn.cursor() as cur:
                await cur.execute("DELETE FROM auth.login_history;")
                await cur.execute("DELETE FROM auth.role;")
                await cur.execute("DELETE FROM auth.user_data;")
                await cur.execute("DELETE FROM auth.user WHERE login != 'superuser';")


@pytest_asyncio.fixture(scope="module")
async def redis() -> AsyncGenerator[aiopg.connection.Connection, None]:
    redis_table = aioredis.Redis(host=SETTINGS.redis_host, port=SETTINGS.redis_port, password=SETTINGS.redis_password)

    yield None

    await redis_table.flushall()


@pytest_asyncio.fixture(scope="module")
async def session(pg_connection, redis):
    session = aiohttp.ClientSession(headers={"Cache-Control": "no-store"})

    yield session

    await session.close()


@dataclass
class HTTPResponse:
    body: dict
    status: int


@pytest_asyncio.fixture(scope="module")
def make_request(session):
    """Post request maker"""

    def wrapper(type: str = "get"):
        async def inner(
            method: str, json: Optional[dict] = None, headers: Optional[dict] = None
        ) -> HTTPResponse:
            url = f"http://{SETTINGS.nginx_host}:{SETTINGS.nginx_port}/auth/api/v1/{method}"  # noqa: E501
            async with getattr(session, type)(
                url, json=json, headers=headers
            ) as response:
                try:
                    body = await response.json()
                except aiohttp.client_exceptions.ContentTypeError:
                    body = await response.text()
                return HTTPResponse(
                    body=body,
                    status=response.status,
                )

        return inner

    return wrapper
