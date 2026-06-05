"""Esquemas Pydantic del dominio de inventario para FastAPI."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from novitec_dwh.api.schemas.financial import PaginationMetadataResponse


class InventorySummaryResponse(BaseModel):
    """Representa el resumen principal del dominio de inventario."""

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


class InventorySparePartResponse(BaseModel):
    """Representa un repuesto expuesto por API."""

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


class InventoryOrderSparePartResponse(BaseModel):
    """Representa un consumo de repuesto por orden expuesto por API."""

    extraction_id: str
    source_id: int
    order_id: int
    spare_part_code: str
    spare_part_name: str
    movement_date: date | None
    installer_user_id: int | None
    quantity: int
    has_installer_user: bool


class InventorySparePartRequestResponse(BaseModel):
    """Representa una solicitud de repuesto expuesta por API."""

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


class InventoryPurchaseListResponse(BaseModel):
    """Representa una lista de compra expuesta por API."""

    extraction_id: str
    source_id: int
    list_number: str
    creator_user_id: int | None
    creation_date: date
    created_date: date
    list_status: str
    has_observation: bool


class InventorySparePartListResponse(BaseModel):
    """Envuelve el listado paginado de repuestos."""

    meta: PaginationMetadataResponse
    items: list[InventorySparePartResponse]


class InventoryOrderSparePartListResponse(BaseModel):
    """Envuelve el listado paginado de consumos de repuestos por orden."""

    meta: PaginationMetadataResponse
    items: list[InventoryOrderSparePartResponse]


class InventorySparePartRequestListResponse(BaseModel):
    """Envuelve el listado paginado de solicitudes de repuesto."""

    meta: PaginationMetadataResponse
    items: list[InventorySparePartRequestResponse]


class InventoryPurchaseListListResponse(BaseModel):
    """Envuelve el listado paginado de listas de compra."""

    meta: PaginationMetadataResponse
    items: list[InventoryPurchaseListResponse]
