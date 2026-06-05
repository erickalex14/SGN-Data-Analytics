"""DTOs de consulta del dominio de inventario."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Generic, TypeVar

ItemType = TypeVar("ItemType")


@dataclass(slots=True)
class InventorySummary:
    """Resume los principales indicadores del dominio de inventario."""

    extraction_id: str | None
    total_repuestos: int
    repuestos_con_stock: int
    stock_total_unidades: int
    costo_total_inventario: Decimal
    total_consumos_orden: int
    cantidad_total_consumida: int
    total_solicitudes_repuesto: int
    solicitudes_aprobadas: int
    solicitudes_rechazadas: int
    solicitudes_pendientes: int
    total_listas_compra: int


@dataclass(slots=True)
class InventorySparePartListItem:
    """Representa un registro consultable del hecho principal de repuestos."""

    extraction_id: str
    source_id: int
    spare_part_code: str
    part_number: str | None
    spare_part_name: str
    created_date: date | None
    updated_date: date | None
    current_stock: int
    current_cost: Decimal
    warehouse_number: int
    has_stock: bool
    has_part_number: bool


@dataclass(slots=True)
class InventoryOrderSparePartListItem:
    """Representa un registro consultable de consumo de repuestos por orden."""

    extraction_id: str
    source_id: int
    order_id: int
    spare_part_code: str
    spare_part_name: str
    movement_date: date | None
    installer_user_id: int | None
    quantity: int
    has_installer_user: bool


@dataclass(slots=True)
class InventorySparePartRequestListItem:
    """Representa un registro consultable de solicitudes de repuesto."""

    extraction_id: str
    source_id: int
    request_number: str
    order_id: int
    technician_name: str
    spare_part_code: str | None
    spare_part_name: str | None
    request_date: date
    management_date: date | None
    approved_by: str | None
    request_status: str
    quantity: int
    is_approved: bool
    is_rejected: bool
    is_pending: bool
    has_purchase_link: bool


@dataclass(slots=True)
class InventoryPurchaseListListItem:
    """Representa un registro consultable de listas de compra."""

    extraction_id: str
    source_id: int
    list_number: str
    creator_user_id: int | None
    creation_date: date
    created_date: date
    list_status: str
    has_observation: bool


@dataclass(slots=True)
class PaginatedInventoryResult(Generic[ItemType]):
    """Envuelve resultados paginados para listados API del dominio de inventario."""

    total: int
    limit: int
    offset: int
    items: list[ItemType]
