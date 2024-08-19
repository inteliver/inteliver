from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.database.dependencies import get_db
from inteliver.image.service import ImageService

router = APIRouter()


@router.get(
    "/{cloudname}/{commands:path}/{object_key}",
    tags=["Image Processor"],
)
async def process_image(
    cloudname: str,
    commands: str,
    object_key: str,
    db: AsyncSession = Depends(get_db),
    # current_user: TokenData = Depends(AuthService.get_current_user),
) -> StreamingResponse:
    """
    Process an image with specified commands.

    Args:
        cloudname (str): The user's cloud name.
        commands (str): The commands to apply to the image.
        object_key (str): The key of the resource.

    Returns:
        StreamingResponse: The modified image.
    """
    data, media_type = await ImageService.process_image(
        db, cloudname, commands, object_key
    )
    return StreamingResponse(data, media_type=media_type)
