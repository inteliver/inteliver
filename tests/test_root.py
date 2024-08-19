from fastapi.testclient import TestClient

from inteliver.main import app

client = TestClient(app)


def test_root_main():
    response = client.get("/")
    assert response.status_code == 200
