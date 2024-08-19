from inteliver.config import settings

SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = settings.reset_password_token_expire_minutes
EMAIL_CONFIRMATION_TOKEN_EXPIRE_MINUTES = (
    settings.email_confirmation_token_expires_minutes
)
