import os
from enum import Enum
from functools import lru_cache
from pathlib import Path

import yaml
from dotenv import load_dotenv
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings
from tabulate import tabulate


class AppEnvEnum(str, Enum):
    """Enum representing different application environments."""

    DEVELOPMENT = "development"
    DEVELOPMENT_DOCKER = "development_docker"
    STAGING = "staging"
    PRODUCTION = "production"


class InteliverSettings(BaseSettings):
    """
    Configuration settings for the Inteliver application.
    """

    # App setttings
    app_name: str = Field("inteliver-api", alias="APP_NAME")

    app_api_host: str = Field("127.0.0.1", alias="APP_API_HOST")
    app_api_port: int = Field(8000, alias="APP_API_PORT")

    api_prefix: str = Field("/api/v1", alias="API_PREFIX")

    openapi_docs_url: str = Field("/docs", alias="FASTAPI_DOCS_URL")
    openapi_json_url: str = Field("/openapi.json", alias="FASTAPI_OPENAPI_URL")

    app_running_env: AppEnvEnum = Field(AppEnvEnum.DEVELOPMENT, alias="APP_RUNNING_ENV")

    # postgresql settings
    postgres_host: str = Field("localhost", alias="POSTGRES_HOST")
    postgres_user: str = Field("postgres", alias="POSTGRES_USER")
    postgres_password: str = Field("postgres", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field("inteliver", alias="POSTGRES_DB")

    # minio settings
    minio_host: str = Field("localhost:9000", alias="MINIO_HOST")
    minio_root_user: str = Field("minioadmin", alias="MINIO_ROOT_USER")
    minio_root_password: str = Field("minioadmin", alias="MINIO_ROOT_PASSWORD")
    minio_secure: bool = Field(False, alias="MINIO_SECURE")

    # auth settings
    jwt_secret_key: str = Field("your-secret-key", alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", alias="JWT_ALGORITHM")
    # 1 month
    access_token_expire_minutes: int = Field(
        30 * 24 * 60, alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    # 1 hour
    reset_password_token_expire_minutes: int = Field(
        60, alias="RESET_PASSWORD_TOKEN_EXPIRE_MINUTES"
    )
    # 1 hour
    email_confirmation_token_expires_minutes: int = Field(
        60, alias="EMAIL_VALIDATION_TOKEN_EXPIRE_MINUTES"
    )

    def log_settings(self):
        """Logs the settings in a tabular format to the console."""
        headers = ["Field", "Value", "Default Value", "Env Variable"]
        table = []

        for field_name, field_info in self.model_fields.items():
            value = getattr(self, field_name)
            default_value = (
                field_info.default if field_info.default is not None else "None"
            )

            env_variable = field_info.alias or "N/A"

            table.append([field_name, value, default_value, env_variable])

        logger.info("\n" + tabulate(table, headers, tablefmt="pretty"))


class DevelopmentSettings(InteliverSettings):
    pass


class DevelopmentDockerSettings(InteliverSettings):
    # example of a database url that has different env variable names and
    # default value in different running env settings
    # database_url: str = Field(..., env="STAGING_DB_URL")
    app_api_host: str = Field("0.0.0.0", alias="CONFIG_APP_API_HOST")
    app_api_port: int = Field(8000, alias="APP_API_PORT")
    # sample secret key
    # you can generate a 32 byte random key using the following command:
    # openssl rand -base64 32
    jwt_secret_key: str = Field(
        "G8GVVh68JeLRoD1doMoN6AL0zROZN1bN35b+zctMm18=", alias="JWT_SECRET_KEY"
    )
    postgres_host: str = Field("postgres", alias="POSTGRES_HOST")
    minio_host: str = Field("minio:9000", alias="MINIO_HOST")


class StagingSettings(InteliverSettings):
    # example of a database url that has different env variable names and
    # default value in different running env settings
    # database_url: str = Field(..., env="STAGING_DB_URL")
    app_api_host: str = Field("0.0.0.0", alias="CONFIG_APP_API_HOST")


class ProductionSettings(InteliverSettings):
    # example of a database url that has different env variable names and
    # default value in different running env settings
    # database_url: str = Field(..., env="PROD_DB_URL")
    app_api_host: str = Field("0.0.0.0", alias="CONFIG_APP_API_HOST")


@lru_cache
def get_settings() -> InteliverSettings:
    setting_mapping = {
        AppEnvEnum.DEVELOPMENT: DevelopmentSettings,
        AppEnvEnum.DEVELOPMENT_DOCKER: DevelopmentDockerSettings,
        AppEnvEnum.STAGING: StagingSettings,
        AppEnvEnum.PRODUCTION: ProductionSettings,
    }
    running_env = AppEnvEnum(os.getenv("APP_RUNNING_ENV", "development"))
    logger.debug(f"Running inteliver using {running_env} configs.")
    setting = setting_mapping.get(running_env, None)
    if not setting:
        raise ValueError("Invalid environment specified")
    return setting()


settings = get_settings()
settings.log_settings()
