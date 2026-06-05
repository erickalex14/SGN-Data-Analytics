"""Esquemas Pydantic del dominio tecnico para FastAPI."""

from datetime import date, datetime

from pydantic import BaseModel

from novitec_dwh.api.schemas.financial import PaginationMetadataResponse


class TechnicalSummaryResponse(BaseModel):
    """Representa el resumen principal del dominio tecnico."""

    extraction_id: str | None
    total_informes: int
    informes_equipo_operativo: int
    informes_con_presupuesto: int
    total_fotos_informes: int
    total_equipos: int
    equipos_con_contrasena: int
    total_accesos_equipos: int


class TechnicalReportResponse(BaseModel):
    """Representa un informe tecnico expuesto por API."""

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


class TechnicalReportPhotoResponse(BaseModel):
    """Representa una foto de informe expuesta por API."""

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


class TechnicalEquipmentResponse(BaseModel):
    """Representa un equipo tecnico expuesto por API."""

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


class TechnicalEquipmentAccessResponse(BaseModel):
    """Representa un acceso de equipo expuesto por API."""

    extraction_id: str
    source_id: int
    equipment_source_id: int
    has_user_name: bool
    is_pattern: bool
    access_count: int


class TechnicalReportListResponse(BaseModel):
    """Envuelve el listado paginado de informes tecnicos."""

    meta: PaginationMetadataResponse
    items: list[TechnicalReportResponse]


class TechnicalReportPhotoListResponse(BaseModel):
    """Envuelve el listado paginado de fotos de informes."""

    meta: PaginationMetadataResponse
    items: list[TechnicalReportPhotoResponse]


class TechnicalEquipmentListResponse(BaseModel):
    """Envuelve el listado paginado de equipos tecnicos."""

    meta: PaginationMetadataResponse
    items: list[TechnicalEquipmentResponse]


class TechnicalEquipmentAccessListResponse(BaseModel):
    """Envuelve el listado paginado de accesos de equipo."""

    meta: PaginationMetadataResponse
    items: list[TechnicalEquipmentAccessResponse]
