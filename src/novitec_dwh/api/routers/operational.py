"""Endpoints HTTP del dominio operativo."""

from dataclasses import asdict
from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_operational_query_service
from novitec_dwh.api.schemas.financial import PaginationMetadataResponse
from novitec_dwh.api.schemas.operational import (
    OperationalAssignmentListResponse,
    OperationalAssignmentResponse,
    OperationalOrderListResponse,
    OperationalOrderResponse,
    OperationalPreorderListResponse,
    OperationalPreorderResponse,
    OperationalSummaryResponse,
)
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.operational.application.services import OperationalQueryService

router = APIRouter(
    prefix="/operational",
    tags=["operational"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/summary", response_model=OperationalSummaryResponse, summary="Resumen operativo")
def get_operational_summary(
    order_type: str | None = Query(default=None),
    technician_name: str | None = Query(default=None),
    branch_name: str | None = Query(default=None),
    status_name: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    service: OperationalQueryService = Depends(get_operational_query_service),
) -> OperationalSummaryResponse:
    """Devuelve el resumen principal del dominio operativo."""

    summary = service.get_summary(
        order_type=order_type,
        technician_name=technician_name,
        branch_name=branch_name,
        status_name=status_name,
        date_from=date_from,
        date_to=date_to,
    )
    return OperationalSummaryResponse(**asdict(summary))


@router.get("/orders", response_model=OperationalOrderListResponse, summary="Listado de ordenes operativas")
def list_operational_orders(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None),
    order_type: str | None = Query(default=None),
    status_name: str | None = Query(default=None),
    technician_name: str | None = Query(default=None),
    branch_name: str | None = Query(default=None),
    customer_type: str | None = Query(default=None),
    is_open: bool | None = Query(default=None),
    is_warranty: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="intake_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: OperationalQueryService = Depends(get_operational_query_service),
) -> dict:
    """Lista ordenes operativas con filtros opcionales."""

    result = service.list_orders(
        limit=limit,
        offset=offset,
        search=search,
        order_type=order_type,
        status_name=status_name,
        technician_name=technician_name,
        branch_name=branch_name,
        customer_type=customer_type,
        is_open=is_open,
        is_warranty=is_warranty,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [OperationalOrderResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get("/preorders", response_model=OperationalPreorderListResponse, summary="Listado de preordenes operativas")
def list_operational_preorders(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    preorder_status: str | None = Query(default=None),
    branch_name: str | None = Query(default=None),
    has_invoice: bool | None = Query(default=None),
    has_photos: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="registration_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: OperationalQueryService = Depends(get_operational_query_service),
) -> dict:
    """Lista preordenes operativas con filtros opcionales."""

    result = service.list_preorders(
        limit=limit,
        offset=offset,
        preorder_status=preorder_status,
        branch_name=branch_name,
        has_invoice=has_invoice,
        has_photos=has_photos,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [OperationalPreorderResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/company-order-assignments",
    response_model=OperationalAssignmentListResponse,
    summary="Listado de asignaciones tecnico-orden empresarial",
)
def list_company_order_assignments(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    source_order_id: int | None = Query(default=None, ge=1),
    technician_name: str | None = Query(default=None),
    sort_by: str = Query(default="source_order_id"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: OperationalQueryService = Depends(get_operational_query_service),
) -> dict:
    """Lista asignaciones tecnico-orden empresarial con filtros opcionales."""

    result = service.list_company_order_assignments(
        limit=limit,
        offset=offset,
        source_order_id=source_order_id,
        technician_name=technician_name,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [OperationalAssignmentResponse(**asdict(item)).model_dump() for item in result.items]
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
