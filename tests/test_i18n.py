from fastapi.testclient import TestClient

from inteliver.main import app

client = TestClient(app)


def test_i18n_root_en():
    # Send a request with Accept-Language: en header
    response = client.get("/", headers={"Accept-Language": "en"})

    assert response.status_code == 200

    # Parse the JSON response
    response_data = response.json()

    # Assert the text of the returned JSON
    assert response_data["message"] == "API is up and ok."


def test_i18n_root_fa():
    # Send a request with Accept-Language: en header
    response = client.get("/", headers={"Accept-Language": "fa"})

    assert response.status_code == 200

    # Parse the JSON response
    response_data = response.json()

    # Assert the text of the returned JSON
    assert response_data["message"] == "API به درستی کار می‌کند"
