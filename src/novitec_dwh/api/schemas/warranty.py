"""Esquemas Pydantic del dominio de garantias para FastAPI."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from novitec_dwh.api.schemas.financial import PaginationMetadataResponse


class WarrantySummaryResponse(BaseModel):
    """Representa el resumen principal del dominio de garantias."""

    extraction_id: str | None
    total_cas: int
    cas_activos: int
    total_ordenes_personales: int
    ordenes_personales_con_caso: int
    ordenes_personales_cerradas: int
    total_ordenes_empresariales: int
    ordenes_empresariales_con_ticket: int
    ordenes_empresariales_con_horas: int
    total_asignaciones_usuario_cas: int


class WarrantyServiceCenterResponse(BaseModel):
    """Representa un CAS expuesto por API."""

    source_id: int
    service_center_name: str
    prefix_code: str | None
    brand_name: str | None
    phone_number: str | None
    email: str | None
    city_name: str | None
    contact_name: str | None
    is_active: bool


class WarrantyPersonalOrderResponse(BaseModel):
    """Representa una orden personal de garantia expuesta por API."""

    extraction_id: str
    source_id: int
    order_number: str | None
    order_status: str
    warranty_status: str
    warranty_type: str
    service_center_name: str
    opened_date: date | None
    promised_date: date | None
    shipped_date: date | None
    returned_date: date | None
    delivered_date: date | None
    finalized_date: date | None
    technician_id: int | None
    branch_id: int
    client_id: int
    equipment_id: int
    case_number: str | None
    cycle_days: int | None
    sla_days: int | None
    has_case_number: bool
    has_return_date: bool
    is_closed: bool


class WarrantyCompanyOrderResponse(BaseModel):
    """Representa una orden empresarial con CAS expuesta por API."""

    extraction_id: str
    source_id: int
    order_number: str
    order_status: str
    opened_date: date | None
    promised_date: date | None
    service_center_name: str | None
    technician_id: int | None
    branch_id: int
    company_id: int
    equipment_id: int | None
    ticket_number: str | None
    hourly_rate: Decimal | None
    worked_hours: Decimal | None
    estimated_revenue: Decimal | None
    cycle_days: int | None
    sla_days: int | None
    has_ticket_number: bool
    has_worked_hours: bool


class WarrantyUserAssignmentResponse(BaseModel):
    """Representa una asignacion usuario CAS expuesta por API."""

    extraction_id: str
    source_id: int
    user_id: int
    user_login: str | None
    user_name: str | None
    service_center_id: int
    service_center_name: str | None


class WarrantyServiceCenterListResponse(BaseModel):
    """Envuelve el listado paginado de CAS."""

    meta: PaginationMetadataResponse
    items: list[WarrantyServiceCenterResponse]


class WarrantyPersonalOrderListResponse(BaseModel):
    """Envuelve el listado paginado de ordenes personales de garantia."""

    meta: PaginationMetadataResponse
    items: list[WarrantyPersonalOrderResponse]


class WarrantyCompanyOrderListResponse(BaseModel):
    """Envuelve el listado paginado de ordenes empresariales con CAS."""

    meta: PaginationMetadataResponse
    items: list[WarrantyCompanyOrderResponse]


class WarrantyUserAssignmentListResponse(BaseModel):
    """Envuelve el listado paginado de asignaciones usuario CAS."""

    meta: PaginationMetadataResponse
    items: list[WarrantyUserAssignmentResponse]
