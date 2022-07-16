from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    db_host: str = Field('localhost', env='DB_HOST')
    db_port: int = Field('27017', env='DB_PORT')
    rabbitmq_default_user: str = Field('', env='RABBITMQ_DEFAULT_USER')
    rabbitmq_default_pass: str = Field('', env='RABBITMQ_DEFAULT_PASS')
    grpc_channel_host: str = Field('localhost', env='GRPC_CHANNEL_HOST')
    grpc_channel_port: str = Field('50055', env='GRPC_CHANNEL_PORT')

settings = Settings()
