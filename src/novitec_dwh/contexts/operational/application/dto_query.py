"""DTOs de consulta del dominio operativo."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Generic, TypeVar

ItemType = TypeVar("ItemType")


@dataclass(slots=True)
class OperationalSummary:
    """Resume los principales indicadores del dominio operativo."""

    extraction_id: str | None
    total_ordenes: int
    ordenes_abiertas: int
    ordenes_entregadas: int
    ordenes_con_garantia: int
    total_preordenes: int
    total_asignaciones_tecnicos: int
    promedio_dias_ciclo: Decimal | None


@dataclass(slots=True)
class OperationalOrderListItem:
    """Representa un registro consultable del hecho operativo de ordenes."""

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


@dataclass(slots=True)
class OperationalPreorderListItem:
    """Representa un registro consultable del hecho de preordenes."""

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


@dataclass(slots=True)
class OperationalAssignmentListItem:
    """Representa un registro consultable de asignaciones tecnico-orden."""

    extraction_id: str
    source_id: int
    source_order_id: int
    technician_name: str
    assignment_count: int


@dataclass(slots=True)
class PaginatedOperationalResult(Generic[ItemType]):
    """Envuelve resultados paginados para listados API del dominio operativo."""

    total: int
    limit: int
    offset: int
    items: list[ItemType]
