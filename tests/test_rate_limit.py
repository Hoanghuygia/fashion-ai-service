from fastapi.testclient import TestClient

from app.main import create_app


def test_rate_limit_excludes_health() -> None:
    app = create_app()
    app.state.settings.rate_limit_enabled = True
    app.state.settings.rate_limit_requests = 1
    app.state.settings.rate_limit_window_seconds = 60

    client = TestClient(app)

    assert client.get("/health").status_code == 200
    assert client.get("/health").status_code == 200


def test_rate_limit_returns_base_response_format() -> None:
    app = create_app()
    app.state.settings.rate_limit_enabled = True
    app.state.settings.rate_limit_requests = 1
    app.state.settings.rate_limit_window_seconds = 60

    client = TestClient(app)

    assert client.get("/").status_code == 200
    response = client.get("/")

    assert response.status_code == 429
    assert response.json() == {
        "data": None,
        "message": "Rate limit exceeded",
        "stackTrace": None,
        "exceptionCode": "RATE_LIMIT.001",
    }
