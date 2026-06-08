"""Endpoints HTTP del dominio de garantias."""

from dataclasses import asdict
from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_warranty_query_service
from novitec_dwh.api.schemas.financial import PaginationMetadataResponse
from novitec_dwh.api.schemas.warranty import (
    WarrantyCompanyOrderListResponse,
    WarrantyCompanyOrderResponse,
    WarrantyPersonalOrderListResponse,
    WarrantyPersonalOrderResponse,
    WarrantyServiceCenterListResponse,
    WarrantyServiceCenterResponse,
    WarrantySummaryResponse,
    WarrantyUserAssignmentListResponse,
    WarrantyUserAssignmentResponse,
)
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.warranty.application.services import WarrantyQueryService

router = APIRouter(
    prefix="/warranty",
    tags=["warranty"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/summary", response_model=WarrantySummaryResponse, summary="Resumen de garantias")
def get_warranty_summary(
    service_center_name: str | None = Query(default=None),
    technician_id: int | None = Query(default=None, ge=1),
    user_id: int | None = Query(default=None, ge=1),
    warranty_status: str | None = Query(default=None),
    warranty_type: str | None = Query(default=None),
    order_status: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    service: WarrantyQueryService = Depends(get_warranty_query_service),
) -> WarrantySummaryResponse:
    """Devuelve el resumen principal del dominio de garantias."""

    summary = service.get_summary(
        service_center_name=service_center_name,
        technician_id=technician_id,
        user_id=user_id,
        warranty_status=warranty_status,
        warranty_type=warranty_type,
        order_status=order_status,
        date_from=date_from,
        date_to=date_to,
    )
    return WarrantySummaryResponse(**asdict(summary))


@router.get("/service-centers", response_model=WarrantyServiceCenterListResponse, summary="Listado de CAS")
def list_warranty_service_centers(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    service_center_name: str | None = Query(default=None),
    prefix_code: str | None = Query(default=None),
    brand_name: str | None = Query(default=None),
    city_name: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    sort_by: str = Query(default="service_center_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: WarrantyQueryService = Depends(get_warranty_query_service),
) -> dict:
    """Lista centros autorizados de servicio con filtros opcionales."""

    result = service.list_service_centers(
        limit=limit,
        offset=offset,
        service_center_name=service_center_name,
        prefix_code=prefix_code,
        brand_name=brand_name,
        city_name=city_name,
        is_active=is_active,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [WarrantyServiceCenterResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/personal-orders",
    response_model=WarrantyPersonalOrderListResponse,
    summary="Listado de ordenes personales de garantia",
)
def list_warranty_personal_orders(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_number: str | None = Query(default=None),
    service_center_name: str | None = Query(default=None),
    technician_id: int | None = Query(default=None, ge=1),
    warranty_status: str | None = Query(default=None),
    warranty_type: str | None = Query(default=None),
    order_status: str | None = Query(default=None),
    has_case_number: bool | None = Query(default=None),
    is_closed: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="opened_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: WarrantyQueryService = Depends(get_warranty_query_service),
) -> dict:
    """Lista ordenes personales de garantia con filtros opcionales."""

    result = service.list_personal_orders(
        limit=limit,
        offset=offset,
        order_number=order_number,
        service_center_name=service_center_name,
        technician_id=technician_id,
        warranty_status=warranty_status,
        warranty_type=warranty_type,
        order_status=order_status,
        has_case_number=has_case_number,
        is_closed=is_closed,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [WarrantyPersonalOrderResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/company-orders",
    response_model=WarrantyCompanyOrderListResponse,
    summary="Listado de ordenes empresariales con CAS",
)
def list_warranty_company_orders(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_number: str | None = Query(default=None),
    service_center_name: str | None = Query(default=None),
    technician_id: int | None = Query(default=None, ge=1),
    company_id: int | None = Query(default=None, ge=1),
    order_status: str | None = Query(default=None),
    has_ticket_number: bool | None = Query(default=None),
    has_worked_hours: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="opened_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: WarrantyQueryService = Depends(get_warranty_query_service),
) -> dict:
    """Lista ordenes empresariales con CAS y filtros opcionales."""

    result = service.list_company_orders(
        limit=limit,
        offset=offset,
        order_number=order_number,
        service_center_name=service_center_name,
        technician_id=technician_id,
        company_id=company_id,
        order_status=order_status,
        has_ticket_number=has_ticket_number,
        has_worked_hours=has_worked_hours,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [WarrantyCompanyOrderResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/user-assignments",
    response_model=WarrantyUserAssignmentListResponse,
    summary="Listado de asignaciones usuario CAS",
)
def list_warranty_user_assignments(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: int | None = Query(default=None, ge=1),
    user_login: str | None = Query(default=None),
    user_name: str | None = Query(default=None),
    service_center_name: str | None = Query(default=None),
    sort_by: str = Query(default="user_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: WarrantyQueryService = Depends(get_warranty_query_service),
) -> dict:
    """Lista asignaciones entre usuarios internos y CAS."""

    result = service.list_user_assignments(
        limit=limit,
        offset=offset,
        user_id=user_id,
        user_login=user_login,
        user_name=user_name,
        service_center_name=service_center_name,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [WarrantyUserAssignmentResponse(**asdict(item)).model_dump() for item in result.items]
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
