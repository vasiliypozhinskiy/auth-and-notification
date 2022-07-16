import secrets
import string
from abc import ABC, abstractmethod
from http import HTTPStatus

import requests

from app.services.auth_services.jwt_service import JWT_SERVICE
from app.services.auth_services.storages import REF_TOK_STORAGE
from app.services.storage.storage import user_table, user_login_history_table
from app.utils.exceptions import NotFoundError, AccessDenied
from app.core.config import VKOathConfig, YandexOathConfig, BaseOauthConfig, MailOauthConfig, TIME_OUT_REQUEST
from app.models.service_models import OauthAccess, LoginTokens, OauthUserData


class BaseOauthService(ABC):
    type_: str
    config: BaseOauthConfig

    def login(self, code: str, agent: str):
        access = self._get_oauth_tokens(code=code)
        user_data = self._get_user_data(access=access)
        return self._login(oauth_user_id=user_data.user_id, agent=agent)

    def _login(self, oauth_user_id: str, agent: str):
        try:
            user = user_table.read({"oauth_id": oauth_user_id, "oauth_type": self.type_})
            user_id = user["id"]
        except NotFoundError:
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(20))

            user_data = {
                "login": self.type_ + oauth_user_id,
                "password": password,
                "oauth_id": oauth_user_id,
                "oauth_type": self.type_
            }
            user_id = user_table.create(user_data)

        access_token, refresh_token = JWT_SERVICE.generate_tokens(
            user_id=user_id,
        )

        REF_TOK_STORAGE.add_token(
            token=refresh_token,
            agent=agent,
            user_id=user_id
        )

        user_login_history_table.create(
            data={
                "user_id": user_id,
                "user_agent": agent,
                "refresh_token": refresh_token,
            }
        )

        return LoginTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @abstractmethod
    def _get_oauth_tokens(self, code) -> OauthAccess:
        pass

    @abstractmethod
    def _get_user_data(self, access: OauthAccess) -> OauthUserData:
        pass


class YandexOauthService(BaseOauthService):

    type_ = "Yandex"
    config = YandexOathConfig()

    def _get_oauth_tokens(self, code):
        get_token_params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": self.config.redirect_url,
            "code": code,
            "grant_type": "authorization_code",
        }
        get_token_response = requests.post(
            self.config.get_token_url,
            data=get_token_params,
            headers={"Content-type": "application/x-www-form-urlencoded"},
            timeout=TIME_OUT_REQUEST
        )
        resp_json = get_token_response.json()

        return OauthAccess(**resp_json)

    def _get_user_data(self, access: OauthAccess):
        resp = requests.get(
            "https://login.yandex.ru/info",
            params={"oauth_token": access.access_token},
            timeout=TIME_OUT_REQUEST
        )
        if resp.status_code == HTTPStatus.OK:
            return OauthUserData(user_id=resp.json()['id'])
        else:
            raise AccessDenied


class VKOauthService(BaseOauthService):

    type_ = 'VK'
    config = VKOathConfig()

    def _get_oauth_tokens(self, code):
        get_token_params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": self.config.redirect_url,
            "code": code,
        }
        get_token_response = requests.get(
            self.config.get_token_url,
            params=get_token_params,
            timeout=TIME_OUT_REQUEST
        )
        resp_json = get_token_response.json()

        return OauthAccess(**resp_json)

    def _get_user_data(self, access: OauthAccess):
        return OauthUserData(user_id=access.user_id)

class MailOauthService(BaseOauthService):

    type_ = 'Mail'
    config = MailOauthConfig()

    def _get_oauth_tokens(self, code):
        get_token_params = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "redirect_uri": self.config.redirect_url,
            "code": code,
        }
        get_token_response = requests.get(
            self.config.get_token_url,
            params=get_token_params,
            timeout=TIME_OUT_REQUEST
        )
        resp_json = get_token_response.json()

        return OauthAccess(**resp_json)

    def _get_user_data(self, access: OauthAccess):
        return OauthUserData(user_id=access.user_id)



class OauthService:

    @staticmethod
    def login(oauth_user_id: str, oauth_type: str, agent: str):
        try:
            user = user_table.read({"oauth_id": oauth_user_id, "oauth_type": oauth_type})
            user_id = user["id"]
        except NotFoundError:
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for i in range(20))

            user_data = {
                "login": oauth_type + oauth_user_id,
                "password": password,
                "oauth_id": oauth_user_id,
                "oauth_type": oauth_type
            }
            user_id = user_table.create(user_data)

        access_token, refresh_token = JWT_SERVICE.generate_tokens(
            user_id=user_id,
        )

        REF_TOK_STORAGE.add_token(
            token=refresh_token,
            agent=agent,
            user_id=user_id
        )

        user_login_history_table.create(
            data={
                "user_id": user_id,
                "user_agent": agent,
                "refresh_token": refresh_token,
            }
        )

        return access_token, refresh_token


oauth_service = OauthService()

vk_oauth_service = VKOauthService()
yandex_oauth_service = YandexOauthService()
mail_oauth_service = MailOauthService()
