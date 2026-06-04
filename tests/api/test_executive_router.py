"""Pruebas del endpoint ejecutivo consolidado."""

from datetime import date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_executive_dashboard_service
from novitec_dwh.api.main import app
from novitec_dwh.core.config import get_settings
from novitec_dwh.contexts.executive.application.dto import (
    ExecutiveDashboard,
    ExecutiveDashboardFilters,
    ExecutiveDashboardKpis,
)
from novitec_dwh.contexts.financial.application.dto import FinancialSummary
from novitec_dwh.contexts.operational.application.dto_query import OperationalSummary


class FakeExecutiveDashboardService:
    """Doblez de servicio para probar el endpoint ejecutivo sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa un contenedor para capturar filtros del dashboard."""

        self.last_filters: dict | None = None

    def get_dashboard(self, **kwargs) -> ExecutiveDashboard:
        """Devuelve un dashboard ejecutivo fijo para pruebas."""

        self.last_filters = kwargs
        return ExecutiveDashboard(
            generated_at=datetime(2026, 6, 4, 16, 30, 0),
            filters=ExecutiveDashboardFilters(
                date_from=kwargs.get("date_from"),
                date_to=kwargs.get("date_to"),
                technician_name=kwargs.get("technician_name"),
                branch_name=kwargs.get("branch_name"),
                admin_name=kwargs.get("admin_name"),
                status_name=kwargs.get("status_name"),
                order_type=kwargs.get("order_type"),
            ),
            operational=OperationalSummary(
                extraction_id="operational_20260604_202615",
                total_ordenes=1500,
                ordenes_abiertas=700,
                ordenes_entregadas=650,
                ordenes_con_garantia=120,
                total_preordenes=60,
                total_asignaciones_tecnicos=12,
                promedio_dias_ciclo=Decimal("4.50"),
            ),
            financial=FinancialSummary(
                extraction_id="financial_20260603_204252",
                total_solicitudes_nc=226,
                solicitudes_aprobadas=182,
                solicitudes_rechazadas=4,
                solicitudes_pendientes=40,
                total_registros_ingreso=39,
                monto_total_ingresos=Decimal("546.00"),
                total_notificaciones=831,
                total_notificaciones_leidas=500,
            ),
            kpis=ExecutiveDashboardKpis(
                tasa_aprobacion_nc=Decimal("80.53"),
                tasa_notificaciones_leidas=Decimal("60.17"),
                tasa_ordenes_entregadas=Decimal("43.33"),
                tasa_ordenes_abiertas=Decimal("46.67"),
                tasa_ordenes_garantia=Decimal("8.00"),
            ),
        )


def test_get_executive_dashboard() -> None:
    """Valida la respuesta base del dashboard ejecutivo."""

    app.dependency_overrides[get_executive_dashboard_service] = lambda: FakeExecutiveDashboardService()
    client = TestClient(app)

    response = client.get("/api/v1/dashboard/executive")

    assert response.status_code == 200
    assert response.json()["operational"]["total_ordenes"] == 1500
    assert response.json()["financial"]["total_solicitudes_nc"] == 226
    assert response.json()["kpis"]["tasa_aprobacion_nc"] == "80.53"

    app.dependency_overrides.clear()


def test_get_executive_dashboard_with_filters() -> None:
    """Valida que los filtros globales lleguen al servicio ejecutivo."""

    fake_service = FakeExecutiveDashboardService()
    app.dependency_overrides[get_executive_dashboard_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/dashboard/executive",
        params={
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "technician_name": "Tecnico 1",
            "branch_name": "Quito",
            "admin_name": "Supervisor",
            "status_name": "Aprobada",
            "order_type": "personal",
        },
    )

    assert response.status_code == 200
    assert response.json()["filters"]["branch_name"] == "Quito"
    assert fake_service.last_filters == {
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "technician_name": "Tecnico 1",
        "branch_name": "Quito",
        "admin_name": "Supervisor",
        "status_name": "Aprobada",
        "order_type": "personal",
    }

    app.dependency_overrides.clear()


def test_executive_endpoint_requires_token_when_auth_is_enabled() -> None:
    """Valida que el dashboard ejecutivo exija token cuando la auth esta activa."""

    settings = get_settings()
    original_enabled = settings.api_auth_enabled
    original_token = settings.api_auth_token
    settings.api_auth_enabled = True
    settings.api_auth_token = "token-prueba"

    try:
        app.dependency_overrides[get_executive_dashboard_service] = lambda: FakeExecutiveDashboardService()
        client = TestClient(app)

        response = client.get("/api/v1/dashboard/executive")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthorized"
    finally:
        settings.api_auth_enabled = original_enabled
        settings.api_auth_token = original_token
        app.dependency_overrides.clear()
