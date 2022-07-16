from http import HTTPStatus

import grpc
import pytest

import auth_pb2
import auth_pb2_grpc
from settings import Settings

SETTINGS = Settings()

# All test coroutines will be treated as marked with this decorator.
pytestmark = pytest.mark.asyncio

SU_ACCESS_TOKEN = None

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
NEW_ROLE = 'NEW_ROLE'


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
    )

    assert response.status == HTTPStatus.OK
    ACCESS_TOKEN = response.body['access_token']
    REFRESH_TOKEN = response.body['refresh_token']


async def test_login_su(make_request):
    global SU_ACCESS_TOKEN
    response = await make_request("post")(
        "login/",
        json={"login": "superuser", "password": SETTINGS.super_user_password},
    )

    assert response.status == HTTPStatus.OK
    SU_ACCESS_TOKEN = response.body['access_token']


async def test_check_auth(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
    assert response.body['roles'] == []


async def test_add_role(make_request):
    global SU_ACCESS_TOKEN
    global NEW_ROLE
    response = await make_request("post")(
        f"role/{NEW_ROLE}",
        headers={"Authorization": SU_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.CREATED


async def test_list_roles(make_request):
    global NEW_ROLE
    response = await make_request("get")(
        f"role/role_list/",
    )

    assert response.status == HTTPStatus.OK
    assert response.body == {"role_list": [NEW_ROLE]}


async def test_assign_role(make_request):
    global SU_ACCESS_TOKEN
    global NEW_ROLE
    global USER_ID

    response = await make_request("post")(
        f"user_add_role/{USER_ID}/{NEW_ROLE}",
        headers={"Authorization": SU_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK


async def test_check_token(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_refresh_after_add(make_request):

    global REFRESH_TOKEN
    global ACCESS_TOKEN

    response = await make_request("post")(
        f"refresh/",
        json={"refresh_token": REFRESH_TOKEN},
    )

    assert response.status == HTTPStatus.OK
    ACCESS_TOKEN = response.body['access_token']
    REFRESH_TOKEN = response.body['refresh_token']


async def test_check_roles_after_refresh_add(make_request):
    global ACCESS_TOKEN
    global NEW_ROLE

    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
    assert response.body['roles'] == [NEW_ROLE]


async def test_check_authorized(make_request):
    global ACCESS_TOKEN
    global NEW_ROLE
    with grpc.insecure_channel('auth:50051') as channel:
        stub = auth_pb2_grpc.AuthStub(channel)
        response = stub.Authorize(
            auth_pb2.AuthorizeRequest(),
            metadata=(
                ('access_token', ACCESS_TOKEN),
            )
        )
    assert response.roles == [NEW_ROLE]


async def test_rm_role(make_request):
    global SU_ACCESS_TOKEN
    global NEW_ROLE
    global USER_ID

    response = await make_request("delete")(
        f"user_delete_role/{USER_ID}/{NEW_ROLE}",
        headers={"Authorization": SU_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK


async def test_check_token_after_rm(make_request):
    global ACCESS_TOKEN
    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_refresh_after_rm(make_request):

    global REFRESH_TOKEN
    global ACCESS_TOKEN

    response = await make_request("post")(
        f"refresh/",
        json={"refresh_token": REFRESH_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
    ACCESS_TOKEN = response.body['access_token']
    REFRESH_TOKEN = response.body['refresh_token']


async def test_refresh_after_rm_wrong_agent(make_request):

    global REFRESH_TOKEN
    global ACCESS_TOKEN

    response = await make_request("post")(
        f"refresh/",
        json={"refresh_token": REFRESH_TOKEN},
        headers={"User-Agent": "agent_2"}
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_check_roles_after_refresh_rm(make_request):
    global ACCESS_TOKEN
    global NEW_ROLE

    response = await make_request("post")(
        "authorize/",
        headers={"Authorization": ACCESS_TOKEN, "User-Agent": "agent_1"},
    )

    assert response.status == HTTPStatus.OK
    assert response.body['roles'] == []


async def test_rm_role_form_list_un_auth(make_request):
    global NEW_ROLE
    response = await make_request("delete")(
        f"role/{NEW_ROLE}",
    )
    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_rm_role_form_list(make_request):
    global NEW_ROLE
    global SU_ACCESS_TOKEN
    response = await make_request("delete")(
        f"role/{NEW_ROLE}",
        headers={"Authorization": SU_ACCESS_TOKEN, "User-Agent": "agent_1"},
    )
    assert response.status == HTTPStatus.OK


async def test_list_roles_after_rm(make_request):
    global NEW_ROLE
    response = await make_request("get")(
        f"role/role_list/",
    )

    assert response.status == HTTPStatus.OK
    assert response.body == {"role_list": []}