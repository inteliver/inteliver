from io import BytesIO

import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from inteliver.image.exceptions import (
    CloudnameNotExistsException,
    ImageDecodeException,
    ImageProcessorException,
)
from inteliver.image.image_processor import ImageProcessor
from inteliver.storage.service import StorageService
from inteliver.users.exceptions import UserNotFoundException
from inteliver.users.service import UserService


class ImageService:
    @staticmethod
    async def process_image(
        db: AsyncSession,
        cloudname: str,
        commands: str,
        object_key: str,
    ):
        """
        Process an image with specified commands.

        Args:
            cloudname (str): The user's cloud name.
            commands (str): The commands to apply to the image.
            object_key (str): The key of the resource.
            db (AsyncSession): The database session.

        Returns:
            BytesIO: The modified image.
        """
        # 1. check structure format of the url: (IT IS CHECKED BY THE FASTAPI PYDANTIC)
        # example: /{cloudname}/{commands}/{object_id}
        # 2. check cloudname exists (return the user with this cloudname)

        # 3. check the commands validity
        # 4. get user active endpoint (currently we only have one main s3 storage endpoint)
        # 5. retrieve image data in an async way from s3 storage
        # (other protocols like http can be handled in other router endpoint
        # or with a specific command at begining of command path)
        # 6. check image format to be in the supported image formats
        # (if image type is not supported return the image without modifications)
        # 7. for each commands run the image modifier service process
        # 8. push statistics into influxdb
        # 9. set any custome response headers, like cache control
        # 10. return the the data using FastAPI StreamingReponse

        # Check if the cloudname exists and get the user information
        try:
            _user = await UserService.get_user_by_cloudname(db, cloudname)
        except UserNotFoundException as e:
            raise CloudnameNotExistsException(
                detail=f"The requested cloudname {cloudname} does not exists. detail: {str(e)}"
            )

        # TODO check the commands validity

        # TODO get user active storage endpoint
        # currently we only have one main s3 storage endpoint

        # Fetch the image from MinIO
        data, headers = await StorageService.retrieve_image_by_cloudname(
            cloudname, object_key
        )
        image_format = str(headers.get("Content-Type"))

        # Convert image to numpy
        image = ImageService._convert_bytes_to_numpy(data)

        # Apply the commands to the image

        modified_image, image_format = ImageService.apply_commands(
            image,
            commands,
            image_format,
        )

        # encode image data with the image format
        modified_image_encoded = ImageService.imencode(modified_image, image_format)

        return BytesIO(modified_image_encoded), image_format

    @staticmethod
    def apply_commands(
        image: np.ndarray, commands: str, image_format: str
    ) -> tuple[np.ndarray, str]:
        """
        Apply the specified commands to the image.

        Args:
            image (np.ndarray): The image data to modify.
            commands (str): The commands to apply.
            image_format: The originam image format.

        Returns:
            Image.Image: The modified image.
        """
        image_processor = ImageProcessor()
        # Split the commands and apply each one
        command_list = commands.split("/")
        subcommands_list = [cmd.split(",") for cmd in command_list]
        for command_group in subcommands_list:
            image_format, image = image_processor.process(
                command_group, image_format, image
            )
            if image_format.startswith("error"):
                raise ImageProcessorException(
                    detail=f"Can not apply image modification: {str(image_format)}"
                )
        return image, image_format

    @staticmethod
    def imencode(image: np.ndarray, format: str) -> bytes:
        """
        Uses OpenCV to encode the image data using the specified format.

        Args:
            image (np.ndarray): The image to encode.
            format (str): The format to encode the image in (e.g., 'image/jpeg').

        Returns:
            bytes: The encoded image in bytes.

        Raises:
            ValueError: If the image format is invalid or encoding fails.
        """

        if not format.startswith("image/"):
            raise ValueError(f"Invalid image format: {format}")

        format = format[6:]  # Remove "image/" prefix

        if format.startswith("jpeg;q="):
            q_str = format[7:]
            try:
                q = float(q_str)
            except (ValueError, TypeError):
                q = 0.95
            params = [int(cv2.IMWRITE_JPEG_QUALITY), int(q * 100)]
            result, encoded_image = cv2.imencode(".jpg", image, params)

        elif format.startswith("png;q="):
            q_str = format[6:]
            try:
                q = float(q_str)
            except (ValueError, TypeError):
                q = 0.3
            params = [int(cv2.IMWRITE_PNG_COMPRESSION), int(q * 10)]
            result, encoded_image = cv2.imencode(".png", image, params)

        elif format.startswith("webp;q="):
            q_str = format[7:]
            try:
                q = float(q_str)
            except (ValueError, TypeError):
                q = 0.8
            params = [int(cv2.IMWRITE_WEBP_QUALITY), int(q * 100)]
            result, encoded_image = cv2.imencode(".webp", image, params)

        else:
            raise ValueError(f"Invalid image format: {format}")

        if not result:
            raise ValueError("Image encoding failed")

        return encoded_image.tobytes()

    @staticmethod
    def _convert_bytes_to_numpy(data: BytesIO) -> np.ndarray:
        # Convert image to numpy
        try:
            image_np_array = np.frombuffer(data.read(), np.uint8)
            image = cv2.imdecode(image_np_array, cv2.IMREAD_UNCHANGED)

        except Exception as e:
            raise ImageDecodeException(
                detail=f"Can not decode image data (cv2): {str(e)}"
            )
        return image
