"""Pruebas de endpoints de inventario de la API."""

from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_inventory_query_service
from novitec_dwh.api.main import app
from novitec_dwh.contexts.inventory.application.dto_query import (
    InventoryOrderSparePartListItem,
    InventoryPurchaseListListItem,
    InventorySparePartListItem,
    InventorySparePartRequestListItem,
    InventorySummary,
    PaginatedInventoryResult,
)


class FakeInventoryQueryService:
    """Doblez de servicio para probar los endpoints de inventario sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa contenedores simples para capturar filtros."""

        self.last_summary_filters: dict | None = None
        self.last_spare_part_filters: dict | None = None
        self.last_order_consumption_filters: dict | None = None
        self.last_request_filters: dict | None = None
        self.last_purchase_list_filters: dict | None = None

    def get_summary(self, **kwargs) -> InventorySummary:
        """Devuelve un resumen fijo de inventario para pruebas."""

        self.last_summary_filters = kwargs
        return InventorySummary(
            extraction_id="inventory_20260605_173536",
            total_repuestos=2086,
            repuestos_con_stock=1560,
            stock_total_unidades=4820,
            costo_total_inventario=Decimal("153240.50"),
            total_consumos_orden=16,
            cantidad_total_consumida=28,
            total_solicitudes_repuesto=12,
            solicitudes_aprobadas=5,
            solicitudes_rechazadas=1,
            solicitudes_pendientes=6,
            total_listas_compra=4,
        )

    def list_spare_parts(self, **kwargs) -> PaginatedInventoryResult[InventorySparePartListItem]:
        """Devuelve una pagina fija de repuestos."""

        self.last_spare_part_filters = kwargs
        return PaginatedInventoryResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                InventorySparePartListItem(
                    extraction_id="inventory_20260605_173536",
                    source_id=1,
                    spare_part_code="REP-001",
                    part_number="NP-001",
                    spare_part_name="Pantalla 15 pulgadas",
                    created_date=date(2026, 6, 5),
                    updated_date=date(2026, 6, 5),
                    current_stock=8,
                    current_cost=Decimal("45.50"),
                    warehouse_number=1,
                    has_stock=True,
                    has_part_number=True,
                )
            ],
        )

    def list_order_spare_parts(
        self,
        **kwargs,
    ) -> PaginatedInventoryResult[InventoryOrderSparePartListItem]:
        """Devuelve una pagina fija de consumos por orden."""

        self.last_order_consumption_filters = kwargs
        return PaginatedInventoryResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                InventoryOrderSparePartListItem(
                    extraction_id="inventory_20260605_173536",
                    source_id=1,
                    order_id=10,
                    spare_part_code="REP-001",
                    spare_part_name="Pantalla 15 pulgadas",
                    movement_date=date(2026, 6, 5),
                    installer_user_id=7,
                    quantity=2,
                    has_installer_user=True,
                )
            ],
        )

    def list_spare_part_requests(
        self,
        **kwargs,
    ) -> PaginatedInventoryResult[InventorySparePartRequestListItem]:
        """Devuelve una pagina fija de solicitudes de repuesto."""

        self.last_request_filters = kwargs
        return PaginatedInventoryResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                InventorySparePartRequestListItem(
                    extraction_id="inventory_20260605_173536",
                    source_id=1,
                    request_number="SR-001",
                    order_id=10,
                    technician_name="Tecnico 1",
                    spare_part_code="REP-001",
                    spare_part_name="Pantalla 15 pulgadas",
                    request_date=date(2026, 6, 5),
                    management_date=date(2026, 6, 6),
                    approved_by="Supervisor",
                    request_status="Aprobada",
                    quantity=2,
                    is_approved=True,
                    is_rejected=False,
                    is_pending=False,
                    has_purchase_link=True,
                )
            ],
        )

    def list_purchase_lists(
        self,
        **kwargs,
    ) -> PaginatedInventoryResult[InventoryPurchaseListListItem]:
        """Devuelve una pagina fija de listas de compra."""

        self.last_purchase_list_filters = kwargs
        return PaginatedInventoryResult(
            total=1,
            limit=kwargs.get("limit", 50),
            offset=kwargs.get("offset", 0),
            items=[
                InventoryPurchaseListListItem(
                    extraction_id="inventory_20260605_173536",
                    source_id=1,
                    list_number="LC-001",
                    creator_user_id=5,
                    creation_date=date(2026, 6, 5),
                    created_date=date(2026, 6, 5),
                    list_status="Pendiente",
                    has_observation=True,
                )
            ],
        )


def test_get_inventory_summary() -> None:
    """Valida la respuesta del endpoint de resumen de inventario."""

    app.dependency_overrides[get_inventory_query_service] = lambda: FakeInventoryQueryService()
    client = TestClient(app)

    response = client.get("/api/v1/inventory/summary")

    assert response.status_code == 200
    assert response.json()["total_repuestos"] == 2086

    app.dependency_overrides.clear()


def test_list_inventory_spare_parts_with_filters() -> None:
    """Valida filtros y respuesta del listado de repuestos."""

    fake_service = FakeInventoryQueryService()
    app.dependency_overrides[get_inventory_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/inventory/spare-parts",
        params={
            "limit": 20,
            "offset": 5,
            "spare_part_code": "REP",
            "part_number": "NP",
            "spare_part_name": "Pantalla",
            "warehouse_number": 1,
            "has_stock": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "current_stock",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["meta"]["limit"] == 20
    assert response.json()["items"][0]["spare_part_code"] == "REP-001"
    assert fake_service.last_spare_part_filters == {
        "limit": 20,
        "offset": 5,
        "spare_part_code": "REP",
        "part_number": "NP",
        "spare_part_name": "Pantalla",
        "warehouse_number": 1,
        "has_stock": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "current_stock",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_inventory_order_spare_parts_with_filters() -> None:
    """Valida filtros y respuesta del listado de consumos por orden."""

    fake_service = FakeInventoryQueryService()
    app.dependency_overrides[get_inventory_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/inventory/order-spare-parts",
        params={
            "limit": 10,
            "offset": 1,
            "order_id": 10,
            "spare_part_code": "REP",
            "spare_part_name": "Pantalla",
            "installer_user_id": 7,
            "has_installer_user": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "quantity",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["order_id"] == 10
    assert fake_service.last_order_consumption_filters == {
        "limit": 10,
        "offset": 1,
        "order_id": 10,
        "spare_part_code": "REP",
        "spare_part_name": "Pantalla",
        "installer_user_id": 7,
        "has_installer_user": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "quantity",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_inventory_spare_part_requests_with_filters() -> None:
    """Valida filtros y respuesta del listado de solicitudes de repuesto."""

    fake_service = FakeInventoryQueryService()
    app.dependency_overrides[get_inventory_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/inventory/spare-part-requests",
        params={
            "limit": 10,
            "offset": 2,
            "request_number": "SR",
            "order_id": 10,
            "technician_name": "Tecnico",
            "spare_part_code": "REP",
            "request_status": "Aprobada",
            "approved_by": "Supervisor",
            "has_purchase_link": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "quantity",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["request_number"] == "SR-001"
    assert fake_service.last_request_filters == {
        "limit": 10,
        "offset": 2,
        "request_number": "SR",
        "order_id": 10,
        "technician_name": "Tecnico",
        "spare_part_code": "REP",
        "request_status": "Aprobada",
        "approved_by": "Supervisor",
        "has_purchase_link": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "quantity",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()


def test_list_inventory_purchase_lists_with_filters() -> None:
    """Valida filtros y respuesta del listado de listas de compra."""

    fake_service = FakeInventoryQueryService()
    app.dependency_overrides[get_inventory_query_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/inventory/purchase-lists",
        params={
            "limit": 12,
            "offset": 3,
            "list_number": "LC",
            "creator_user_id": 5,
            "list_status": "Pendiente",
            "has_observation": "true",
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "sort_by": "list_number",
            "sort_dir": "asc",
        },
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["list_number"] == "LC-001"
    assert fake_service.last_purchase_list_filters == {
        "limit": 12,
        "offset": 3,
        "list_number": "LC",
        "creator_user_id": 5,
        "list_status": "Pendiente",
        "has_observation": True,
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "sort_by": "list_number",
        "sort_dir": "asc",
    }

    app.dependency_overrides.clear()
