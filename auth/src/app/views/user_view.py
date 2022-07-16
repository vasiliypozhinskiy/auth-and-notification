from http import HTTPStatus

from flask.views import MethodView
from flasgger.utils import swag_from
from flask import Blueprint, jsonify, request

from app.core.swagger_config import SWAGGER_DOCS_PATH
from app.services.user_service import user_service
from app.services.auth_services.auth_services import AUTH_SERVICE
from app.services.rate_limit import limit_rate
from app.utils.exceptions import NotFoundError
from app.views.models.user import UserResponse, UserHistoryResponse, HistoryEntry
from app.views.utils.decorator import catch_exceptions

user_blueprint = Blueprint("user", __name__, url_prefix="/auth/api/v1")


class UserView(MethodView):
    @swag_from(
        f"{SWAGGER_DOCS_PATH}/user/create_user.yaml",
        endpoint="user.create_user"
    )
    @catch_exceptions
    def post(self):
        return self._create_user()

    @swag_from(
        f"{SWAGGER_DOCS_PATH}/user/get_user.yaml",
        endpoint="user.user_with_id",
        methods=["GET"],
    )
    @catch_exceptions
    @limit_rate
    def get(self, user_id):
        return self._get_user(user_id)

    @swag_from(
        f"{SWAGGER_DOCS_PATH}/user/update_user.yaml",
        endpoint="user.user_with_id",
        methods=["PATCH"],
    )
    @catch_exceptions
    @limit_rate
    def patch(self, user_id):
        return self._update_user(user_id=user_id)

    @swag_from(
        f"{SWAGGER_DOCS_PATH}/user/delete_user.yaml",
        endpoint="user.user_with_id",
        methods=["DELETE"],
    )
    @catch_exceptions
    @limit_rate
    def delete(self, user_id):
        return self._delete_user(user_id=user_id)

    @staticmethod
    def _create_user():
        """Метод для регистрации пользователя"""
        user_data = request.json

        new_user_id = user_service.create_user(user_data)

        return {"user_id": new_user_id}, HTTPStatus.CREATED

    @staticmethod
    def _get_user(user_id: str):
        """Метод для получения данных пользователя по id"""
        user = user_service.get_user(user_id)
        if not user:
            raise NotFoundError

        if user.birthdate:
            user.birthdate = user.birthdate.strftime('%Y-%m-%d')
        response = UserResponse.parse_obj(user)

        return jsonify(dict(response))

    @staticmethod
    @AUTH_SERVICE.token_required(check_is_me=True)
    def _update_user(user_id: str):
        """Метод для обновления данных пользователя (кроме пароля) по id"""
        user_data = request.json

        user_service.update_user(user_id, user_data)

        return "User updated", HTTPStatus.OK

    @staticmethod
    @AUTH_SERVICE.token_required(check_is_me=True)
    def _delete_user(user_id: str):
        """Метод для удаления пользователя по id"""
        user_service.delete_user(user_id)
        AUTH_SERVICE.logout_all(request.headers["authorization"])

        return "User deleted", HTTPStatus.OK


class UserChangePassword(MethodView):
    @swag_from(
        f"{SWAGGER_DOCS_PATH}/user/change_password.yaml",
        endpoint="user.change_password"
    )
    @catch_exceptions
    @limit_rate
    def put(self, user_id):
        return self._change_password(user_id=user_id)

    @staticmethod
    @AUTH_SERVICE.token_required(check_is_me=True)
    @limit_rate
    def _change_password(user_id):
        passwords = request.json
        if (not passwords.get("old_password")) or (not passwords.get("new_password")):
            return "Wrong request params", HTTPStatus.BAD_REQUEST

        user_service.change_password(user_id, passwords)
        AUTH_SERVICE.logout_all(request.headers["authorization"])

        return "Password changed", HTTPStatus.OK


class UserHistory(MethodView):
    @swag_from(
        f"{SWAGGER_DOCS_PATH}/user/get_history.yaml",
        endpoint="user.get_history"
    )
    @catch_exceptions
    @limit_rate
    def get(self, user_id):
        return jsonify(self._get_history(user_id=user_id))

    @staticmethod
    @AUTH_SERVICE.token_required(check_is_me=True)
    def _get_history(user_id):
        history_entries = [HistoryEntry(**dict(entry)) for entry in user_service.get_history(user_id)]
        response = UserHistoryResponse(entries=history_entries)
        return response.to_dict()


user_blueprint.add_url_rule(
    "/user/<string:user_id>",
    endpoint="user_with_id",
    methods=["GET", "PATCH", "DELETE"],
    view_func=UserView.as_view("user")
)

user_blueprint.add_url_rule(
    "/user/",
    endpoint="create_user",
    methods=["POST"],
    view_func=UserView.as_view("user")
)

user_blueprint.add_url_rule(
    "/user/<string:user_id>/change_password",
    endpoint="change_password",
    methods=["PUT"],
    view_func=UserChangePassword.as_view("user")
)

user_blueprint.add_url_rule(
    "/user/<string:user_id>/get_history",
    endpoint="get_history",
    methods=["GET"],
    view_func=UserHistory.as_view("user")
)
