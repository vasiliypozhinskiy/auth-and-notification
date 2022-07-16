import time
from http import HTTPStatus

import pytest

from settings import Settings

SETTINGS = Settings()

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

SU_ACCESS_TOKEN = None

U1_FIRST_ACCESS_TOKEN = None
U1_SECOND_ACCESS_TOKEN = None
U1_THIRD_ACCESS_TOKEN = None

USER_ID_FIRST = None
USER_FIRST = {
  "email": "example@email.com",
  "first_name": "Ivan",
  "last_name": "Ivan",
  "login": "login",
  "middle_name": "Ivan",
  "password": "123qweQWE!@#",
}

U2_FIRST_ACCESS_TOKEN = None
USER_ID_SECOND = None
USER_SECOND = {
  "email": "1example@email.com",
  "first_name": "Ivan",
  "last_name": "Ivan",
  "login": "login1",
  "middle_name": "Ivan",
  "password": "123qweQWE!@#",
}

async def test_user_create(make_request):
    global USER_FIRST
    global USER_ID_FIRST

    response = await make_request("post")(
        "user/",
        json=USER_FIRST,
    )
    assert response.status == HTTPStatus.CREATED
    USER_ID_FIRST = response.body["user_id"]


async def test_user_create_another(make_request):
    global USER_ID_SECOND
    global USER_SECOND

    response = await make_request("post")(
        "user/",
        json=USER_SECOND,
    )
    assert response.status == HTTPStatus.CREATED
    USER_ID_SECOND = response.body["user_id"]


async def test_login(make_request):
    global U1_FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    U1_FIRST_ACCESS_TOKEN = response.body['access_token']


async def test_login_su(make_request):
    global SU_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "superuser", "password": SETTINGS.super_user_password},
    )

    assert response.status == HTTPStatus.OK
    SU_ACCESS_TOKEN = response.body['access_token']


async def test_check_authorized(make_request):
    global U1_FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": U1_FIRST_ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK

async def test_login_again(make_request):
    global U1_SECOND_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    U1_SECOND_ACCESS_TOKEN = response.body['access_token']


async def test_login_second_user(make_request):
    global U2_FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login1", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    U2_FIRST_ACCESS_TOKEN = response.body['access_token']


async def test_logout_all_wrong_itself_on_id(make_request):
    global U1_FIRST_ACCESS_TOKEN
    global USER_ID_FIRST
    response = await make_request("post")(
        f"logout_all/{USER_ID_FIRST}",
        headers={"Authorization": U1_FIRST_ACCESS_TOKEN},
    )
    assert response.status == HTTPStatus.FORBIDDEN

async def test_logout_all_wrong_other_on_id(make_request):
    global U2_FIRST_ACCESS_TOKEN
    global USER_ID_FIRST
    response = await make_request("post")(
        f"logout_all/{USER_ID_FIRST}",
        headers={"Authorization": U2_FIRST_ACCESS_TOKEN},
    )
    assert response.status == HTTPStatus.FORBIDDEN
    
async def test_logout_all(make_request):
    global SU_ACCESS_TOKEN
    global USER_ID_FIRST
    response = await make_request("post")(
        f"logout_all/{USER_ID_FIRST}",
        headers={"Authorization": SU_ACCESS_TOKEN},
    )
    assert response.status == HTTPStatus.OK


async def test_check_notauthorized_first_agent(make_request):
    global U1_FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": U1_FIRST_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_check_notauthorized_second_agent(make_request):
    global U1_SECOND_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": U1_SECOND_ACCESS_TOKEN, "User-Agent": "agent_2"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_check_authorized_second_user(make_request):
    global U2_FIRST_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": U2_FIRST_ACCESS_TOKEN, "User-Agent": "agent_2"},
    )

    assert response.status == HTTPStatus.OK


async def test_log_in_third(make_request):
    global U1_THIRD_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "login", "password": "123qweQWE!@#"},
    )

    assert response.status == HTTPStatus.OK
    U1_THIRD_ACCESS_TOKEN = response.body['access_token']


async def test_check_after_first_logged_in(make_request):

    global U1_THIRD_ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": U1_THIRD_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
