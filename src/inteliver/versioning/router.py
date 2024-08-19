from fastapi import APIRouter, status

from inteliver.version import __version__
from inteliver.versioning.schemas import Version

router = APIRouter()


@router.get("/version", response_model=Version, status_code=status.HTTP_200_OK)
async def get_app_version():
    """
    Retrieve the application version.

    Returns:
        Version: The pydantic model for app version.
    """
    return Version(version=__version__)
