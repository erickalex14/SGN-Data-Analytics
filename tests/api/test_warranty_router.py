"""Pruebas de endpoints de garantias de la API."""

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_warranty_query_service
from novitec_dwh.api.main import app
from novitec_dwh.contexts.warranty.application.dto_query import (
    PaginatedWarrantyResult,
    WarrantyCompanyOrderListItem,
    WarrantyPersonalOrderListItem,
    WarrantyServiceCenterListItem,
    WarrantySummary,
    WarrantyUserAssignmentListItem,
)


class FakeWarrantyQueryService:
    """Doblez de servicio para probar los endpoints de garantias sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa contenedores simples para capturar filtros."""

        self.last_summary_filters: dict | None = None
        self.last_service_center_filters: dict | None = None
        self.last_personal_order_filters: dict | None = None
        self.last_company_order_filters: dict | None = None
        self.last_assignment_filters: dict | None = None

    def get_summary(self, **kwargs) -> WarrantySummary:
        """Devuelve un resumen fijo de garantias para pruebas."""

        self.last_summary_filters = kwargs
        return WarrantySummary(
            extraction_id="warranty_20260608_150000",
            total_cas=12,
            cas_activos=10,
            total_ordenes_personales=85,
            ordenes_personales_con_caso=58,
            ordenes_personales_cerradas=49,
            total_ordenes_empresariales=19,
            ordenes_empresariales_con_ticket=14,
            ordenes_empresariales_con_horas=11,
            total_asignaciones_usuario_cas=9,
        )

    def list_service_centers(self, **kwargs) -> PaginatedWarrantyResult[WarrantyServiceCenterListItem]:
        """Devuelve una pagina fija de CAS."""

        self.last_service_center_filters = kwargs
        return PaginatedWarrantyResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                WarrantyServiceCenterListItem(
                    source_id=1,
                    service_center_name="CAS Samsung Quito",
                    prefix_code="SMS",
                    brand_name="Samsung",
                    phone_number="022000000",
                    email="cas@samsung.com",
                    city_name="Quito",
                    contact_name="Andrea",
                    is_active=True,
                )
            ],
        )

    def list_personal_orders(self, **kwargs) -> PaginatedWarrantyResult[WarrantyPersonalOrderListItem]:
        """Devuelve una pagina fija de ordenes personales."""

        self.last_personal_order_filters = kwargs
        return PaginatedWarrantyResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                WarrantyPersonalOrderListItem(
                    extraction_id="warranty_20260608_150000",
                    source_id=10,
                    order_number="ORD-100",
                    order_status="En garantia",
                    warranty_status="Enviada",
                    warranty_type="CAS",
                    service_center_name="CAS Samsung Quito",
                    opened_date=date(2026, 6, 1),
                    promised_date=date(2026, 6, 5),
                    shipped_date=date(2026, 6, 2),
                    returned_date=None,
                    delivered_date=None,
                    finalized_date=None,
                    technician_id=22,
                    branch_id=1,
                    client_id=15,
                    equipment_id=30,
                    case_number="CAS-7788",
                    cycle_days=4,
                    sla_days=5,
                    has_case_number=True,
                    has_return_date=False,
                    is_closed=False,
                )
            ],
        )

    def list_company_orders(self, **kwargs) -> PaginatedWarrantyResult[WarrantyCompanyOrderListItem]:
        """Devuelve una pagina fija de ordenes empresariales."""

        self.last_company_order_filters = kwargs
        return PaginatedWarrantyResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                WarrantyCompanyOrderListItem(
                    extraction_id="warranty_20260608_150000",
                    source_id=20,
                    order_number="OE-200",
                    order_status="Abierta",
                    opened_date=date(2026, 6, 3),
                    promised_date=date(2026, 6, 10),
                    service_center_name="CAS Lenovo Quito",
                    technician_id=33,
                    branch_id=2,
                    company_id=8,
                    equipment_id=44,
                    ticket_number="TK-001",
                    hourly_rate=Decimal("20.00"),
                    worked_hours=Decimal("2.50"),
                    estimated_revenue=Decimal("50.00"),
                    cycle_days=7,
                    sla_days=7,
                    has_ticket_number=True,
                    has_worked_hours=True,
                )
            ],
        )

    def list_user_assignments(self, **kwargs) -> PaginatedWarrantyResult[WarrantyUserAssignmentListItem]:
        """Devuelve una pagina fija de asignaciones usuario CAS."""

        self.last_assignment_filters = kwargs
        return PaginatedWarrantyResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                WarrantyUserAssignmentListItem(
                    extraction_id="warranty_20260608_150000",
                    source_id=5,
                    user_id=22,
                    user_login="aperez",
                    user_name="Andrea Perez",
                    service_center_id=1,
                    service_center_name="CAS Samsung Quito",
                )
            ],
        )


def test_get_warranty_summary() -> None:
    """Valida la respuesta del endpoint de resumen de garantias."""

    app.dependency_overrides[get_warranty_query_service] = lambda: FakeWarrantyQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/warranty/summary")

    assert response.status_code == 200
    assert response.json()["total_cas"] == 12

    app.dependency_overrides.clear()


def test_list_warranty_personal_orders_with_filters() -> None:
    """Valida filtros y respuesta del listado de ordenes personales de garantia."""

    fake_service = FakeWarrantyQueryService()
    app.dependency_overrides[get_warranty_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/warranty/personal-orders",
        params={
            "limit": 20,
            "offset": 5,
            "order_number": "ORD",
            "service_center_name": "Samsung",
            "technician_id": 22,
            "warranty_status": "Enviada",
            "warranty_type": "CAS",
            "order_status": "garantia",
            "has_case_number": "true",
            "is_closed": "false",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "cycle_days",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["order_number"] == "ORD-100"
    assert fake_service.last_personal_order_filters == {
        "limit": 20,
        "offset": 5,
        "order_number": "ORD",
        "service_center_name": "Samsung",
        "technician_id": 22,
        "warranty_status": "Enviada",
        "warranty_type": "CAS",
        "order_status": "garantia",
        "has_case_number": True,
        "is_closed": False,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "cycle_days",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_warranty_company_orders_with_filters() -> None:
    """Valida filtros y respuesta del listado de ordenes empresariales con CAS."""

    fake_service = FakeWarrantyQueryService()
    app.dependency_overrides[get_warranty_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/warranty/company-orders",
        params={
            "limit": 10,
            "offset": 2,
            "order_number": "OE",
            "service_center_name": "Lenovo",
            "technician_id": 33,
            "company_id": 8,
            "order_status": "Abierta",
            "has_ticket_number": "true",
            "has_worked_hours": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "estimated_revenue",
            "sort_dir": "desc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["order_number"] == "OE-200"
    assert fake_service.last_company_order_filters == {
        "limit": 10,
        "offset": 2,
        "order_number": "OE",
        "service_center_name": "Lenovo",
        "technician_id": 33,
        "company_id": 8,
        "order_status": "Abierta",
        "has_ticket_number": True,
        "has_worked_hours": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "estimated_revenue",
        "sort_dir": "desc",
    }

    app.dependency_overrides.clear()


def test_list_warranty_user_assignments_with_filters() -> None:
    """Valida filtros y respuesta del listado de asignaciones usuario CAS."""

    fake_service = FakeWarrantyQueryService()
    app.dependency_overrides[get_warranty_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/warranty/user-assignments",
        params={
            "limit": 12,
            "offset": 3,
            "user_id": 22,
            "user_login": "aperez",
            "user_name": "Andrea",
            "service_center_name": "Samsung",
            "sort_by": "service_center_name",
            "sort_dir": "desc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["user_login"] == "aperez"
    assert fake_service.last_assignment_filters == {
        "limit": 12,
        "offset": 3,
        "user_id": 22,
        "user_login": "aperez",
        "user_name": "Andrea",
        "service_center_name": "Samsung",
        "sort_by": "service_center_name",
        "sort_dir": "desc",
    }

    app.dependency_overrides.clear()
