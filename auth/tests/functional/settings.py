from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    pg_name = "auth_database"
    pg_host: str = Field("auth_db", env="POSTGRES_DB")
    pg_user: str = Field("auth_app", env="POSTGRES_USER")
    pg_password: str = Field("qwe123", env="DB_PASSWORD")
    pg_port: int = 4321

    auth_host: str = Field("auth", env="API_HOST")
    auth_port: int = Field(5000, env="API_PORT")

    nginx_port: int = Field(80, env="API_PORT")
    nginx_host: str = Field("nginx", env="NGINX_PORT")

    service_wait_timeout: int = Field(30, env="SERVICE_WAIT_TIMEOUT")  # seconds
    service_wait_interval: int = Field(1, env="SERVICE_WAIT_INTERVAL")  # seconds

    redis_host: str = Field("redis", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_password = Field("123qwe", env="REDIS_PASSWORD")

    super_user_password: str = Field("password", env="SUPERUSER_PASSWORD")

