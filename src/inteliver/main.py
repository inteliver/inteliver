"""
    Main script of Inteliver API.

    This script setups the API server using FastAPI.

"""

from fastapi import FastAPI

from inteliver.config import settings
from inteliver.constants import SERVICE_DESCRIPTION, SERVICE_SUMMARY, SERVICE_TITLE
from inteliver.routers import register_routers
from inteliver.utils.lifespan import lifespan
from inteliver.utils.middleware import LanguageMiddleware
from inteliver.version import __version__

app = FastAPI(
    lifespan=lifespan,
    title=SERVICE_TITLE,
    summary=SERVICE_SUMMARY,
    description=SERVICE_DESCRIPTION,
    version=__version__,
    docs_url=settings.openapi_docs_url,
    openapi_url=settings.openapi_json_url,
    # root_path=os.environ.get("FASTAPI_ROOT_PATH", "/api/v1"),
)


register_routers(app)
app.add_middleware(LanguageMiddleware)


def run_service(host: str = settings.app_api_host, port: int = settings.app_api_port):
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_service()
