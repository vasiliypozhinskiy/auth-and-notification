from pydantic import BaseSettings


class MongoSettings(BaseSettings):
    host: str = "notification_db"
    port: int = 27017

    class Config:
        env_prefix = "mongo_"


class RabbitSettings(BaseSettings):
    host: str = "rabbitmq"
    port: int = 5672
    default_user: str = "notification_admin"
    default_pass: str = "as1234"

    class Config:
        env_prefix = "rabbitmq_"


class Config(BaseSettings):
    auth_url: str = "http://auth-rest:5000/auth/api/v1/users/"
    mongo: MongoSettings = MongoSettings()
    rabbit: RabbitSettings = RabbitSettings()
