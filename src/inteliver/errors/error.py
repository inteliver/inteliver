from pydantic import BaseModel
from fastapi import HTTPException, status


class BaseErrorResponse(BaseModel):
    status_code: int
    type: str
    msg: str
    loc: list[str]

    def as_exception(self) -> HTTPException:
        return HTTPException(status_code=self.status_code, detail=self.model_dump())


class BadRequestErrorResponse(BaseErrorResponse):
    status_code: int = status.HTTP_400_BAD_REQUEST
    type: str = "service.bad_request"
    msg: str = "The server cannot process the request"
    loc: list[str] = ["general", "bad_request"]


class NotFoundErrorResponse(BaseErrorResponse):
    status_code: int = status.HTTP_404_NOT_FOUND
    type: str = "service.not_found_error"
    msg: str = "The requested resource not found"
    loc: list[str] = ["general", "not_found_error"]


class InternalServerErrorResponse(BaseErrorResponse):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    type: str = "service.internal_server_error"
    msg: str = "The server encountered an unexpected condition"
    loc: list[str] = ["general", "internal_server_error"]
