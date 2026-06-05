"""Endpoints HTTP del dominio tecnico."""

from dataclasses import asdict
from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_technical_query_service
from novitec_dwh.api.schemas.financial import PaginationMetadataResponse
from novitec_dwh.api.schemas.technical import (
    TechnicalEquipmentAccessListResponse,
    TechnicalEquipmentAccessResponse,
    TechnicalEquipmentListResponse,
    TechnicalEquipmentResponse,
    TechnicalReportListResponse,
    TechnicalReportPhotoListResponse,
    TechnicalReportPhotoResponse,
    TechnicalReportResponse,
    TechnicalSummaryResponse,
)
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.technical.application.services import TechnicalQueryService

router = APIRouter(
    prefix="/technical",
    tags=["technical"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/summary", response_model=TechnicalSummaryResponse, summary="Resumen tecnico")
def get_technical_summary(
    technician_name: str | None = Query(default=None),
    equipment_status: str | None = Query(default=None),
    service_name: str | None = Query(default=None),
    brand_name: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    service: TechnicalQueryService = Depends(get_technical_query_service),
) -> TechnicalSummaryResponse:
    """Devuelve el resumen principal del dominio tecnico."""

    summary = service.get_summary(
        technician_name=technician_name,
        equipment_status=equipment_status,
        service_name=service_name,
        brand_name=brand_name,
        date_from=date_from,
        date_to=date_to,
    )
    return TechnicalSummaryResponse(**asdict(summary))


@router.get("/reports", response_model=TechnicalReportListResponse, summary="Listado de informes tecnicos")
def list_technical_reports(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_id: int | None = Query(default=None, ge=1),
    technician_name: str | None = Query(default=None),
    equipment_status: str | None = Query(default=None),
    has_budget_json: bool | None = Query(default=None),
    is_equipment_operational: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="report_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: TechnicalQueryService = Depends(get_technical_query_service),
) -> dict:
    """Lista informes tecnicos con filtros opcionales."""

    result = service.list_reports(
        limit=limit,
        offset=offset,
        order_id=order_id,
        technician_name=technician_name,
        equipment_status=equipment_status,
        has_budget_json=has_budget_json,
        is_equipment_operational=is_equipment_operational,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [TechnicalReportResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/report-photos",
    response_model=TechnicalReportPhotoListResponse,
    summary="Listado de fotos de informes tecnicos",
)
def list_technical_report_photos(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    report_source_id: int | None = Query(default=None, ge=1),
    technician_name: str | None = Query(default=None),
    has_binary_evidence: bool | None = Query(default=None),
    mime_type: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="report_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: TechnicalQueryService = Depends(get_technical_query_service),
) -> dict:
    """Lista fotos de informes tecnicos con filtros opcionales."""

    result = service.list_report_photos(
        limit=limit,
        offset=offset,
        report_source_id=report_source_id,
        technician_name=technician_name,
        has_binary_evidence=has_binary_evidence,
        mime_type=mime_type,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [TechnicalReportPhotoResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get("/equipment", response_model=TechnicalEquipmentListResponse, summary="Listado de equipos tecnicos")
def list_technical_equipment(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service_name: str | None = Query(default=None),
    brand_name: str | None = Query(default=None),
    device_type_name: str | None = Query(default=None),
    inventory_product_code: str | None = Query(default=None),
    has_password_provided: bool | None = Query(default=None),
    has_failure_description: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="billing_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: TechnicalQueryService = Depends(get_technical_query_service),
) -> dict:
    """Lista equipos tecnicos con filtros opcionales."""

    result = service.list_equipment(
        limit=limit,
        offset=offset,
        service_name=service_name,
        brand_name=brand_name,
        device_type_name=device_type_name,
        inventory_product_code=inventory_product_code,
        has_password_provided=has_password_provided,
        has_failure_description=has_failure_description,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [TechnicalEquipmentResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/equipment-access",
    response_model=TechnicalEquipmentAccessListResponse,
    summary="Listado de accesos de equipos",
)
def list_technical_equipment_access(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    equipment_source_id: int | None = Query(default=None, ge=1),
    has_user_name: bool | None = Query(default=None),
    is_pattern: bool | None = Query(default=None),
    sort_by: str = Query(default="equipment_source_id"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: TechnicalQueryService = Depends(get_technical_query_service),
) -> dict:
    """Lista accesos de equipos con filtros opcionales."""

    result = service.list_equipment_access(
        limit=limit,
        offset=offset,
        equipment_source_id=equipment_source_id,
        has_user_name=has_user_name,
        is_pattern=is_pattern,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [TechnicalEquipmentAccessResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


def _build_paginated_response(total: int, limit: int, offset: int, items: list[dict]) -> dict:
    """Construye una respuesta paginada uniforme para los listados API."""

    total_pages = ceil(total / limit) if total > 0 else 0
    page = (offset // limit) + 1 if total > 0 else 0
    metadata = PaginationMetadataResponse(
        total=total,
        limit=limit,
        offset=offset,
        count=len(items),
        page=page,
        total_pages=total_pages,
        has_next=(offset + len(items)) < total,
        has_previous=offset > 0,
    )
    return {"meta": metadata.model_dump(), "items": items}
