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
    def __init__(self, detail: str = "Unprocessable Command Arguments"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )
