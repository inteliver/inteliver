import itertools
import uuid
from datetime import datetime, timezone
from io import BytesIO
from uuid import UUID

from fastapi import UploadFile
from loguru import logger
from minio import Minio, S3Error
from minio.datatypes import Object as MinioObject
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.config import settings
from inteliver.storage.constants import SUPPORTED_IMAGE_FORMATS
from inteliver.storage.exceptions import (
    InvalidImageFileException,
    S3ErrorException,
    S3ErrorObjectNotFoundException,
    UnsupportedImageFormatException,
)
from inteliver.storage.schemas import ObjectOut, ObjectStats, ObjectUploaded
from inteliver.users.service import UserService


class MinIOService:
    client = Minio(
        settings.minio_host,
        access_key=settings.minio_root_user,
        secret_key=settings.minio_root_password,
        secure=settings.minio_secure,
    )

    @classmethod
    def bucket_exists(cls, bucket_name: str) -> bool:
        return cls.client.bucket_exists(bucket_name)

    @classmethod
    def make_bucket(cls, bucket_name: str):
        cls.client.make_bucket(bucket_name)

    @classmethod
    def put_object(
        cls, bucket_name: str, object_name: str, data, length: int, content_type: str
    ):
        cls.client.put_object(
            bucket_name, object_name, data, length, content_type=content_type
        )

    @classmethod
    def get_object(cls, bucket_name: str, object_name: str) -> tuple[BytesIO, dict]:
        """
        Retrieve an object from MinIO storage.

        Args:
            bucket_name (str): The name of the bucket.
            object_name (str): The key of the object to retrieve.

        Returns:
            BaseHTTPResponse: The retrieved object data.
        """
        try:
            response = cls.client.get_object(bucket_name, object_name)
            # read the data
            data = response.data
            headers = response.headers
            # close and release connection
            response.close()
            response.release_conn()
            return BytesIO(data), dict(headers)

        except S3Error:
            raise

    @classmethod
    def delete_object(cls, bucket_name: str, object_name: str):
        """
        Delete an object from MinIO storage.

        Args:
            bucket_name (str): The name of the bucket.
            object_name (str): The key of the object to delete.

        Raises:
            S3Error: If an error occurs during deletion.
        """
        try:
            # Check if the object exists
            cls.client.stat_object(bucket_name, object_name)
        except S3Error as e:
            logger.error(f"MinIO S3Error (stat_object): {str(e)}")
            raise S3ErrorObjectNotFoundException(
                detail=f"Object not found: {object_name}"
            )

        # Proceed with object deletion
        cls.client.remove_object(bucket_name, object_name)

    @classmethod
    def list_objects(cls, bucket_name: str, skip: int, limit: int) -> list[MinioObject]:
        """
        List objects in a bucket.

        Args:
            bucket_name (str): The name of the bucket.
            skip (int): The number of objects to skip.
            limit (int): The maximum number of objects to return.

        Returns:
            List[Object]: List of objects.
        """
        try:
            # List objects in the bucket
            objects_iter = cls.client.list_objects(bucket_name)
            return list(itertools.islice(objects_iter, skip, skip + limit))
        except S3Error as e:
            raise S3ErrorException(detail=f"Error listing objects: {e}")

    @classmethod
    def get_object_stats(cls, bucket_name: str, object_name: str):
        """
        Get the stats of an object from MinIO.

        Args:
            bucket_name (str): The name of the bucket.
            object_name (str): The name of the object.

        Returns:
            Object: The stats of the object.

        Raises:
            S3Error: If the object stats cannot be retrieved.
        """
        try:
            stats = cls.client.stat_object(bucket_name, object_name)
            return stats
        except S3Error as e:
            raise S3ErrorException(detail=f"MinIO S3Error (stat_object): {e}")


class StorageService:

    @staticmethod
    async def upload_image(
        db: AsyncSession,
        uid: UUID,
        file: UploadFile,
    ) -> ObjectUploaded:
        """
        Upload a file to the specified storage (internal or external).

        Args:
            db (AsyncSession): The database session.
            uid (UUID): The current authenticated user id.
            file (UploadFile): The file to upload.

        Returns:
            str: The URL of the uploaded file.
        """

        # Step 1: Get user's cloudname
        cloudname = await UserService.get_cloudname(db, uid)

        # Step 2: Validate image format
        mime_type = StorageService._validate_image_format(file)

        # Step 3: Check if bucket exists, if not create it
        if not MinIOService.bucket_exists(cloudname):
            MinIOService.make_bucket(cloudname)

        # Step 4: Create a unique object name
        object_key = StorageService._generate_unique_key(mime_type)

        # Step 5: Upload the file to MinIO
        try:
            MinIOService.put_object(
                bucket_name=cloudname,
                object_name=object_key,
                data=file.file,
                length=file.size,
                content_type=mime_type,
            )
        except S3Error as e:
            logger.error(f"MinIO S3Error: {str(e)}")
            raise S3ErrorException

        return ObjectUploaded(
            uid=uid,
            cloudname=cloudname,
            object_key=object_key,
            detected_content_type=mime_type,
        )

    @staticmethod
    async def retrieve_image(
        db: AsyncSession,
        uid: UUID,
        object_key: str,
    ) -> tuple[BytesIO, dict]:
        """
        Retrieve an image from the storage.

        Args:
            db (AsyncSession): The database session.
            uid (UUID): The current authenticated user id.
            object_key (str): The key of the object to retrieve.

        Returns:
            Any: The retrieved object data.
        """
        # Step 1: Get user's cloudname
        cloudname = await UserService.get_cloudname(db, uid)

        # Step 2: Retrieve the object from MinIO
        return await StorageService.retrieve_image_by_cloudname(cloudname, object_key)

    @staticmethod
    async def retrieve_image_by_cloudname(
        cloudname: str,
        object_key: str,
    ) -> tuple[BytesIO, dict]:
        """
        Retrieve an image from the storage by cloudname and object key.

        Args:
            cloudname (str): The cloudname of the user.
            object_key (str): The key of the object to retrieve.

        Returns:
            Tuple[BytesIO, Dict[str, str]]: The retrieved object data and its headers.
        """
        try:
            data, headers = MinIOService.get_object(
                bucket_name=cloudname,
                object_name=object_key,
            )
            return data, headers

        except S3Error as e:
            logger.debug(f"MinIO S3Error: {str(e)}")
            raise S3ErrorObjectNotFoundException(detail=f"MinIO S3Error: {str(e)}")

    @staticmethod
    async def delete_image(
        db: AsyncSession,
        uid: UUID,
        object_key: str,
    ):
        """
        Delete an object from the storage.

        Args:
            db (AsyncSession): The database session.
            uid (UUID): The current authenticated user id.
            object_key (str): The key of the object to delete.

        Raises:
            S3ErrorException: If the object is not found or an error occurs during deletion.
        """
        # Step 1: Get user's cloudname
        cloudname = await UserService.get_cloudname(db, uid)

        # Step 2: Delete the object from MinIO
        try:
            MinIOService.delete_object(bucket_name=cloudname, object_name=object_key)

        except S3Error as e:
            logger.debug(f"MinIO S3Error: {str(e)}")
            raise S3ErrorException(detail=f"MinIO S3Error (remove_object): {str(e)}")

        return {"message": f"Object {object_key} deleted successfully"}

    @staticmethod
    async def list_images(
        db: AsyncSession,
        uid: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ObjectOut]:
        """
        List user images with pagination.

        Args:
            db (AsyncSession): The database session.
            uid (UUID): The current authenticated user id.
            skip (int): The number of objects to skip.
            limit (int): The maximum number of objects to return.

        Returns:
            List[ObjectOut]: List of images.
        """
        # Step 1: Get user's cloudname
        cloudname = await UserService.get_cloudname(db, uid)

        # Step 3: List objects from MinIO
        objects = MinIOService.list_objects(cloudname, skip, limit)

        return [
            ObjectOut(
                object_key=obj.object_name,
                etag=obj.etag,
                bucket_name=obj.bucket_name,
                size=obj.size,
                last_modified=obj.last_modified,
            )
            for obj in objects
        ]

    @staticmethod
    async def get_image_stats(
        db: AsyncSession,
        uid: UUID,
        object_key: str,
    ) -> ObjectStats:
        """
        Retrieve the stats of a specific image for the authenticated user.

        Args:
            uid (UUID): The current authenticated user id.
            object_key (str): The name of the object (image).

        Returns:
            ObjectStats: The stats of the specified image.

        Raises:
            HTTPException: If the image stats cannot be retrieved.
        """
        try:
            # Step 1: Get user's cloudname
            cloudname = await UserService.get_cloudname(db, uid)
            # Step 2: Get object stats
            stats = MinIOService.get_object_stats(cloudname, object_key)
            return ObjectStats(
                object_key=object_key,
                etag=stats.etag,
                bucket_name=stats.bucket_name,
                size=stats.size,
                last_modified=stats.last_modified.isoformat(),
                content_type=stats.content_type,
            )
        except Exception as e:
            logger.debug(f"MinIO S3Error: {str(e)}")
            raise S3ErrorException(
                detail=f"Could not retrieve stats for object ({object_key})",
            )

    @staticmethod
    def _validate_image_format(file: UploadFile) -> str | None:
        """
        Validate that the uploaded image is in supported image formats.

        Args:
            file (UploadFile): The uploaded file.

        Returns:
            str: The mime type of the image.
        """
        try:
            image = Image.open(file.file)
            if image.format not in SUPPORTED_IMAGE_FORMATS:
                raise UnsupportedImageFormatException
        except Exception as e:
            raise InvalidImageFileException(detail=str(e))
        # Ensure the file pointer is at the beginning
        file.file.seek(0)
        return image.get_format_mimetype()

    @staticmethod
    def _generate_unique_key(mime_type: str) -> str:
        """
        Generate a unique key for the file to be stored in MinIO.

        Args:
            cloud_name (str): The cloud name of the user.
            mime_type (str): The MIME type of the file.

        Returns:
            str: A unique key for the file.
        """
        # Extract the file extension from the MIME type
        ext = mime_type.split("/")[-1]

        # Get the current timestamp in milliseconds since epoch
        time_milli = int(datetime.now(timezone.utc).timestamp() * 1000)

        # Generate a UUID for global uniqueness
        unique_id = uuid.uuid4().hex

        # Construct the filename
        unique_key = f"{time_milli}_{unique_id}.{ext}"

        return unique_key
