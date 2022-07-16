from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

ACCESS_TOKEN = None
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
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    ACCESS_TOKEN = response.body['access_token']

async def test_login_invalid(make_request):
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#222"},
    )

    assert response.status == HTTPStatus.FORBIDDEN


async def test_check_authorized(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK


async def test_check_authorized_inv_token(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": "invalid_token"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_logout(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "logout",
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK


async def test_check_notauthorized(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED
