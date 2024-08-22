import os
from pathlib import Path

from loguru import logger

from inteliver.config.schema import AppEnvEnum


def get_yaml_config_path() -> str:
    # Get the directory where this file is located
    base_path = Path(__file__).parent.resolve()
    home_path = Path.home()
    yaml_config_path_mapping = {
        AppEnvEnum.DEVELOPMENT: base_path / "yamls/config.dev.standalone.yml",
        AppEnvEnum.DEVELOPMENT_DOCKER: base_path / "yamls/config.dev.docker.yml",
        AppEnvEnum.STAGING: home_path / ".config/inteliver/config.stage.yml",
        AppEnvEnum.PRODUCTION: home_path / ".config/inteliver/config.prod.yml",
    }
    try:
        running_env = AppEnvEnum(os.getenv("APP_RUNNING_ENV", "development"))
    except ValueError as e:
        logger.error(
            f"{str(e)}. APP_RUNNING_ENV must be set to one of {[e.value for e in AppEnvEnum]}"
        )
    yaml_config_path = yaml_config_path_mapping.get(running_env)
    logger.debug(
        f"Running inteliver using {running_env} configs. YAML config file location at {yaml_config_path}"
    )
    return yaml_config_path
