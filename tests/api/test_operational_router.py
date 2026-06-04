"""Pruebas de endpoints operativos de la API."""

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_operational_query_service
from novitec_dwh.api.main import app
from novitec_dwh.contexts.operational.application.dto_query import (
    OperationalAssignmentListItem,
    OperationalOrderListItem,
    OperationalPreorderListItem,
    OperationalSummary,
    PaginatedOperationalResult,
)


class FakeOperationalQueryService:
    """Doblez de servicio para probar los endpoints operativos sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa contenedores simples para capturar filtros."""

        self.last_summary_filters: dict | None = None
        self.last_order_filters: dict | None = None
        self.last_preorder_filters: dict | None = None
        self.last_assignment_filters: dict | None = None

    def get_summary(self, **kwargs) -> OperationalSummary:
        """Devuelve un resumen operativo fijo para pruebas."""

        self.last_summary_filters = kwargs
        return OperationalSummary(
            extraction_id="operational_20260604_202615",
            total_ordenes=1500,
            ordenes_abiertas=700,
            ordenes_entregadas=650,
            ordenes_con_garantia=120,
            total_preordenes=60,
            total_asignaciones_tecnicos=12,
            promedio_dias_ciclo=Decimal("4.50"),
        )

    def list_orders(self, **kwargs) -> PaginatedOperationalResult[OperationalOrderListItem]:
        """Devuelve una pagina fija de ordenes operativas."""

        self.last_order_filters = kwargs
        return PaginatedOperationalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OperationalOrderListItem(
                    extraction_id="operational_20260604_202615",
                    source_order_id=1,
                    order_type="personal",
                    order_number="ORD-001",
                    intake_date=date(2026, 6, 4),
                    promised_date=date(2026, 6, 6),
                    delivery_date=None,
                    order_status="Pendiente",
                    intake_reason="Servicio Tecnico",
                    customer_type="B2C",
                    customer_name="Cliente Demo",
                    technician_name="Tecnico 1",
                    branch_name="Quito",
                    cycle_days=None,
                    delay_days=None,
                    worked_hours=None,
                    hourly_rate=None,
                    is_open=True,
                    is_delivered=False,
                    is_warranty=False,
                )
            ],
        )

    def list_preorders(self, **kwargs) -> PaginatedOperationalResult[OperationalPreorderListItem]:
        """Devuelve una pagina fija de preordenes."""

        self.last_preorder_filters = kwargs
        return PaginatedOperationalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OperationalPreorderListItem(
                    extraction_id="operational_20260604_202615",
                    source_id=1,
                    linked_order_id=None,
                    preorder_number="PRE-001",
                    registration_date=date(2026, 6, 4),
                    preorder_status="pendiente",
                    customer_name="Ana Perez",
                    branch_name="Quito",
                    city_name="Quito",
                    has_invoice=False,
                    has_photos=False,
                )
            ],
        )

    def list_company_order_assignments(
        self,
        **kwargs,
    ) -> PaginatedOperationalResult[OperationalAssignmentListItem]:
        """Devuelve una pagina fija de asignaciones tecnico-orden."""

        self.last_assignment_filters = kwargs
        return PaginatedOperationalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                OperationalAssignmentListItem(
                    extraction_id="operational_20260604_202615",
                    source_id=1,
                    source_order_id=2,
                    technician_name="Tecnico 1",
                    assignment_count=1,
                )
            ],
        )


def test_get_operational_summary() -> None:
    """Valida la respuesta del endpoint de resumen operativo."""

    app.dependency_overrides[get_operational_query_service] = lambda: FakeOperationalQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/operational/summary")

    assert response.status_code == 200
    assert response.json()["total_ordenes"] == 1500

    app.dependency_overrides.clear()


def test_list_operational_orders_with_filters() -> None:
    """Valida filtros y respuesta del listado de ordenes operativas."""

    fake_service = FakeOperationalQueryService()
    app.dependency_overrides[get_operational_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/operational/orders",
        params={
            "limit": 20,
            "offset": 5,
            "search": "ORD",
            "order_type": "personal",
            "status_name": "Pendiente",
            "technician_name": "Tecnico",
            "branch_name": "Quito",
            "customer_type": "B2C",
            "is_open": "true",
            "is_warranty": "false",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "order_number",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["limit"] == 20
    assert response.json()["items"][0]["order_number"] == "ORD-001"
    assert fake_service.last_order_filters == {
        "limit": 20,
        "offset": 5,
        "search": "ORD",
        "order_type": "personal",
        "status_name": "Pendiente",
        "technician_name": "Tecnico",
        "branch_name": "Quito",
        "customer_type": "B2C",
        "is_open": True,
        "is_warranty": False,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "order_number",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_operational_preorders_with_filters() -> None:
    """Valida filtros y respuesta del listado de preordenes."""

    fake_service = FakeOperationalQueryService()
    app.dependency_overrides[get_operational_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/operational/preorders",
        params={
            "limit": 10,
            "offset": 2,
            "preorder_status": "pendiente",
            "branch_name": "Quito",
            "has_invoice": "false",
            "has_photos": "false",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "preorder_number",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["offset"] == 2
    assert response.json()["items"][0]["preorder_number"] == "PRE-001"
    assert fake_service.last_preorder_filters == {
        "limit": 10,
        "offset": 2,
        "preorder_status": "pendiente",
        "branch_name": "Quito",
        "has_invoice": False,
        "has_photos": False,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "preorder_number",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_operational_assignments_with_filters() -> None:
    """Valida filtros y respuesta del listado de asignaciones."""

    fake_service = FakeOperationalQueryService()
    app.dependency_overrides[get_operational_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/operational/company-order-assignments",
        params={
            "limit": 15,
            "offset": 1,
            "source_order_id": 2,
            "technician_name": "Tecnico 1",
            "sort_by": "technician_name",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["has_previous"] is True
    assert response.json()["items"][0]["source_order_id"] == 2
    assert fake_service.last_assignment_filters == {
        "limit": 15,
        "offset": 1,
        "source_order_id": 2,
        "technician_name": "Tecnico 1",
        "sort_by": "technician_name",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()
