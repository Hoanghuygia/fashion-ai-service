from fastapi.testclient import TestClient

from app.core.error_codes import ErrorCode
from app.main import app, settings

client = TestClient(app)


def test_protected_route_rejects_missing_api_key() -> None:
    response = client.post("/api/v1/background/remove", json={"image_id": "att_1"})

    assert response.status_code == 401
    assert response.json()["exceptionCode"] == ErrorCode.UNAUTHORIZED.code
    assert response.json()["data"] is None


def test_protected_route_rejects_wrong_api_key() -> None:
    response = client.post(
        "/api/v1/background/remove",
        json={"image_id": "att_1"},
        headers={"X-API-Key": "wrong-key"},
    )

    assert response.status_code == 401
    assert response.json()["exceptionCode"] == ErrorCode.UNAUTHORIZED.code


def test_valid_api_key_passes_auth() -> None:
    # A valid key clears the auth gate; the request then fails validation (422),
    # proving auth ran and passed rather than short-circuiting with 401.
    response = client.post(
        "/api/v1/background/remove",
        json={},
        headers={"X-API-Key": settings.internal_api_key},
    )

    assert response.status_code == 422


def test_health_is_public() -> None:
    assert client.get("/health").status_code == 200
    assert client.get("/").status_code == 200
