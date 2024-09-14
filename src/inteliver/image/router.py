from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.database.dependencies import get_db
from inteliver.image.schemas import ImageSource
from inteliver.image.service import ImageService

router = APIRouter()


@router.get(
    "/{cloudname}/{commands:path}/s3/{object_key}",
    tags=["Image Processor"],
)
async def process_image_s3(
    cloudname: str,
    commands: str,
    object_key: str,
    db: AsyncSession = Depends(get_db),
    # current_user: TokenData = Depends(AuthService.get_current_user),
) -> StreamingResponse:
    """
    Process an image with specified commands.
    fetch the image from internal s3 storage.

    Args:
        cloudname (str): The user's cloud name.
        commands (str): The commands to apply to the image.
        object_key (str): The key of the resource.

    Returns:
        StreamingResponse: The modified image.
    """
    data, media_type = await ImageService.process_image(
        db=db,
        cloudname=cloudname,
        commands=commands,
        uri=object_key,
        image_source=ImageSource.S3,
    )
    return StreamingResponse(data, media_type=media_type)


@router.get(
    "/{cloudname}/{commands:path}/http/{url:path}",
    tags=["Image Processor"],
)
async def process_image_http(
    cloudname: str,
    commands: str,
    url: str,
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Process an image with specified commands.
    fetch the image from a url.

    Args:
        cloudname (str): The user's cloud name.
        commands (str): The commands to apply to the image.
        url (str): The url of the image.

    Returns:
        StreamingResponse: The modified image.
    """
    data, media_type = await ImageService.process_image(
        db=db,
        cloudname=cloudname,
        commands=commands,
        uri=url,
        image_source=ImageSource.HTTP,
    )
    return StreamingResponse(data, media_type=media_type)
