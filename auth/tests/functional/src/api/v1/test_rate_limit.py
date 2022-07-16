from http import HTTPStatus
import asyncio

import pytest


pytestmark = pytest.mark.asyncio

USER_ID = "14"
ACCESS_TOKEN = None
USER = {
  "email": "example@email.com",
  "first_name": "Ivan",
  "last_name": "Ivan",
  "login": "login",
  "birthdate": "2000-01-20",
  "password": "123qweQWE!@#",
}


async def test_user_create(make_request):
    global USER_ID
    global USER

    response = await make_request("post")(
        "user/",
        json=USER,
    )
    assert response.status == HTTPStatus.CREATED
    USER_ID = response.body["user_id"]


async def test_login(make_request):
    global ACCESS_TOKEN
    global USER

    response = await make_request("post")(
        "login/",
        json={"login": USER["login"], "password": USER["password"]},
    )

    assert response.status == HTTPStatus.OK
    ACCESS_TOKEN = response.body['access_token']


async def test_rate_limit(make_request):
    bunch_of_reqs = [
        make_request('post')(
            "authorize/",
            headers={"Authorization": ACCESS_TOKEN},
        ) for _ in range(21)
    ]

    responses = await asyncio.gather(*bunch_of_reqs)
    responses = [r.status for r in responses]
    assert HTTPStatus.TOO_MANY_REQUESTS in responses