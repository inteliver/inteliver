from fastapi import HTTPException, status


class CloudnameNotExistsException(HTTPException):
    def __init__(self, detail: str = "The requested cloudname does not exists"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class ImageDecodeException(HTTPException):
    def __init__(self, detail: str = "Can not decode the image data"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class ImageProcessorException(HTTPException):
    def __init__(self, detail: str = "Can not apply image modification"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )


class UnprocessableCommandArgumentsException(HTTPException):
    def __init__(self, detail: str = "Unprocessable command arguments"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InsufficientCommandArgumentsException(HTTPException):
    def __init__(self, detail: str = "Insufficient number of command arguments"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class InvalidCommandOperationException(HTTPException):
    def __init__(self, detail: str = "Invalid command operation"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class FetchImageURLException(HTTPException):
    def __init__(
        self, detail: str = "Unable to retrieve image from the requested url."
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
