from http import HTTPStatus

from flasgger.utils import swag_from
from flask import Blueprint
from flask.views import MethodView

from app.core.swagger_config import SWAGGER_DOCS_PATH
from app.services.auth_services.auth_services import AUTH_SERVICE
from app.services.rate_limit import limit_rate
from app.services.role_service import role_service
from app.views.utils.decorator import catch_exceptions

role_blueprint = Blueprint("role", __name__, url_prefix="/auth/api/v1")


class RoleView(MethodView):
    @swag_from(
        f"{SWAGGER_DOCS_PATH}/role/create_role.yaml",
        endpoint="role.create_role",
        methods=["POST"]
    )
    @catch_exceptions
    @limit_rate
    def post(self, new_role):
        return self._create_role(new_role)

    @swag_from(
        f"{SWAGGER_DOCS_PATH}/role/get_list_role.yaml",
        endpoint="role.list_role",
        methods=["GET"],
    )
    @catch_exceptions
    @limit_rate
    def get(self):
        return self._get_list_role()

    @swag_from(
        f"{SWAGGER_DOCS_PATH}/role/update_role.yaml",
        endpoint="role.update_role",
        methods=["PATCH"],
    )
    @catch_exceptions
    @limit_rate
    def patch(self, role_title, new_role):
        return self._update_role(role_title, new_role)

    @swag_from(
        f"{SWAGGER_DOCS_PATH}/role/delete_role.yaml",
        endpoint="role.delete_role",
        methods=["DELETE"],
    )
    @catch_exceptions
    @limit_rate
    def delete(self, role_title):
        return self._delete_role(role_title)

    @staticmethod
    @AUTH_SERVICE.token_required(check_is_superuser=True)
    def _create_role(new_role):
        """
        Метод для создания роли
        """
        role_service.create_role(new_role)

        return "Created", HTTPStatus.CREATED

    @staticmethod
    def _get_list_role():
        roles = role_service.get_list_role()
        return roles

    @staticmethod
    @AUTH_SERVICE.token_required(check_is_superuser=True)
    def _update_role(role_title: str, new_role: str):

        role_service.update_role(role_title, new_role)
        return "Role updated", HTTPStatus.OK

    @staticmethod
    @AUTH_SERVICE.token_required(check_is_superuser=True)
    def _delete_role(role_title):
        """Метод для удаления роли"""
        role_service.delete_role(role_title)
        return "Role deleted", HTTPStatus.OK


role_blueprint.add_url_rule(
    "/role/role_list/",
    endpoint="list_role",
    methods=["GET"],
    view_func=RoleView.as_view("role")
)

role_blueprint.add_url_rule(
    "/role/<string:new_role>",
    endpoint="create_role",
    methods=["POST"],
    view_func=RoleView.as_view("role")
)

role_blueprint.add_url_rule(
    "/role/<string:role_title>",
    endpoint="delete_role",
    methods=["DELETE"],
    view_func=RoleView.as_view("role")
)

role_blueprint.add_url_rule(
    "/role/<string:role_title>/<new_role>",
    endpoint="update_role",
    methods=["PATCH"],
    view_func=RoleView.as_view("role")
)
