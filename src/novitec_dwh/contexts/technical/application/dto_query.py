"""DTOs de consulta del dominio tecnico."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Generic, TypeVar

ItemType = TypeVar("ItemType")


@dataclass(slots=True)
class TechnicalSummary:
    """Resume los principales indicadores del dominio tecnico."""

    extraction_id: str | None
    total_informes: int
    informes_equipo_operativo: int
    informes_con_presupuesto: int
    total_fotos_informes: int
    total_equipos: int
    equipos_con_contrasena: int
    total_accesos_equipos: int


@dataclass(slots=True)
class TechnicalReportListItem:
    """Representa un registro consultable del hecho de informes tecnicos."""

    extraction_id: str
    source_id: int
    order_id: int
    report_date: date
    created_at: datetime | None
    technician_name: str
    equipment_status: str | None
    has_background: bool
    has_process: bool
    has_conclusion: bool
    has_recommendations: bool
    has_budget_json: bool
    is_equipment_operational: bool
    background_length: int | None
    process_length: int | None
    conclusion_length: int | None
    recommendation_length: int | None


@dataclass(slots=True)
class TechnicalReportPhotoListItem:
    """Representa un registro consultable del hecho de fotos de informes."""

    extraction_id: str
    source_id: int
    report_source_id: int
    report_date: date | None
    technician_name: str | None
    photo_order: int | None
    file_name: str | None
    mime_type: str | None
    caption: str | None
    has_binary_evidence: bool
    has_file_name: bool
    is_jpeg: bool


@dataclass(slots=True)
class TechnicalEquipmentListItem:
    """Representa un registro consultable del hecho de equipos tecnicos."""

    extraction_id: str
    source_id: int
    billing_date: date | None
    service_name: str | None
    brand_name: str | None
    device_type_name: str | None
    device_model: str | None
    serial_number: str | None
    inventory_product_code: str | None
    has_password_provided: bool
    has_failure_description: bool
    has_observation: bool
    has_billing_date: bool


@dataclass(slots=True)
class TechnicalEquipmentAccessListItem:
    """Representa un registro consultable del hecho de accesos de equipo."""

    extraction_id: str
    source_id: int
    equipment_source_id: int
    has_user_name: bool
    is_pattern: bool
    access_count: int


@dataclass(slots=True)
class PaginatedTechnicalResult(Generic[ItemType]):
    """Envuelve resultados paginados para listados API del dominio tecnico."""

    total: int
    limit: int
    offset: int
    items: list[ItemType]
