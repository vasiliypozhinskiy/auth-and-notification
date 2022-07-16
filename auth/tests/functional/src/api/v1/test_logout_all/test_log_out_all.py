import time
from http import HTTPStatus

import pytest

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio
FIRST_ACCESS_TOKEN = None
SECOND_ACCESS_TOKEN = None
THIRD_ACCESS_TOKEN = None

USER_ID = None
USER = {
  "email": "example@email.com",
  "first_name": "Ivan",
  "last_name": "Ivan",
  "login": "login",
  "middle_name": "Ivan",
  "password": "123qweQWE!@#",
}

U2_ACCESS_TOKEN = None
USER2 = {
  "email": "example1@email.com",    
  "first_name": "Ivan",
  "last_name": "Ivan",
  "login": "login1",
  "middle_name": "Ivan",
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

    
async def test_user2_create(make_request):
    global USER2

    response = await make_request("post")(
        "user/",
        json=USER2,
    )
    assert response.status == HTTPStatus.CREATED


async def test_login(make_request):
    global FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    FIRST_ACCESS_TOKEN = response.body['access_token']


async def test_login_u2(make_request):
    global U2_ACCESS_TOKEN
    global USER2
    response = await make_request("post")(
        "login/",
        json={"login": USER2["login"], "password": USER2["password"]},
    )

    assert response.status == HTTPStatus.OK
    U2_ACCESS_TOKEN = response.body['access_token']


async def test_check_authorized(make_request):
    global FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": FIRST_ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK

async def test_login_again(make_request):
    global SECOND_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    SECOND_ACCESS_TOKEN = response.body['access_token']


async def test_logout_all(make_request):
    global SECOND_ACCESS_TOKEN
    response = await make_request("post")(
        "logout_all/",
        headers={"Authorization": SECOND_ACCESS_TOKEN},
    )
    assert response.status == HTTPStatus.OK


async def test_check_notauthorized_first_agent(make_request):
    global FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": FIRST_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_check_notauthorized_second_agent(make_request):
    global SECOND_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": SECOND_ACCESS_TOKEN, "User-Agent": "agent_2"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_log_in_third(make_request):
    global THIRD_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    THIRD_ACCESS_TOKEN = response.body['access_token']


async def test_check_after_first_logged_in(make_request):

    global THIRD_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": THIRD_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK

async def test_log_out_u2(make_request):
    global U2_ACCESS_TOKEN
    response = await make_request("post")(
        "logout_all/",
        headers={"Authorization": U2_ACCESS_TOKEN},
    )
    assert response.status == HTTPStatus.OK

async def test_check_after_first_logged_in_after_other_logout(make_request):

    global THIRD_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": THIRD_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK