import pytest
from fastapi import status
from httpx import AsyncClient

from inteliver.config import settings
from inteliver.storage.schemas import ObjectUploaded
from inteliver.users.models import User

test_cases = [
    # resize
    ("i_h_200,i_w_200,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    ("i_h_200,i_w_1.5,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    ("i_h_200,i_w_iw,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    ("i_h_iw,i_w_200,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    ("i_h_ih,i_w_200,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    ("i_h_200,i_w_ih,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    ("i_h_200,i_w_200,i_o_resize_keep", {"content-type": "image/jpeg;q=0.95"}),
    ("i_c_face,i_h_200,i_w_200,i_o_resize_keep", {"content-type": "image/jpeg;q=0.95"}),
    (
        "i_c_face,i_h_200,i_w_200,i_o_resize_keep,i_o_rcrop,i_o_format_png",
        {"content-type": "image/png;q=0.3"},
    ),
    ("i_h_200,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    ("i_w_200,i_o_resize", {"content-type": "image/jpeg;q=0.95"}),
    # crop
    ("i_h_300,i_w_300,i_o_crop", {"content-type": "image/jpeg;q=0.95"}),
    (
        "i_c_x_100,i_c_y_150,i_h_300,i_w_300,i_o_crop",
        {"content-type": "image/jpeg;q=0.95"},
    ),
    ("i_h_300,i_w_300,i_o_crop,i_o_rcrop", {"content-type": "image/jpeg;q=0.95"}),
    (
        "i_h_300,i_w_300,i_o_crop,i_o_rcrop,i_o_format_png",
        {"content-type": "image/png;q=0.3"},
    ),
    ("i_c_face,i_h_200,i_w_200,i_o_crop", {"content-type": "image/jpeg;q=0.95"}),
    # rotate
    ("i_o_rotate_90", {"content-type": "image/jpeg;q=0.95"}),
    ("i_o_rotate_180", {"content-type": "image/jpeg;q=0.95"}),
    ("i_o_rotate_60_1.8", {"content-type": "image/jpeg;q=0.95"}),
    ("i_c_x_250,i_c_y_250,i_o_rotate_60_2", {"content-type": "image/jpeg;q=0.95"}),
    # flip
    ("i_o_flip_v", {"content-type": "image/jpeg;q=0.95"}),
    ("i_o_flip_h", {"content-type": "image/jpeg;q=0.95"}),
    ("i_o_flip_b", {"content-type": "image/jpeg;q=0.95"}),
    # blur
    ("i_o_blur_10", {"content-type": "image/jpeg;q=0.95"}),
    ("i_o_blur_40", {"content-type": "image/jpeg;q=0.95"}),
    (
        "i_c_x_275,i_c_y_275,i_h_75,i_w_75,i_o_blur_25",
        {"content-type": "image/jpeg;q=0.95"},
    ),
    (
        "i_c_x_280,i_c_y_50,i_h_100,i_w_100,i_o_blur_25/i_c_face,i_o_blur_21",
        {"content-type": "image/jpeg;q=0.95"},
    ),
    ("i_c_face,i_o_blur_20", {"content-type": "image/jpeg;q=0.95"}),
    # pixelate
    ("i_o_pixelate_5", {"content-type": "image/jpeg;q=0.95"}),
    ("i_o_pixelate_20", {"content-type": "image/jpeg;q=0.95"}),
    (
        "i_c_x_150,i_c_y_100,i_h_200,i_w_200,i_o_pixelate_10",
        {"content-type": "image/jpeg;q=0.95"},
    ),
    ("i_c_face,i_o_pixelate_10", {"content-type": "image/jpeg;q=0.95"}),
    # sharpen
    ("i_o_sharpen", {"content-type": "image/jpeg;q=0.95"}),
    (
        "i_c_x_275,i_c_y_300,i_h_100,i_w_100,i_o_sharpen",
        {"content-type": "image/jpeg;q=0.95"},
    ),
    ("i_c_face,i_o_sharpen", {"content-type": "image/jpeg;q=0.95"}),
    # gray scale
    ("i_o_gray", {"content-type": "image/jpeg;q=0.95"}),
    (
        "i_c_x_100,i_c_y_300,i_h_200,i_w_200,i_o_gray",
        {"content-type": "image/jpeg;q=0.95"},
    ),
    # compression
    ("i_o_format_jpg", {"content-type": "image/jpeg;q=0.95"}),
    ("i_o_format_jpg_80", {"content-type": "image/jpeg;q=0.8"}),
    ("i_o_format_jpg_40", {"content-type": "image/jpeg;q=0.4"}),
    ("i_o_format_jpg_20", {"content-type": "image/jpeg;q=0.2"}),
    ("i_o_format_webp", {"content-type": "image/webp;q=0.8"}),
    ("i_o_format_webp_80", {"content-type": "image/webp;q=0.8"}),
    ("i_o_format_webp_40", {"content-type": "image/webp;q=0.4"}),
    ("i_o_format_webp_20", {"content-type": "image/webp;q=0.2"}),
    ("i_o_format_png", {"content-type": "image/png;q=0.3"}),
    ("i_o_format_png_1", {"content-type": "image/png;q=0.1"}),
    ("i_o_format_png_6", {"content-type": "image/png;q=0.6"}),
    ("i_o_format_png_9", {"content-type": "image/png;q=0.9"}),
    # text-overlay
    (
        "i_c_y_100,i_c_x_-180,i_o_text_Your-Brand_1.5_4_14_70_160",
        {"content-type": "image/jpeg;q=0.95"},
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("command, expected_result", test_cases)
async def test_image_processing_success(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    pre_existing_user: User,
    command: str,
    expected_result: dict,
):
    """Test the process_image endpoint."""
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{command}/{uploaded_image.object_key}"
    )
    print(response.headers["content-type"])
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == expected_result["content-type"]
    # TODO: check the response binary data against the expected image data


@pytest.mark.asyncio
async def test_test_image_processing_invalid_command(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    pre_existing_user: User,
):
    """Test the process_image endpoint."""
    invaild_command = "invalid_command"
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{invaild_command}/{uploaded_image.object_key}"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_test_image_processing_invalid_command_operation(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    pre_existing_user: User,
):
    """Test the process_image endpoint."""
    invaild_command = "i_h_200,i_w_200,i_o_invalid"
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{invaild_command}/{uploaded_image.object_key}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_test_image_processing_non_existing_cloudname(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
):
    """Test the process_image endpoint."""
    non_existing_cloudname = "non_existing_cloudname"
    command = "i_h_200,i_w_200,i_o_resize"
    response = await test_client.get(
        f"{settings.api_prefix}/image/{non_existing_cloudname}/{command}/{uploaded_image.object_key}"
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_test_image_processing_invalid_int_arg(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    pre_existing_user: User,
):
    """Test the process_image endpoint."""
    invalid_command = "i_h_200,i_w_ten,i_o_resize"
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{invalid_command}/{uploaded_image.object_key}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_test_image_processing_invalid_int_arg(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    pre_existing_user: User,
):
    """Test the process_image endpoint."""
    invalid_command = "i_h_200,i_w_ten,i_o_resize"
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{invalid_command}/{uploaded_image.object_key}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_test_image_processing_invalid_float_arg(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    pre_existing_user: User,
):
    """Test the process_image endpoint."""
    invalid_command = "i_h_200,i_w_1.ten,i_o_resize"
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{invalid_command}/{uploaded_image.object_key}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


test_cases_face = [
    # center face
    ("i_c_face,i_h_200,i_w_200,i_o_resize_keep", {"content-type": "image/jpeg;q=0.95"}),
    # profile picture
    (
        "i_c_face,i_h_200,i_w_200,i_o_resize_keep,i_o_rcrop,i_o_format_png",
        {"content-type": "image/png;q=0.3"},
    ),
    # face crop
    ("i_c_face,i_h_200,i_w_200,i_o_crop", {"content-type": "image/jpeg;q=0.95"}),
    # blur face
    ("i_c_face,i_o_blur_20", {"content-type": "image/jpeg;q=0.95"}),
    # pixelate face
    ("i_c_face,i_o_pixelate_10", {"content-type": "image/jpeg;q=0.95"}),
    # sharpen face
    ("i_c_face,i_o_sharpen", {"content-type": "image/jpeg;q=0.95"}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("command, expected_result", test_cases_face)
async def test_image_processing_face_success(
    test_client: AsyncClient,
    uploaded_image_face: ObjectUploaded,
    pre_existing_user: User,
    command: str,
    expected_result: dict,
):
    """Test the process_image endpoint."""
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{command}/{uploaded_image_face.object_key}"
    )
    print(response.headers["content-type"])
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["content-type"] == expected_result["content-type"]
    # TODO: check the response binary data against the expected image data


test_cases_insufficient_command_arg = [
    # arg center
    ("i_c_x,i_c_y_275,i_h_75,i_w_75,i_o_blur_25", {}),
    ("i_c_x_275,i_c_y,i_h_75,i_w_75,i_o_blur_25", {}),
    # arg rotate
    ("i_o_rotate", {}),
    # arg resize
    ("i_o_resize", {}),
    # arg format
    ("i_o_format", {}),
    # arg flip
    ("i_o_flip", {}),
    ("i_o_flip_invalid", {}),
    # arg pixelate
    ("i_o_pixelate", {}),
    # arg text-overly
    ("i_c_y_-100,i_c_x_-180,i_o_text_Your-Brand", {}),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command, expected_result", test_cases_insufficient_command_arg
)
async def test_test_image_processing_insufficient_command_arg(
    test_client: AsyncClient,
    uploaded_image: ObjectUploaded,
    pre_existing_user: User,
    command: str,
    expected_result: dict,
):
    """Test the process_image endpoint."""
    response = await test_client.get(
        f"{settings.api_prefix}/image/{pre_existing_user.cloudname}/{command}/{uploaded_image.object_key}"
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
