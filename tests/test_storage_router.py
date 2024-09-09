from datetime import datetime, timezone
from io import BytesIO

import pytest
from fastapi import UploadFile, status
from httpx import AsyncClient
from minio import Minio, S3Error

from inteliver.auth.schemas import Token
from inteliver.config import settings
from inteliver.storage.exceptions import S3ErrorException
from inteliver.storage.schemas import ObjectUploaded
from inteliver.storage.service import MinIOService
from inteliver.users.models import User

# Test scenarios for storage upload image
# Endpoint post /storage/images


@pytest.mark.asyncio
async def test_upload_image_success(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
    minio_client: Minio,
    test_image_file: UploadFile,
    cleanup_minio,
):
    # Send request
    response = await test_client.post(
        f"{settings.api_prefix}/storage/images",
        files={"file": (test_image_file.filename, test_image_file.file, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "uid" in data
    assert data["cloudname"] == pre_existing_user.cloudname
    assert "object_key" in data
    assert data["detected_content_type"] == "image/jpeg"

    # Verify the object exists in MinIO
    assert minio_client.bucket_exists(pre_existing_user.cloudname)
    assert minio_client.stat_object(pre_existing_user.cloudname, data["object_key"])


@pytest.mark.asyncio
async def test_upload_image_invalid_content_type(
    test_client: AsyncClient,
    auth_token: Token,
    test_image_file: UploadFile,
    cleanup_minio,
):
    # Send request
    # Although request content type is set uncorrectly to 'text/plain',
    # the storage service will handle image upload and return the
    # correct mime type, if the image is valid and the image type
    # is in the supported formats
    response = await test_client.post(
        f"{settings.api_prefix}/storage/images",
        files={"file": (test_image_file.filename, test_image_file.file, "text/plain")},
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    # Assert response
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "uid" in data
    assert data["detected_content_type"] == "image/jpeg"


@pytest.mark.asyncio
async def test_upload_image_invalid_image_content(
    test_client: AsyncClient,
    auth_token: Token,
    cleanup_minio,
):
    # Prepare test data
    file = UploadFile(
        filename="jpg_test_image.jpg", file=BytesIO(b"invalid image content")
    )

    # Send request
    response = await test_client.post(
        f"{settings.api_prefix}/storage/images",
        files={"file": (file.filename, file.file, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    # Assert response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "cannot identify image file" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_image_unsupported_image_format(
    test_client: AsyncClient,
    auth_token: Token,
    cleanup_minio,
):
    # Prepare test data
    filepath = "tests/assets/images/gif_test_image.gif"
    with open(filepath, "rb") as image:
        file = UploadFile(filename="gif_test_image.gif", file=BytesIO(image.read()))

    # Send request
    response = await test_client.post(
        f"{settings.api_prefix}/storage/images",
        files={"file": (file.filename, file.file, "image/gif")},
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    # Assert response
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "Unsupported image format" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_image_unauthorized(
    test_client: AsyncClient,
    test_image_file: UploadFile,
    cleanup_minio,
):
    # Send request without authentication
    response = await test_client.post(
        f"{settings.api_prefix}/storage/images",
        files={"file": (test_image_file.filename, test_image_file.file, "image/jpeg")},
    )

    # Assert response
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_upload_image_minio_error(
    test_client: AsyncClient,
    auth_token: Token,
    test_image_file: UploadFile,
    mocker,
    cleanup_minio,
):
    # Mock MinIOService to raise an S3Error
    mocker.patch.object(
        MinIOService,
        "put_object",
        side_effect=S3Error(
            code=500,
            message="Mocked S3Error",
            request_id=None,
            host_id=None,
            resource=None,
            response=None,
        ),
    )

    # Send request
    response = await test_client.post(
        f"{settings.api_prefix}/storage/images",
        files={"file": (test_image_file.filename, test_image_file.file, "image/jpeg")},
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    # Assert response
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


# Test scenarios for storage list of images
# Endpoint get /storage/images


# list objects
@pytest.mark.asyncio
async def test_list_images_success(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
    setup_minio_data,
):
    response = await test_client.get(
        f"{settings.api_prefix}/storage/images",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 10
    for item in data:
        assert "object_key" in item
        assert "etag" in item
        assert "bucket_name" in item
        assert "size" in item
        assert "last_modified" in item


@pytest.mark.asyncio
async def test_list_images_empty(
    test_client: AsyncClient,
    auth_token: Token,
    pre_existing_user: User,
    minio_client,
):
    # Ensure the bucket is empty
    bucket_name = pre_existing_user.cloudname
    if minio_client.bucket_exists(bucket_name):
        objects = minio_client.list_objects(bucket_name, recursive=True)
        for obj in objects:
            minio_client.remove_object(bucket_name, obj.object_name)
    else:
        minio_client.make_bucket(bucket_name)
    response = await test_client.get(
        f"{settings.api_prefix}/storage/images",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_list_images_unauthorized(
    test_client: AsyncClient,
):
    response = await test_client.get(f"{settings.api_prefix}/storage/images")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_list_images_minio_error(
    test_client: AsyncClient,
    auth_token: Token,
    mocker,
):
    # Mock MinIOService to raise an exception
    mocker.patch.object(
        MinIOService,
        "list_objects",
        side_effect=S3Error(
            code=500,
            message="Mocked S3Error",
            request_id=None,
            host_id=None,
            resource=None,
            response=None,
        ),
    )

    response = await test_client.get(
        f"{settings.api_prefix}/storage/images",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Error listing objects" in response.json()["detail"]


# Test scenarios for storage retrieve image data
# Endpoint get /storage/images/{object_key}


@pytest.mark.asyncio
async def test_retrieve_image_success(
    test_client: AsyncClient,
    auth_token: Token,
    uploaded_image: ObjectUploaded,
    cleanup_minio,
):
    response = await test_client.get(
        f"{settings.api_prefix}/storage/images/{uploaded_image.object_key}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"].startswith("image/")
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_retrieve_image_not_found(
    test_client: AsyncClient,
    auth_token: Token,
):
    non_existent_key = "non_existent_image.jpg"
    response = await test_client.get(
        f"{settings.api_prefix}/storage/images/{non_existent_key}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_retrieve_image_unauthorized(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    cleanup_minio,
):
    response = await test_client.get(
        f"{settings.api_prefix}/storage/images/{uploaded_image.object_key}",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Test scenarios for storage delete image data
# Endpoint delete /storage/images/{object_key}


@pytest.mark.asyncio
async def test_delete_image_success(
    test_client: AsyncClient,
    auth_token: Token,
    uploaded_image: ObjectUploaded,
    cleanup_minio,
):
    response = await test_client.delete(
        f"{settings.api_prefix}/storage/images/{uploaded_image.object_key}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "message": f"Object {uploaded_image.object_key} deleted successfully"
    }


@pytest.mark.asyncio
async def test_delete_image_not_found(
    test_client: AsyncClient,
    auth_token: Token,
):
    non_existent_key = "non_existent_image.jpg"
    response = await test_client.delete(
        f"{settings.api_prefix}/storage/images/{non_existent_key}",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_image_unauthorized(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    cleanup_minio,
):
    response = await test_client.delete(
        f"{settings.api_prefix}/storage/images/{uploaded_image.object_key}",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_image_stats_success(
    test_client: AsyncClient,
    auth_token: Token,
    uploaded_image: ObjectUploaded,
    cleanup_minio,
):

    response = await test_client.get(
        f"{settings.api_prefix}/storage/{uploaded_image.object_key}/stats",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )

    assert response.status_code == status.HTTP_200_OK
    stats = response.json()
    assert stats["object_key"] == uploaded_image.object_key
    assert stats["bucket_name"] == uploaded_image.cloudname
    assert "last_modified" in stats
    assert stats["content_type"] == uploaded_image.detected_content_type


@pytest.mark.asyncio
async def test_get_image_stats_not_found(
    test_client: AsyncClient,
    auth_token: Token,
):
    non_existent_key = "non_existent_image.jpg"
    response = await test_client.get(
        f"{settings.api_prefix}/storage/{non_existent_key}/stats",
        headers={"Authorization": f"Bearer {auth_token.access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_image_stats_unauthorized(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    cleanup_minio,
):
    response = await test_client.get(
        f"{settings.api_prefix}/storage/{uploaded_image.object_key}/stats",
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
