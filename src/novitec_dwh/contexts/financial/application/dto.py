"""DTOs del contexto financiero."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar

ItemType = TypeVar("ItemType")

@dataclass(slots=True)
class FinancialExtractionSummary:
    """Resume el volumen procesado durante una extraccion."""

    extraction_id: str
    started_at: datetime
    finished_at: datetime | None = None
    solicitudes_nc: int = 0
    solicitudes_nc_chunks: int = 0
    precios_orden: int = 0
    precios_orden_chunks: int = 0
    notificaciones: int = 0
    notificaciones_chunks: int = 0
    output_directory: str | None = None
    manifest_path: str | None = None


@dataclass(slots=True)
class FinancialStagingLoadSummary:
    """Resume el resultado de la carga del dominio financiero a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    solicitudes_nc: int = 0
    solicitudes_nc_chunks: int = 0
    precios_orden: int = 0
    precios_orden_chunks: int = 0
    notificaciones: int = 0
    notificaciones_chunks: int = 0


@dataclass(slots=True)
class FinancialMartLoadSummary:
    """Resume el resultado de la carga del mart financiero."""

    extraction_id: str
    staging_schema: str
    mart_schema: str
    started_at: datetime
    finished_at: datetime | None = None
    solicitudes_nc: int = 0
    precios_orden: int = 0
    notificaciones: int = 0
    reglas_calidad_ejecutadas: int = 0
    hallazgos_calidad: int = 0


@dataclass(slots=True)
class FinancialSummary:
    """Resume los principales indicadores del dominio financiero."""

    extraction_id: str | None
    total_solicitudes_nc: int
    solicitudes_aprobadas: int
    solicitudes_rechazadas: int
    solicitudes_pendientes: int
    total_registros_ingreso: int
    monto_total_ingresos: Decimal
    total_notificaciones: int
    total_notificaciones_leidas: int


@dataclass(slots=True)
class CreditNoteRequestListItem:
    """Representa un registro consultable del hecho de solicitudes NC."""

    extraction_id: str
    request_number: str
    order_id: int
    order_number: str | None
    request_date: datetime
    status_name: str
    subject_name: str
    admin_name: str | None
    rejection_reason: str | None
    technician_name: str
    created_at: datetime | None


@dataclass(slots=True)
class OrderPriceListItem:
    """Representa un registro consultable del hecho de ingresos por orden."""

    extraction_id: str
    order_id: int
    order_number: str | None
    service_name: str
    standard_service_name: str | None
    amount: Decimal
    standard_amount: Decimal | None
    created_at: datetime | None


@dataclass(slots=True)
class NotificationListItem:
    """Representa un registro consultable del hecho de notificaciones."""

    extraction_id: str
    order_id: int | None
    order_number: str | None
    nc_id: int | None
    notification_type: str
    is_read: bool
    technician_name: str
    created_at: datetime


@dataclass(slots=True)
class PaginatedResult(Generic[ItemType]):
    """Envuelve resultados paginados para listados API."""

    total: int
    limit: int
    offset: int
    items: list[ItemType]
