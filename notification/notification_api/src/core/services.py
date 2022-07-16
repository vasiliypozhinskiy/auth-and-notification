import asyncio

import aiohttp
import aio_pika
from aiohttp.client_exceptions import ContentTypeError
from fastapi import Header, Request
from motor import motor_asyncio

from core.config import Config

config = Config()

aiohttp_session = aiohttp.ClientSession | None
mongo_client = motor_asyncio.AsyncIOMotorClient | None
rabbit_connection = aio_pika.Connection | None


def get_aiohttp_session():
    return aiohttp_session


def get_mongo_client() -> motor_asyncio.AsyncIOMotorClient | None:
    return mongo_client


def get_rabbit_connection() -> aio_pika.Connection | None:
    return rabbit_connection


async def task(session, url):
    try:
        async with session.get(url=url) as response:
            data = await response.json()
            if not data["notification"]:
                return
            return data
    except ContentTypeError:
        return None


async def get_data_from_auth(request_data: Request,
                             x_request_id: str | None = Header(None)):
    async with aiohttp.ClientSession(
            headers={"X-Request-Id": x_request_id}
    ) as session:

        data = await request_data.json()

        if isinstance(data["user_id"], list):
            tasks = [task(
                session=session,
                url=config.auth_url + str(_id)) for _id in data["user_id"]]
        else:
            tasks = [task(
                session=session,
                url=config.auth_url + str(data["user_id"]))]

        users_data = await asyncio.gather(*tasks)

        return users_data
