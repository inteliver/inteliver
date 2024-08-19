from fastapi import HTTPException, status


class CludnameNotSetException(HTTPException):
    def __init__(self, detail: str = "Cloudname not set"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class UnsupportedImageFormatException(HTTPException):
    def __init__(self, detail: str = "Unsupported image format"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InvalidImageFileException(HTTPException):
    def __init__(self, detail: str = "Invalid image file"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class S3ErrorException(HTTPException):
    def __init__(self, detail: str = "S3 object storage error occured"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class S3ErrorObjectNotFoundException(HTTPException):
    def __init__(self, detail: str = "Object not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
