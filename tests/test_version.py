from fastapi.testclient import TestClient

from inteliver.main import app
from inteliver.version import __version__

client = TestClient(app)


def test_root_main():
    response = client.get("/api/v1/inteliver-api/version")
    assert response.status_code == 200
    assert response.json() == {"version": __version__}
