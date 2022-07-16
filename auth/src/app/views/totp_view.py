from http import HTTPStatus

from flask import Blueprint, request
from flask.views import MethodView

from app.services.auth_services.auth_services import AUTH_SERVICE
from app.services.auth_services.jwt_service import JWT_SERVICE
from app.services.totp_service import totp_service
from app.views.utils.decorator import catch_exceptions

totp_blueprint = Blueprint('totp', __name__, url_prefix='/auth/api/v1')


class SyncTOTPView(MethodView):

    @catch_exceptions
    @AUTH_SERVICE.token_required()
    def get(self):
        access_token = request.headers["Authorization"]
        user_data = dict(JWT_SERVICE.get_access_payload(access_token))

        provisioning_uri = totp_service.generate_provisioning_uri(user_data)

        return {"provisioning_url": provisioning_uri, "user_id": user_data["user_id"]}, HTTPStatus.OK


totp_blueprint.add_url_rule(
    "/enable_totp/",
    endpoint="enable_totp",
    methods=["GET"],
    view_func=SyncTOTPView.as_view("totp")
)