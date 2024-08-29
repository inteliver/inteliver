import os
import sys
from pathlib import Path

import yaml
from loguru import logger

from inteliver.config.schema import AppEnvEnum


def get_yaml_config_path() -> str:
    # Get the directory where this file is located
    base_path = Path(__file__).parent.resolve()
    home_path = Path.home()
    yaml_config_path_mapping = {
        AppEnvEnum.DEVELOPMENT: base_path / "yamls/config.dev.standalone.yml",
        AppEnvEnum.DEVELOPMENT_DOCKER: base_path / "yamls/config.dev.docker.yml",
        AppEnvEnum.STAGING: home_path / ".config/inteliver/config.yml",
        AppEnvEnum.PRODUCTION: home_path / ".config/inteliver/config.yml",
    }
    running_env = get_running_env()
    yaml_config_path = yaml_config_path_mapping.get(running_env)

    # setting up a simple pre setup logger for this section only
    pre_setup_format: str = "<level>{message}</level>"
    logger.remove()
    logger.add(sink=sys.stdout, format=pre_setup_format)
    logger.warning(f"Running inteliver in {running_env.value} mode.")
    logger.info(f"Default YAML config file location at: {yaml_config_path}")
    return yaml_config_path


def get_running_env() -> AppEnvEnum:
    """Getting the running environment"""
    env_value = os.getenv("APP_RUNNING_ENV", "development")
    try:
        return AppEnvEnum(env_value)
    except ValueError:
        logger.warning(
            f"Invalid APP_RUNNING_ENV '{env_value}', defaulting to 'development'."
        )
        return AppEnvEnum.DEVELOPMENT


def save_config_to_yaml(config_data: dict):
    """
    Save the provided configuration data to a YAML file in the user's home directory.
    Create config file if it does not exist, update existing fields and add new ones.

    Args:
        config_data (dict): A dictionary containing the configuration data to be saved.
    """
    # Define the path to the config file
    config_dir = Path.home() / ".config" / "inteliver"
    config_file = config_dir / "config.yml"

    # Ensure the config directory exists
    config_dir.mkdir(parents=True, exist_ok=True)

    # Read existing config or create an empty dict if file doesn't exist
    if config_file.exists():
        with open(config_file, "r") as file:
            existing_config = yaml.safe_load(file) or {}
    else:
        existing_config = {}
        logger.info(f"Created new config file: {config_file}")

    # Update existing config with new data
    for key, value in config_data.items():
        if key in existing_config:
            if existing_config[key] != value:
                logger.info(
                    f"Updated value for '{key}': {existing_config[key]} -> {value}"
                )
                existing_config[key] = value
        else:
            logger.info(f"Added new field '{key}' with value: {value}")
            existing_config[key] = value

    # Write the updated configuration data to the YAML file
    with open(config_file, "w") as file:
        yaml.dump(existing_config, file, default_flow_style=False)

    logger.info(f"Configuration saved to {config_file}")
