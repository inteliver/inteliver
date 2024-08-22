from enum import Enum


class AppEnvEnum(str, Enum):
    """Enum representing different application environments."""

    DEVELOPMENT = "development"
    DEVELOPMENT_DOCKER = "development_docker"
    STAGING = "staging"
    PRODUCTION = "production"
