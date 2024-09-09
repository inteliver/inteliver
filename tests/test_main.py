from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from inteliver.config import settings
from inteliver.main import app, run_service
from inteliver.version import __version__


def test_app_initialization():
    """
    Test that the FastAPI app is initialized with the correct settings.
    """
    assert isinstance(app, FastAPI)
    assert app.version == __version__


def test_run_service():
    """
    Test that `run_service` calls `uvicorn.run` with the correct parameters.
    """
    with patch("inteliver.main.uvicorn.run", new_callable=MagicMock) as mock_run:
        run_service()
        mock_run.assert_called_once_with(
            app, host=settings.app_api_host, port=settings.app_api_port
        )


@pytest.mark.asyncio
async def test_service_up_and_running(test_client: AsyncClient):
    """
    Test that the service is up and responds to HTTP requests.
    """
    response = await test_client.get("/")
    assert response.status_code == 200
