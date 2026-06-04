"""Esquemas Pydantic del dominio financiero para FastAPI."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class FinancialSummaryResponse(BaseModel):
    """Representa el resumen principal del dominio financiero."""

    extraction_id: str | None
    total_solicitudes_nc: int
    solicitudes_aprobadas: int
    solicitudes_rechazadas: int
    solicitudes_pendientes: int
    total_registros_ingreso: int
    monto_total_ingresos: Decimal
    total_notificaciones: int
    total_notificaciones_leidas: int


class CreditNoteRequestResponse(BaseModel):
    """Representa una solicitud de nota de credito expuesta por API."""

    extraction_id: str
    request_number: str
    order_id: int
    order_number: str | None
    request_date: date
    status_name: str
    subject_name: str
    admin_name: str | None
    rejection_reason: str | None
    technician_name: str
    created_at: datetime | None


class OrderPriceResponse(BaseModel):
    """Representa un registro de ingreso por orden expuesto por API."""

    extraction_id: str
    order_id: int
    order_number: str | None
    service_name: str
    standard_service_name: str | None
    amount: Decimal
    standard_amount: Decimal | None
    created_at: datetime | None


class NotificationResponse(BaseModel):
    """Representa una notificacion financiera expuesta por API."""

    extraction_id: str
    order_id: int | None
    order_number: str | None
    nc_id: int | None
    notification_type: str
    is_read: bool
    technician_name: str
    created_at: datetime


class PaginationMetadataResponse(BaseModel):
    """Expone metadatos uniformes de paginacion para listados API."""

    total: int
    limit: int
    offset: int
    count: int
    page: int
    total_pages: int
    has_next: bool
    has_previous: bool


class CreditNoteRequestListResponse(BaseModel):
    """Envuelve el listado paginado de solicitudes NC."""

    meta: PaginationMetadataResponse
    items: list[CreditNoteRequestResponse]


class OrderPriceListResponse(BaseModel):
    """Envuelve el listado paginado de ingresos por orden."""

    meta: PaginationMetadataResponse
    items: list[OrderPriceResponse]


class NotificationListResponse(BaseModel):
    """Envuelve el listado paginado de notificaciones."""

    meta: PaginationMetadataResponse
    items: list[NotificationResponse]
