from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

ACCESS_TOKEN = None
REFRESH_TOKEN = None
USER_ID = None
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
    global REFRESH_TOKEN

    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
        headers={"User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
    ACCESS_TOKEN = response.body['access_token']
    REFRESH_TOKEN = response.body['refresh_token']


async def test_check_auth(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK


async def test_refresh(make_request):

    global REFRESH_TOKEN
    global ACCESS_TOKEN

    response = await make_request("post")(
        f"refresh/",
        json={"refresh_token": REFRESH_TOKEN},
        headers={"User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
    ACCESS_TOKEN = response.body['access_token']
    REFRESH_TOKEN = response.body['refresh_token']


async def test_check_auth_with_new(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK


async def test_logout_all(make_request):
    global ACCESS_TOKEN

    response = await make_request("post")(
        "logout_all/",
        headers={"Authorization": ACCESS_TOKEN},
    )
    assert response.status == HTTPStatus.OK


async def test_refresh_after_logout(make_request):

    global REFRESH_TOKEN
    global ACCESS_TOKEN

    response = await make_request("post")(
        f"refresh/",
        json={"refresh_token": REFRESH_TOKEN},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED