"""Pruebas de endpoints CRM de la API."""

from datetime import date

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_crm_query_service
from novitec_dwh.api.main import app
from novitec_dwh.contexts.crm.application.dto_query import (
    CrmCompanyListItem,
    CrmCustomerBranchListItem,
    CrmCustomerListItem,
    CrmSummary,
    PaginatedCrmResult,
)


class FakeCrmQueryService:
    """Doblez de servicio para probar los endpoints CRM sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa contenedores simples para capturar filtros."""

        self.last_summary_filters: dict | None = None
        self.last_customer_filters: dict | None = None
        self.last_company_filters: dict | None = None
        self.last_branch_filters: dict | None = None

    def get_summary(self, **kwargs) -> CrmSummary:
        """Devuelve un resumen fijo de CRM para pruebas."""

        self.last_summary_filters = kwargs
        return CrmSummary(
            extraction_id="crm_20260605_140000",
            total_clientes=120,
            clientes_con_correo=85,
            clientes_con_direccion=97,
            clientes_con_contacto=118,
            total_empresas=24,
            empresas_con_correo=20,
            empresas_con_telefono=22,
            total_sucursalescliente=51,
            sucursalescliente_activas=46,
        )

    def list_customers(self, **kwargs) -> PaginatedCrmResult[CrmCustomerListItem]:
        """Devuelve una pagina fija de clientes."""

        self.last_customer_filters = kwargs
        return PaginatedCrmResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                CrmCustomerListItem(
                    extraction_id="crm_20260605_140000",
                    source_id=1,
                    full_name="Juan Perez",
                    first_name="Juan",
                    last_name="Perez",
                    identification="0102030405",
                    phone_number="0999999999",
                    email="juan@example.com",
                    address="Av. Principal",
                    has_email=True,
                    has_address=True,
                    has_phone=True,
                )
            ],
        )

    def list_companies(self, **kwargs) -> PaginatedCrmResult[CrmCompanyListItem]:
        """Devuelve una pagina fija de empresas."""

        self.last_company_filters = kwargs
        return PaginatedCrmResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                CrmCompanyListItem(
                    extraction_id="crm_20260605_140000",
                    source_id=1,
                    company_name="Empresa Uno",
                    ruc="1799999999001",
                    phone_number="022222222",
                    email="contacto@empresauno.com",
                    address="Centro Norte",
                    created_date=date(2026, 6, 5),
                    has_phone=True,
                    has_email=True,
                    has_address=True,
                )
            ],
        )

    def list_customer_branches(self, **kwargs) -> PaginatedCrmResult[CrmCustomerBranchListItem]:
        """Devuelve una pagina fija de sucursales cliente."""

        self.last_branch_filters = kwargs
        return PaginatedCrmResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                CrmCustomerBranchListItem(
                    extraction_id="crm_20260605_140000",
                    source_id=1,
                    created_date=date(2026, 6, 5),
                    branch_code="SC-001",
                    branch_number=1,
                    branch_name="Sucursal Matriz",
                    province="Pichincha",
                    novitec_branch_name="Quito",
                    is_active=True,
                )
            ],
        )


def test_get_crm_summary() -> None:
    """Valida la respuesta del endpoint de resumen CRM."""

    app.dependency_overrides[get_crm_query_service] = lambda: FakeCrmQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/crm/summary")

    assert response.status_code == 200
    assert response.json()["total_clientes"] == 120

    app.dependency_overrides.clear()


def test_list_crm_customers_with_filters() -> None:
    """Valida filtros y respuesta del listado de clientes."""

    fake_service = FakeCrmQueryService()
    app.dependency_overrides[get_crm_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/crm/customers",
        params={
            "limit": 20,
            "offset": 5,
            "search": "Juan",
            "identification": "0102",
            "has_email": "true",
            "has_address": "true",
            "sort_by": "identification",
            "sort_dir": "desc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["full_name"] == "Juan Perez"
    assert fake_service.last_customer_filters == {
        "limit": 20,
        "offset": 5,
        "search": "Juan",
        "identification": "0102",
        "has_email": True,
        "has_address": True,
        "sort_by": "identification",
        "sort_dir": "desc",
    }

    app.dependency_overrides.clear()


def test_list_crm_companies_with_filters() -> None:
    """Valida filtros y respuesta del listado de empresas."""

    fake_service = FakeCrmQueryService()
    app.dependency_overrides[get_crm_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/crm/companies",
        params={
            "limit": 10,
            "offset": 2,
            "search": "Empresa",
            "ruc": "1799",
            "has_email": "true",
            "has_phone": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "created_date",
            "sort_dir": "desc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["company_name"] == "Empresa Uno"
    assert fake_service.last_company_filters == {
        "limit": 10,
        "offset": 2,
        "search": "Empresa",
        "ruc": "1799",
        "has_email": True,
        "has_phone": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "created_date",
        "sort_dir": "desc",
    }

    app.dependency_overrides.clear()


def test_list_crm_customer_branches_with_filters() -> None:
    """Valida filtros y respuesta del listado de sucursales cliente."""

    fake_service = FakeCrmQueryService()
    app.dependency_overrides[get_crm_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/crm/customer-branches",
        params={
            "limit": 12,
            "offset": 3,
            "branch_code": "SC",
            "branch_name": "Matriz",
            "province": "Pichincha",
            "novitec_branch_name": "Quito",
            "is_active": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "branch_number",
            "sort_dir": "desc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["branch_code"] == "SC-001"
    assert fake_service.last_branch_filters == {
        "limit": 12,
        "offset": 3,
        "branch_code": "SC",
        "branch_name": "Matriz",
        "province": "Pichincha",
        "novitec_branch_name": "Quito",
        "is_active": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "branch_number",
        "sort_dir": "desc",
    }

    app.dependency_overrides.clear()
