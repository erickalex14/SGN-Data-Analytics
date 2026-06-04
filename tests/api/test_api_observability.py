"""Pruebas de trazabilidad y errores uniformes de la API."""

import logging

from fastapi.testclient import TestClient

from novitec_dwh.api.main import app


def _ensure_test_error_route() -> None:
    """Registra una ruta de prueba para forzar errores internos controlados."""

    existing_paths = {route.path for route in app.router.routes}
    if "/api/v1/test-error" in existing_paths:
        return

    @app.get("/api/v1/test-error")
    def raise_test_error() -> dict:
        """Fuerza una excepcion interna para probar el handler global."""

        raise RuntimeError("Fallo controlado de prueba")


def test_health_response_includes_request_id_header(caplog) -> None:
    """Valida que cada respuesta exitosa incluya request_id y log de acceso."""

    client = TestClient(app)

    with caplog.at_level(logging.INFO, logger="novitec_dwh.api.access"):
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    assert any(
        "Solicitud HTTP procesada" in record.message and "/api/v1/health" in record.message
        for record in caplog.records
    )


def test_not_found_uses_uniform_error_payload() -> None:
    """Valida el formato uniforme para errores 404."""

    client = TestClient(app)
    response = client.get("/api/v1/no-existe")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"
    assert response.json()["error"]["message"] == "Recurso no encontrado."
    assert response.json()["error"]["path"] == "/api/v1/no-existe"
    assert response.headers["X-Request-ID"] == response.json()["error"]["request_id"]


def test_validation_error_uses_uniform_error_payload() -> None:
    """Valida el formato uniforme para errores 422 de validacion."""

    client = TestClient(app)
    response = client.get("/api/v1/financial/credit-note-requests?limit=0")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert response.json()["error"]["message"] == "La solicitud contiene parametros invalidos."
    assert isinstance(response.json()["error"]["details"], list)
    assert response.headers["X-Request-ID"] == response.json()["error"]["request_id"]


def test_internal_server_error_uses_uniform_error_payload() -> None:
    """Valida el formato uniforme para errores 500 inesperados."""

    _ensure_test_error_route()
    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/api/v1/test-error")

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_server_error"
    assert response.json()["error"]["message"] == "Ocurrio un error interno en el servidor."
    assert response.json()["error"]["path"] == "/api/v1/test-error"
    assert response.headers["X-Request-ID"] == response.json()["error"]["request_id"]
