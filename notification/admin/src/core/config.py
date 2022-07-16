import os

from pydantic import BaseConfig


class Config(BaseConfig):
    notification_api_url: str = "http://notification_api:8000/notifications/api/v1/thematic/"
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 27017))


config = Config()

TEMPLATE_AVAILABLE_VARIABLES = {
    "username": "username",
    "email": "test@mail.ru",
    "first_name": "FirstName",
    "last_name": "LastName"
}
