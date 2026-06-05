"""Contratos de lectura del dominio de inventario."""

from datetime import date
from typing import Protocol

from novitec_dwh.contexts.inventory.application.dto_query import (
    InventoryOrderSparePartListItem,
    InventoryPurchaseListListItem,
    InventorySparePartListItem,
    InventorySparePartRequestListItem,
    InventorySummary,
    PaginatedInventoryResult,
)


class InventoryQueryRepository(Protocol):
    """Define las consultas de solo lectura sobre el mart de inventario."""

    def get_summary(
        self,
        technician_name: str | None = None,
        spare_part_code: str | None = None,
        request_status: str | None = None,
        warehouse_number: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> InventorySummary:
        """Obtiene los indicadores principales del dominio de inventario."""

    def list_spare_parts(
        self,
        limit: int,
        offset: int,
        spare_part_code: str | None = None,
        part_number: str | None = None,
        spare_part_name: str | None = None,
        warehouse_number: int | None = None,
        has_stock: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "updated_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventorySparePartListItem]:
        """Lista repuestos con filtros opcionales."""

    def list_order_spare_parts(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        spare_part_code: str | None = None,
        spare_part_name: str | None = None,
        installer_user_id: int | None = None,
        has_installer_user: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "movement_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventoryOrderSparePartListItem]:
        """Lista consumos de repuestos por orden con filtros opcionales."""

    def list_spare_part_requests(
        self,
        limit: int,
        offset: int,
        request_number: str | None = None,
        order_id: int | None = None,
        technician_name: str | None = None,
        spare_part_code: str | None = None,
        request_status: str | None = None,
        approved_by: str | None = None,
        has_purchase_link: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "request_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventorySparePartRequestListItem]:
        """Lista solicitudes de repuesto con filtros opcionales."""

    def list_purchase_lists(
        self,
        limit: int,
        offset: int,
        list_number: str | None = None,
        creator_user_id: int | None = None,
        list_status: str | None = None,
        has_observation: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "creation_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventoryPurchaseListListItem]:
        """Lista listas de compra con filtros opcionales."""
