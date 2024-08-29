import logging
import os
import sys

from loguru import logger

from inteliver.config.schema import AppEnvEnum
from inteliver.config.utils import get_running_env


def configure_loguru(log_level: int = logging.DEBUG) -> logging.Logger:
    # Remove default logger to add a custom one with
    logger.remove()

    simple_format: str = "<level>{level: <8}</level> |   <level>{message}</level>"

    # Add a logger that outputs to the console
    logger.add(sink=sys.stdout, level=log_level, format=simple_format)

    # Add a logger that outputs to a file with rotation and retention
    logger.add(
        "logs/inteliver.log",
        level=log_level,
        rotation="10 MB",
        retention="10 days",
    )

    # Optional: Add more handlers as needed, for example, an error log file
    logger.add(
        "logs/inteliver.error.log",
        level=logging.ERROR,
        rotation="1 MB",
        retention="10 days",
    )
    return logger


def get_logging_level():
    log_level_mapping = {
        AppEnvEnum.DEVELOPMENT: logging.DEBUG,
        AppEnvEnum.DEVELOPMENT_DOCKER: logging.DEBUG,
        AppEnvEnum.STAGING: logging.WARNING,
        AppEnvEnum.PRODUCTION: logging.WARNING,
    }
    running_env = get_running_env()

    return log_level_mapping.get(running_env)


def setup_logging() -> logging.Logger:
    log_level = get_logging_level()
    return configure_loguru(log_level)
