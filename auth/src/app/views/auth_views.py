import uuid
from typing import Optional
from http import HTTPStatus

from flask.views import MethodView
from flask import Blueprint, jsonify, request
from flasgger.utils import swag_from

from app.core.swagger_config import SWAGGER_DOCS_PATH
from app.views.models.auth import AuthRefreshReqView, AuthReqView, AuthorizeResponse
from app.services.auth_services.auth_services import AUTH_SERVICE
from app.services.rate_limit import limit_rate
from app.views.utils.decorator import catch_exceptions

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth/api/v1')


class Login(MethodView):
    
    @swag_from(f'{SWAGGER_DOCS_PATH}/auth/login.yaml', endpoint='auth.login', methods=['POST'])
    @catch_exceptions
    def post(self):
        request_data = request.json
        agent = request.headers.get('User-Agent')
        login_data = AuthReqView.parse_obj(request_data)
        login_resp = AUTH_SERVICE.login(login_data, agent=agent)
        return login_resp.dict()


class LogOut(MethodView):
    
    @swag_from(f'{SWAGGER_DOCS_PATH}/auth/logout.yaml', endpoint='auth.logout', methods=['POST'])
    @catch_exceptions
    @limit_rate
    def post(self):
        access_token = request.headers["Authorization"]
        agent = request.headers.get('User-Agent', "")
        AUTH_SERVICE.logout(access_token=access_token, agent=agent)
        return 'Success logout', HTTPStatus.OK


class Authorize(MethodView):
    
    @swag_from(f'{SWAGGER_DOCS_PATH}/auth/authorize.yaml', endpoint='auth.authorize', methods=['GET'])
    @catch_exceptions
    def get(self):

        access_token = request.headers["Authorization"]
        roles, is_su = AUTH_SERVICE.authorize(access_token=access_token)
        out = AuthorizeResponse(roles=roles, is_superuser=is_su)
        return jsonify(out.dict()), HTTPStatus.OK



class Refresh(MethodView):
    
    @swag_from(f'{SWAGGER_DOCS_PATH}/auth/refresh.yaml', endpoint='auth.refresh', methods=['POST'])
    @catch_exceptions
    @limit_rate
    def post(self):
        req = AuthRefreshReqView(**request.json)
        agent = request.headers.get('User-Agent')
        response = AUTH_SERVICE.refresh_jwt(refresh_jwt=req.refresh_token, agent=agent)
        return response.dict()


class BaseLogoutAll(MethodView):
    
    @catch_exceptions
    def post(self, user_id: Optional[str] = None):
        access_token = request.headers["Authorization"]
        if user_id is not None:
            user_id = uuid.UUID(user_id)
        AUTH_SERVICE.logout_all(access_token=access_token, user_id=user_id)
        return 'Successfull logout from all devices', HTTPStatus.OK


class LogOutAllById(BaseLogoutAll):

    @swag_from(f'{SWAGGER_DOCS_PATH}/auth/logout_all_id.yaml', endpoint='auth.logout-all-id', methods=['POST'])
    @catch_exceptions
    @limit_rate
    @AUTH_SERVICE.token_required(check_is_superuser=True)
    def post(self, user_id: Optional[str] = None):
        return super().post(user_id=user_id)


class LogOutAllByAccess(BaseLogoutAll):
    
    @swag_from(f'{SWAGGER_DOCS_PATH}/auth/logout_all.yaml', endpoint='auth.logout-all-access', methods=['POST'])
    @catch_exceptions
    @limit_rate
    @AUTH_SERVICE.token_required()
    def post(self, user_id: Optional[str] = None):
        return super().post(user_id=user_id)


auth_blueprint.add_url_rule('/login/', endpoint='login', view_func=Login.as_view('auth'), methods=["POST"])
auth_blueprint.add_url_rule('/logout', endpoint='logout', view_func=LogOut.as_view('auth'), methods=["POST"])
auth_blueprint.add_url_rule('/authorize/', endpoint='authorize', view_func=Authorize.as_view('auth'), methods=["GET"])
auth_blueprint.add_url_rule('/refresh/', endpoint='refresh', view_func=Refresh.as_view('auth'), methods=["POST"])
auth_blueprint.add_url_rule('/logout_all/<string:user_id>', endpoint='logout-all-id', view_func=LogOutAllById.as_view('auth'), methods=["POST"])
auth_blueprint.add_url_rule('/logout_all/', endpoint='logout-all-access', view_func=LogOutAllByAccess.as_view('auth'), methods=["POST"])