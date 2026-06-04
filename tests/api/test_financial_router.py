"""Pruebas de endpoints financieros de la API."""

from datetime import date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_financial_query_service
from novitec_dwh.api.main import app
from novitec_dwh.core.config import get_settings
from novitec_dwh.contexts.financial.application.dto import (
    CreditNoteRequestListItem,
    FinancialSummary,
    NotificationListItem,
    OrderPriceListItem,
    PaginatedResult,
)


class FakeFinancialQueryService:
    """Doblez de servicio para probar los endpoints sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa un contenedor simple para capturar filtros."""

        self.last_summary_filters: dict | None = None
        self.last_credit_note_filters: dict | None = None
        self.last_order_price_filters: dict | None = None
        self.last_notification_filters: dict | None = None

    def get_summary(self, **kwargs) -> FinancialSummary:
        """Devuelve un resumen financiero fijo para pruebas."""

        self.last_summary_filters = kwargs
        return FinancialSummary(
            extraction_id="financial_20260603_204252",
            total_solicitudes_nc=226,
            solicitudes_aprobadas=100,
            solicitudes_rechazadas=50,
            solicitudes_pendientes=76,
            total_registros_ingreso=39,
            monto_total_ingresos=Decimal("1250.50"),
            total_notificaciones=831,
            total_notificaciones_leidas=420,
        )

    def list_credit_note_requests(self, **kwargs) -> PaginatedResult[CreditNoteRequestListItem]:
        """Devuelve una pagina fija de solicitudes NC."""

        self.last_credit_note_filters = kwargs
        return PaginatedResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                CreditNoteRequestListItem(
                    extraction_id="financial_20260603_204252",
                    request_number="NC-001",
                    order_id=1,
                    order_number="ORD-001",
                    request_date=date(2026, 6, 3),
                    status_name="Aprobada",
                    subject_name="Solicitud de prueba",
                    admin_name="Admin",
                    rejection_reason=None,
                    technician_name="Tecnico 1",
                    created_at=datetime(2026, 6, 3, 10, 0, 0),
                )
            ],
        )

    def list_order_prices(self, **kwargs) -> PaginatedResult[OrderPriceListItem]:
        """Devuelve una pagina fija de ingresos por orden."""

        self.last_order_price_filters = kwargs
        return PaginatedResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OrderPriceListItem(
                    extraction_id="financial_20260603_204252",
                    order_id=1,
                    order_number="ORD-001",
                    service_name="Revision",
                    standard_service_name="Revision estandar",
                    amount=Decimal("20.00"),
                    standard_amount=Decimal("25.00"),
                    created_at=datetime(2026, 6, 3, 9, 0, 0),
                )
            ],
        )

    def list_notifications(self, **kwargs) -> PaginatedResult[NotificationListItem]:
        """Devuelve una pagina fija de notificaciones."""

        self.last_notification_filters = kwargs
        return PaginatedResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                NotificationListItem(
                    extraction_id="financial_20260603_204252",
                    order_id=1,
                    order_number="ORD-001",
                    nc_id=1,
                    notification_type="nc_aprobada",
                    is_read=True,
                    technician_name="Tecnico 1",
                    created_at=datetime(2026, 6, 3, 11, 0, 0),
                )
            ],
        )


def test_get_financial_summary() -> None:
    """Valida la respuesta del endpoint de resumen financiero."""

    app.dependency_overrides[get_financial_query_service] = lambda: FakeFinancialQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/financial/summary")

    assert response.status_code == 200
    assert response.json()["total_solicitudes_nc"] == 226

    app.dependency_overrides.clear()


def test_get_financial_summary_with_filters() -> None:
    """Valida que el resumen financiero reciba filtros opcionales."""

    fake_service = FakeFinancialQueryService()
    app.dependency_overrides[get_financial_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/financial/summary",
        params={
            "order_id": 10,
            "order_number": "ORD-010",
            "technician_name": "Tecnico",
            "admin_name": "Supervisor",
            "status_name": "Aprobada",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
        },
    )

    assert response.status_code == 200
    assert response.json()["total_solicitudes_nc"] == 226
    assert fake_service.last_summary_filters == {
        "order_id": 10,
        "order_number": "ORD-010",
        "technician_name": "Tecnico",
        "admin_name": "Supervisor",
        "status_name": "Aprobada",
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
    }

    app.dependency_overrides.clear()


def test_list_credit_note_requests() -> None:
    """Valida la respuesta del listado de solicitudes NC."""

    app.dependency_overrides[get_financial_query_service] = lambda: FakeFinancialQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/financial/credit-note-requests")

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 1
    assert response.json()["items"][0]["request_number"] == "NC-001"

    app.dependency_overrides.clear()


def test_list_credit_note_requests_with_fine_filters() -> None:
    """Valida que los filtros finos de solicitudes NC lleguen al servicio."""

    fake_service = FakeFinancialQueryService()
    app.dependency_overrides[get_financial_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/financial/credit-note-requests",
        params={
            "limit": 25,
            "offset": 5,
            "search": "NC",
            "request_number": "NC-001",
            "order_id": 10,
            "order_number": "ORD-010",
            "status_name": "Aprobada",
            "technician_name": "Tecnico",
            "admin_name": "Supervisor",
            "subject_name": "Pantalla",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "admin_name",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["limit"] == 25
    assert response.json()["meta"]["offset"] == 5
    assert response.json()["meta"]["count"] == 1
    assert response.json()["meta"]["page"] == 1
    assert response.json()["meta"]["total_pages"] == 1
    assert response.json()["meta"]["has_next"] is False
    assert response.json()["meta"]["has_previous"] is True
    assert fake_service.last_credit_note_filters == {
        "limit": 25,
        "offset": 5,
        "search": "NC",
        "request_number": "NC-001",
        "order_id": 10,
        "order_number": "ORD-010",
        "status_name": "Aprobada",
        "technician_name": "Tecnico",
        "admin_name": "Supervisor",
        "subject_name": "Pantalla",
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "admin_name",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_order_prices() -> None:
    """Valida la respuesta del listado de ingresos por orden."""

    app.dependency_overrides[get_financial_query_service] = lambda: FakeFinancialQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/financial/order-prices")

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 1
    assert response.json()["items"][0]["service_name"] == "Revision"

    app.dependency_overrides.clear()


def test_list_order_prices_with_fine_filters() -> None:
    """Valida que los filtros finos de ingresos lleguen al servicio."""

    fake_service = FakeFinancialQueryService()
    app.dependency_overrides[get_financial_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/financial/order-prices",
        params={
            "limit": 10,
            "offset": 2,
            "order_id": 88,
            "service_name": "Revision",
            "order_number": "ORD-088",
            "standard_service_name": "Revision estandar",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "amount",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["limit"] == 10
    assert response.json()["meta"]["offset"] == 2
    assert response.json()["meta"]["has_previous"] is True
    assert fake_service.last_order_price_filters == {
        "limit": 10,
        "offset": 2,
        "order_id": 88,
        "service_name": "Revision",
        "order_number": "ORD-088",
        "standard_service_name": "Revision estandar",
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "amount",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_notifications() -> None:
    """Valida la respuesta del listado de notificaciones financieras."""

    app.dependency_overrides[get_financial_query_service] = lambda: FakeFinancialQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/financial/notifications")

    assert response.status_code == 200
    assert response.json()["meta"]["total"] == 1
    assert response.json()["items"][0]["notification_type"] == "nc_aprobada"

    app.dependency_overrides.clear()


def test_list_notifications_with_fine_filters() -> None:
    """Valida que los filtros finos de notificaciones lleguen al servicio."""

    fake_service = FakeFinancialQueryService()
    app.dependency_overrides[get_financial_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/financial/notifications",
        params={
            "limit": 15,
            "offset": 3,
            "order_id": 7,
            "order_number": "ORD-007",
            "nc_id": 99,
            "notification_type": "nc_aprobada",
            "is_read": "true",
            "technician_name": "Tecnico 1",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "notification_type",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["limit"] == 15
    assert response.json()["meta"]["offset"] == 3
    assert response.json()["meta"]["has_previous"] is True
    assert fake_service.last_notification_filters == {
        "limit": 15,
        "offset": 3,
        "order_id": 7,
        "order_number": "ORD-007",
        "nc_id": 99,
        "notification_type": "nc_aprobada",
        "is_read": True,
        "technician_name": "Tecnico 1",
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "notification_type",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_financial_endpoints_require_token_when_auth_is_enabled() -> None:
    """Valida que la API financiera rechace accesos sin token cuando se habilita auth."""

    settings = get_settings()
    original_enabled = settings.api_auth_enabled
    original_token = settings.api_auth_token
    settings.api_auth_enabled = True
    settings.api_auth_token = "token-prueba"

    try:
        app.dependency_overrides[get_financial_query_service] = lambda: FakeFinancialQueryService()
        client = TestClient(app)

        response = client.get("/api/v1/financial/summary")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthorized"
        assert response.json()["error"]["message"] == "No autorizado."
        assert response.headers["X-Request-ID"] == response.json()["error"]["request_id"]
    finally:
        settings.api_auth_enabled = original_enabled
        settings.api_auth_token = original_token
        app.dependency_overrides.clear()


def test_financial_endpoints_accept_valid_token_when_auth_is_enabled() -> None:
    """Valida que la API financiera acepte el token bearer configurado."""

    settings = get_settings()
    original_enabled = settings.api_auth_enabled
    original_token = settings.api_auth_token
    settings.api_auth_enabled = True
    settings.api_auth_token = "token-prueba"

    try:
        app.dependency_overrides[get_financial_query_service] = lambda: FakeFinancialQueryService()
        client = TestClient(app)

        response = client.get(
            "/api/v1/financial/summary",
            headers={"Authorization": "Bearer token-prueba"},
        )

        assert response.status_code == 200
        assert response.json()["total_solicitudes_nc"] == 226
    finally:
        settings.api_auth_enabled = original_enabled
        settings.api_auth_token = original_token
        app.dependency_overrides.clear()
