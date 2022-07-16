from http import HTTPStatus
import copy
import pytest
import json

from pydantic import BaseModel
from pydantic.types import date

# All test coroutines will be treated as marked with this decorator.
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

NEW_USER_DATA = {
  "email": "example@email.com",
  "first_name": "Ivan1",
  "last_name": "Ivan1",
  "login": "login1",
  "birthdate": "2000-04-30",
}


class UserResponse(BaseModel):
    email: str
    first_name: str
    last_name: str
    login: str
    birthdate: date


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


async def test_user_create_again(make_request):
    global USER

    response = await make_request("post")(
        "user/",
        json=USER,
    )
    assert response.status == HTTPStatus.CONFLICT


async def test_user_data(make_request):
    global ACCESS_TOKEN
    global USER_ID
    global USER
    _user = copy.deepcopy(USER)
    _user['id'] = USER_ID
    user_to_view = UserResponse.parse_obj(_user)

    response = await make_request("get")(
        f"user/{USER_ID}",
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK
    assert response.body == json.loads(user_to_view.json())


async def test_user_data_no_token(make_request):
    
    global USER_ID
    global USER
    _user = copy.deepcopy(USER)
    _user['id'] = USER_ID
    user_to_view = UserResponse.parse_obj(_user)

    response = await make_request("get")(
        f"user/{USER_ID}",
    )

    assert response.status == HTTPStatus.OK
    assert response.body == json.loads(user_to_view.json())


async def test_user_data_inv_token(make_request):
    
    global USER_ID
    global USER
    _user = copy.deepcopy(USER)
    _user['id'] = USER_ID
    user_to_view = UserResponse.parse_obj(_user)

    response = await make_request("get")(
        f"user/{USER_ID}",
        headers={"Authorization": "ACCESS_TOKEN"},
    )

    assert response.status == HTTPStatus.OK
    assert response.body == json.loads(user_to_view.json())


# async def test_update_user_data_no_token(make_request):

#     global USER_ID
#     global NEW_USER_DATA
#     global ACCESS_TOKEN

#     response = await make_request("patch")(
#         f"user/{USER_ID}",
#         json=NEW_USER_DATA,
#     )

#     assert response.status == HTTPStatus.UNAUTHORIZED


async def test_update_user_data(make_request):

    global USER_ID
    global NEW_USER_DATA
    global ACCESS_TOKEN

    response = await make_request("patch")(
        f"user/{USER_ID}",
        json=NEW_USER_DATA,
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK


async def test_user_data_after_upd(make_request):
    pass
    global USER_ID
    global NEW_USER_DATA

    response = await make_request("get")(
        f"user/{USER_ID}",
    )

    new_data = copy.deepcopy(USER)
    new_data['id'] = USER_ID
    new_data.update(NEW_USER_DATA)
    user_to_view = UserResponse.parse_obj(new_data)
    assert response.status == HTTPStatus.OK
    assert response.body == json.loads(user_to_view.json())


async def test_user_delete_no_token(make_request):
    global ACCESS_TOKEN
    global USER_ID

    response = await make_request("delete")(
        f"user/{USER_ID}",
    )

    assert response.status == HTTPStatus.UNAUTHORIZED

    
async def test_user_delete_inv_token(make_request):
    global ACCESS_TOKEN
    global USER_ID

    response = await make_request("delete")(
        f"user/{USER_ID}",
        headers={"Authorization": "ACCESS_TOKEN"},
    )

    assert response.status == HTTPStatus.UNAUTHORIZED


async def test_user_delete(make_request):
    global ACCESS_TOKEN
    global USER_ID

    response = await make_request("delete")(
        f"user/{USER_ID}",
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.OK


async def test_user_data_after_del(make_request):
    global USER_ID
    global ACCESS_TOKEN

    response = await make_request("get")(
        f"user/{USER_ID}",
        headers={"Authorization": ACCESS_TOKEN},
    )

    assert response.status == HTTPStatus.NOT_FOUND


async def test_login_after_del(make_request):
    global NEW_USER_DATA
    global USER

    response = await make_request("post")(
        "login/",
        json={"login": NEW_USER_DATA["login"], "password": USER['password']},
    )

    assert response.status == HTTPStatus.NOT_FOUND
