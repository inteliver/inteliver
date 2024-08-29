import logging
import os
from functools import lru_cache
from pathlib import Path

from loguru import logger
from pydantic import Field, ValidationError
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)
from tabulate import tabulate

from inteliver.config.schema import AppEnvEnum
from inteliver.config.utils import get_yaml_config_path
from inteliver.utils.logger import setup_logging


class InteliverSettings(BaseSettings):
    """
    Configuration settings for the Inteliver application.
    """

    # App setttings
    app_name: str = Field(default="inteliver")

    app_api_host: str = Field(default="127.0.0.1")
    app_api_port: int = Field(default=8000)

    api_prefix: str = Field(default="/api/v1")

    openapi_docs_url: str = Field(default="/docs")
    openapi_json_url: str = Field(default="/openapi.json")

    app_running_env: AppEnvEnum = Field(
        default=AppEnvEnum.DEVELOPMENT, alias="APP_RUNNING_ENV"
    )

    # postgresql settings
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_db: str = Field(default="inteliver")

    # minio settings
    minio_host: str = Field(default="localhost:9000")
    minio_root_user: str = Field(default="minioadmin")
    minio_root_password: str = Field(default="minioadmin")
    minio_secure: bool = Field(default=False)

    # auth settings
    jwt_secret_key: str = Field(default="your-secret-key")
    jwt_algorithm: str = Field(default="HS256")
    # default jwt token expire time is 1 month
    access_token_expire_minutes: int = Field(default=(30 * 24 * 60))
    # default jwt token expire time is 1 hour
    reset_password_token_expire_minutes: int = Field(60)
    # default jwt token expire time is 1 hour
    email_confirmation_token_expires_minutes: int = Field(60)

    model_config = SettingsConfigDict(
        env_prefix="inteliver_",
        yaml_file=get_yaml_config_path(),
        extra="allow",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        try:
            yml_settings = YamlConfigSettingsSource(
                settings_cls,
            )
            return (
                init_settings,
                env_settings,
                yml_settings,
                file_secret_settings,
            )
        except ValidationError as e:
            logger.error(f"Yaml config file validation failed: {str(e)}")
        except TypeError:
            logger.info(f"Skipping Yaml config file. The file is empty.")
        except Exception as e:
            logger.error(f"Unable to apply yaml configuration file: {str(e)}")

        return (
            init_settings,
            env_settings,
            file_secret_settings,
        )

    def log_settings(self):
        """Logs the settings in a tabular format to the console."""
        headers = ["Field", "Value", "Default Value"]
        table = []

        for field_name, field_info in self.model_fields.items():
            value = getattr(self, field_name)
            default_value = (
                field_info.default if field_info.default is not None else "None"
            )

            table.append([field_name, value, default_value])

        logger.info("\n" + tabulate(table, headers, tablefmt="pretty"))


@lru_cache
def get_settings() -> InteliverSettings:
    setup_logging()
    try:
        settings = InteliverSettings()
        return settings
    except ValidationError as e:
        logger.critical(f"Unable to validate pydantic settings: {str(e)}")
