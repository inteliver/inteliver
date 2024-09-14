from enum import Enum


class ImageSource(str, Enum):
    S3 = "s3"
    HTTP = "http"
