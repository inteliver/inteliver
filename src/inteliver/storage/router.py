from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.auth.schemas import TokenData
from inteliver.auth.service import AuthService
from inteliver.database.dependencies import get_db
from inteliver.storage.schemas import ObjectOut, ObjectStats, ObjectUploaded
from inteliver.storage.service import StorageService

router = APIRouter()

# TODO: routes should be sync (def) or the minio client should be async
# currently an IO blocking operation (minio storage) is being executed in
# an async def which will block the main loop.
# functions should be sync (def) but currently they have a dependency on Postgre db
# which is async.


@router.post("/images", response_model=ObjectUploaded, tags=["Storage"])
async def upload_image(
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: TokenData = Depends(AuthService.get_current_user),
):
    """
    Upload a file to the specified storage (internal by default).

    Args:
        file (UploadFile): The file to upload.
        storage_type (str, optional): The storage type ("internal" or "external"). Defaults to "internal".
        db (AsyncSession): Database session dependency.
        current_user (TokenData): The current authenticated user.

    Returns:
        str: The URL of the uploaded file.
    """
    return await StorageService.upload_image(db, current_user.sub, file)


@router.get("/images", response_model=list[ObjectOut], tags=["Storage"])
async def list_objects(
    current_user: TokenData = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all user objects.

    Args:
        current_user (UserOut): The current authenticated user.
        db (AsyncSession): The database session.

    Returns:
        List[ResourceOut]: List of resources/images.
    """
    return await StorageService.list_images(db, current_user.sub)


@router.get("/images/{object_key}", tags=["Storage"])
async def retrieve_image(
    object_key: str,
    current_user: TokenData = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """
    Retrieve an object from the storage.

    Args:
        object_key (str): The key of the object to retrieve.
        current_user (TokenData): The current authenticated user.
        db (AsyncSession): The database session.

    Returns:
        Any: The retrieved object data.
    """
    data, headers = await StorageService.retrieve_image(
        db, current_user.sub, object_key
    )

    return StreamingResponse(data, headers=headers)


@router.delete("/images/{object_key}", tags=["Storage"])
async def delete_image(
    object_key: str,
    current_user: TokenData = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an object from the storage.

    Args:
        object_key (str): The key of the object to delete.
        current_user (TokenData): The current authenticated user.
        db (AsyncSession): The database session.

    Returns:
        dict: A message indicating the result of the deletion.
    """
    return await StorageService.delete_image(db, current_user.sub, object_key)


@router.get("/{object_key}/stats", response_model=ObjectStats, tags=["Storage"])
async def get_image_stats(
    object_key: str,
    current_user: TokenData = Depends(AuthService.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve the stats of a specific image for the authenticated user.

    Args:
        object_key (str): The name of the object (image).
        current_user (TokenData): The currently authenticated user.

    Returns:
        ObjectStats: The stats of the specified image.

    Raises:
        HTTPException: If the image stats cannot be retrieved.
    """
    return await StorageService.get_image_stats(db, current_user.sub, object_key)
