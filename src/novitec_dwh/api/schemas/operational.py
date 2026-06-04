"""Esquemas Pydantic del dominio operativo para FastAPI."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from novitec_dwh.api.schemas.financial import PaginationMetadataResponse


class OperationalSummaryResponse(BaseModel):
    """Representa el resumen principal del dominio operativo."""

    extraction_id: str | None
    total_ordenes: int
    ordenes_abiertas: int
    ordenes_entregadas: int
    ordenes_con_garantia: int
    total_preordenes: int
    total_asignaciones_tecnicos: int
    promedio_dias_ciclo: Decimal | None


class OperationalOrderResponse(BaseModel):
    """Representa una orden operativa expuesta por API."""

    extraction_id: str
    source_order_id: int
    order_type: str
    order_number: str
    intake_date: date | None
    promised_date: date | None
    delivery_date: date | None
    order_status: str | None
    intake_reason: str | None
    customer_type: str
    customer_name: str | None
    technician_name: str | None
    branch_name: str | None
    cycle_days: int | None
    delay_days: int | None
    worked_hours: Decimal | None
    hourly_rate: Decimal | None
    is_open: bool
    is_delivered: bool
    is_warranty: bool


class OperationalPreorderResponse(BaseModel):
    """Representa una preorden operativa expuesta por API."""

    extraction_id: str
    source_id: int
    linked_order_id: int | None
    preorder_number: str
    registration_date: date | None
    preorder_status: str | None
    customer_name: str | None
    branch_name: str | None
    city_name: str | None
    has_invoice: bool
    has_photos: bool


class OperationalAssignmentResponse(BaseModel):
    """Representa una asignacion tecnico-orden expuesta por API."""

    extraction_id: str
    source_id: int
    source_order_id: int
    technician_name: str
    assignment_count: int


class OperationalOrderListResponse(BaseModel):
    """Envuelve el listado paginado de ordenes operativas."""

    meta: PaginationMetadataResponse
    items: list[OperationalOrderResponse]


class OperationalPreorderListResponse(BaseModel):
    """Envuelve el listado paginado de preordenes operativas."""

    meta: PaginationMetadataResponse
    items: list[OperationalPreorderResponse]


class OperationalAssignmentListResponse(BaseModel):
    """Envuelve el listado paginado de asignaciones tecnico-orden."""

    meta: PaginationMetadataResponse
    items: list[OperationalAssignmentResponse]
