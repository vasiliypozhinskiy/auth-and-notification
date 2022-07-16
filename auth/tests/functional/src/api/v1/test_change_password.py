from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio
SECOND_ACCESS_TOKEN = None
SECOND_REFRESH_TOKEN = None

FIRST_ACCESS_TOKEN = None
FIRST_REFRESH_TOKEN = None
USER_ID = None
USER = {
  "email": "example@email.com",
  "first_name": "Ivan",
  "last_name": "Ivan",
  "login": "login",
  "birthdate": "2000-01-20",
  "password": "123qweQWE!@#",
}
NEW_PASSWORD = "123qweQWE!@#111"


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
    global FIRST_ACCESS_TOKEN
    global FIRST_REFRESH_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": USER["login"], "password": USER['password']},
        headers={"User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
    FIRST_ACCESS_TOKEN = response.body['access_token']
    FIRST_REFRESH_TOKEN = response.body['refresh_token']


async def test_login_again(make_request):
    global SECOND_ACCESS_TOKEN
    global SECOND_REFRESH_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
        headers={"User-Agent": "agent_2"},
    )

    assert response.status == HTTPStatus.OK
    SECOND_ACCESS_TOKEN = response.body['access_token']
    SECOND_REFRESH_TOKEN = response.body['refresh_token']


async def test_change_password(make_request):
    global FIRST_ACCESS_TOKEN 
    global USER_ID
    global NEW_PASSWORD
    global USER

    response = await make_request("put")(
        f"user/{USER_ID}/change_password",
        headers={"Authorization": FIRST_ACCESS_TOKEN},
        json={
            "new_password": NEW_PASSWORD,
            "old_password": USER['password'],
        },
    )
    assert response.status == HTTPStatus.OK


async def test_check_authorized(make_request):
    global SECOND_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": SECOND_ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_refresh_after_passw_change(make_request):

    global SECOND_REFRESH_TOKEN

    response = await make_request("post")(
        f"refresh/",
        json={"refresh_token": SECOND_REFRESH_TOKEN},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED

