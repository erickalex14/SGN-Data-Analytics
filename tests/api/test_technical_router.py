"""Pruebas de endpoints tecnicos de la API."""

from datetime import date, datetime

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_technical_query_service
from novitec_dwh.api.main import app
from novitec_dwh.contexts.technical.application.dto_query import (
    PaginatedTechnicalResult,
    TechnicalEquipmentAccessListItem,
    TechnicalEquipmentListItem,
    TechnicalReportListItem,
    TechnicalReportPhotoListItem,
    TechnicalSummary,
)


class FakeTechnicalQueryService:
    """Doblez de servicio para probar los endpoints tecnicos sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa contenedores simples para capturar filtros."""

        self.last_summary_filters: dict | None = None
        self.last_report_filters: dict | None = None
        self.last_photo_filters: dict | None = None
        self.last_equipment_filters: dict | None = None
        self.last_access_filters: dict | None = None

    def get_summary(self, **kwargs) -> TechnicalSummary:
        """Devuelve un resumen tecnico fijo para pruebas."""

        self.last_summary_filters = kwargs
        return TechnicalSummary(
            extraction_id="technical_20260605_090000",
            total_informes=1170,
            informes_equipo_operativo=850,
            informes_con_presupuesto=430,
            total_fotos_informes=362,
            total_equipos=1643,
            equipos_con_contrasena=520,
            total_accesos_equipos=39,
        )

    def list_reports(self, **kwargs) -> PaginatedTechnicalResult[TechnicalReportListItem]:
        """Devuelve una pagina fija de informes tecnicos."""

        self.last_report_filters = kwargs
        return PaginatedTechnicalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                TechnicalReportListItem(
                    extraction_id="technical_20260605_090000",
                    source_id=1,
                    order_id=100,
                    report_date=date(2026, 6, 5),
                    created_at=datetime(2026, 6, 5, 9, 0, 0),
                    technician_name="Tecnico 5",
                    equipment_status="Operativo",
                    has_background=True,
                    has_process=True,
                    has_conclusion=True,
                    has_recommendations=True,
                    has_budget_json=True,
                    is_equipment_operational=True,
                    background_length=20,
                    process_length=30,
                    conclusion_length=25,
                    recommendation_length=15,
                )
            ],
        )

    def list_report_photos(self, **kwargs) -> PaginatedTechnicalResult[TechnicalReportPhotoListItem]:
        """Devuelve una pagina fija de fotos de informes."""

        self.last_photo_filters = kwargs
        return PaginatedTechnicalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                TechnicalReportPhotoListItem(
                    extraction_id="technical_20260605_090000",
                    source_id=1,
                    report_source_id=1,
                    report_date=date(2026, 6, 5),
                    technician_name="Tecnico 5",
                    photo_order=1,
                    file_name="foto.jpg",
                    mime_type="image/jpeg",
                    caption="Placa",
                    has_binary_evidence=True,
                    has_file_name=True,
                    is_jpeg=True,
                )
            ],
        )

    def list_equipment(self, **kwargs) -> PaginatedTechnicalResult[TechnicalEquipmentListItem]:
        """Devuelve una pagina fija de equipos tecnicos."""

        self.last_equipment_filters = kwargs
        return PaginatedTechnicalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                TechnicalEquipmentListItem(
                    extraction_id="technical_20260605_090000",
                    source_id=1,
                    billing_date=date(2026, 6, 1),
                    service_name="Revision",
                    brand_name="Dell",
                    device_type_name="Laptop",
                    device_model="Latitude",
                    serial_number="ABC123",
                    inventory_product_code="INV-001",
                    has_password_provided=True,
                    has_failure_description=True,
                    has_observation=True,
                    has_billing_date=True,
                )
            ],
        )

    def list_equipment_access(
        self,
        **kwargs,
    ) -> PaginatedTechnicalResult[TechnicalEquipmentAccessListItem]:
        """Devuelve una pagina fija de accesos de equipos."""

        self.last_access_filters = kwargs
        return PaginatedTechnicalResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                TechnicalEquipmentAccessListItem(
                    extraction_id="technical_20260605_090000",
                    source_id=1,
                    equipment_source_id=1,
                    has_user_name=True,
                    is_pattern=False,
                    access_count=1,
                )
            ],
        )


def test_get_technical_summary() -> None:
    """Valida la respuesta del endpoint de resumen tecnico."""

    app.dependency_overrides[get_technical_query_service] = lambda: FakeTechnicalQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/technical/summary")

    assert response.status_code == 200
    assert response.json()["total_informes"] == 1170

    app.dependency_overrides.clear()


def test_list_technical_reports_with_filters() -> None:
    """Valida filtros y respuesta del listado de informes tecnicos."""

    fake_service = FakeTechnicalQueryService()
    app.dependency_overrides[get_technical_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/technical/reports",
        params={
            "limit": 20,
            "offset": 5,
            "order_id": 100,
            "technician_name": "Tecnico",
            "equipment_status": "Operativo",
            "has_budget_json": "true",
            "is_equipment_operational": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "order_id",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["limit"] == 20
    assert response.json()["items"][0]["order_id"] == 100
    assert fake_service.last_report_filters == {
        "limit": 20,
        "offset": 5,
        "order_id": 100,
        "technician_name": "Tecnico",
        "equipment_status": "Operativo",
        "has_budget_json": True,
        "is_equipment_operational": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "order_id",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_technical_report_photos_with_filters() -> None:
    """Valida filtros y respuesta del listado de fotos de informes."""

    fake_service = FakeTechnicalQueryService()
    app.dependency_overrides[get_technical_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/technical/report-photos",
        params={
            "limit": 10,
            "offset": 2,
            "report_source_id": 1,
            "technician_name": "Tecnico 5",
            "has_binary_evidence": "true",
            "mime_type": "jpeg",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "photo_order",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["offset"] == 2
    assert response.json()["items"][0]["report_source_id"] == 1
    assert fake_service.last_photo_filters == {
        "limit": 10,
        "offset": 2,
        "report_source_id": 1,
        "technician_name": "Tecnico 5",
        "has_binary_evidence": True,
        "mime_type": "jpeg",
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "photo_order",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_technical_equipment_with_filters() -> None:
    """Valida filtros y respuesta del listado de equipos tecnicos."""

    fake_service = FakeTechnicalQueryService()
    app.dependency_overrides[get_technical_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/technical/equipment",
        params={
            "limit": 15,
            "offset": 3,
            "service_name": "Revision",
            "brand_name": "Dell",
            "device_type_name": "Laptop",
            "inventory_product_code": "INV",
            "has_password_provided": "true",
            "has_failure_description": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "device_model",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["has_previous"] is True
    assert response.json()["items"][0]["brand_name"] == "Dell"
    assert fake_service.last_equipment_filters == {
        "limit": 15,
        "offset": 3,
        "service_name": "Revision",
        "brand_name": "Dell",
        "device_type_name": "Laptop",
        "inventory_product_code": "INV",
        "has_password_provided": True,
        "has_failure_description": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "device_model",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_technical_equipment_access_with_filters() -> None:
    """Valida filtros y respuesta del listado de accesos de equipos."""

    fake_service = FakeTechnicalQueryService()
    app.dependency_overrides[get_technical_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/technical/equipment-access",
        params={
            "limit": 12,
            "offset": 1,
            "equipment_source_id": 1,
            "has_user_name": "true",
            "is_pattern": "false",
            "sort_by": "access_count",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["has_previous"] is True
    assert response.json()["items"][0]["equipment_source_id"] == 1
    assert fake_service.last_access_filters == {
        "limit": 12,
        "offset": 1,
        "equipment_source_id": 1,
        "has_user_name": True,
        "is_pattern": False,
        "sort_by": "access_count",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()
