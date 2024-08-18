from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ObjectUploaded(BaseModel):
    uid: UUID
    cloudname: str
    object_key: str
    detected_content_type: str


class ObjectOut(BaseModel):
    object_key: str
    etag: str
    bucket_name: str
    size: int
    last_modified: datetime


class ObjectStats(ObjectOut):
    content_type: str
