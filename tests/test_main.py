from fastapi.testclient import TestClient

from app.core.error_codes import ErrorCode
from app.core.exceptions import AppException
from app.main import app, settings

client = TestClient(app)


def test_root_returns_service_name() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "data": {"service": settings.app_name, "status": "ok"},
        "message": "OK",
        "stackTrace": None,
        "exceptionCode": None,
    }


def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "data": {"status": "ok"},
        "message": "OK",
        "stackTrace": None,
        "exceptionCode": None,
    }


def test_request_id_header_is_returned() -> None:
    response = client.get("/health", headers={"X-Correlation-ID": "test-request-123"})

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request-123"


def test_validation_error_uses_base_response_format() -> None:
    app.state.settings.debug = False

    response = client.post(
        "/api/v1/background/remove",
        json={},
        headers={"X-API-Key": settings.internal_api_key},
    )

    assert response.status_code == 422
    assert response.json()["data"] is None
    assert response.json()["message"] == ErrorCode.VALIDATION_ERROR.default_message
    assert response.json()["stackTrace"] is None
    assert response.json()["exceptionCode"] == ErrorCode.VALIDATION_ERROR.code


def test_app_exception_uses_base_response_format() -> None:
    app.state.settings.debug = False
    route_path = "/test/app-exception"

    if not any(getattr(route, "path", None) == route_path for route in app.routes):

        @app.get(route_path)
        def raise_app_exception() -> None:
            raise AppException(ErrorCode.NOT_FOUND, "Thing not found")

    response = client.get(route_path)

    assert response.status_code == 404
    assert response.json() == {
        "data": None,
        "message": "Thing not found",
        "stackTrace": None,
        "exceptionCode": ErrorCode.NOT_FOUND.code,
    }
