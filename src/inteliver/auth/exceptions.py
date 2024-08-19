from fastapi import HTTPException, status


class AuthenticationFailedException(HTTPException):
    def __init__(self, detail: str = "Incorrect username or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
        )


class ExpiredSignatureException(HTTPException):
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class PyJWTException(HTTPException):
    def __init__(self, detail: str = "Token is invalid"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class NotEnoughPermissionException(HTTPException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class DatabaseException(HTTPException):
    def __init__(self, detail: str = "Database error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail
        )


class TokenFieldsValidationException(HTTPException):
    def __init__(self, detail: str = "Token fields validation failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class EmailValidationTokenException(HTTPException):
    def __init__(self, detail: str = "Invalid email validation token"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
