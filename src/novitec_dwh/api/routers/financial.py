"""Endpoints HTTP del dominio financiero."""

from dataclasses import asdict
from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_financial_query_service
from novitec_dwh.api.schemas.financial import (
    CreditNoteRequestResponse,
    CreditNoteRequestListResponse,
    FinancialSummaryResponse,
    NotificationListResponse,
    NotificationResponse,
    OrderPriceListResponse,
    OrderPriceResponse,
    PaginationMetadataResponse,
)
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.financial.application.services import FinancialQueryService

router = APIRouter(
    prefix="/financial",
    tags=["financial"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/summary", response_model=FinancialSummaryResponse, summary="Resumen financiero")
def get_financial_summary(
    order_id: int | None = Query(default=None, ge=1),
    order_number: str | None = Query(default=None),
    technician_name: str | None = Query(default=None),
    admin_name: str | None = Query(default=None),
    status_name: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    service: FinancialQueryService = Depends(get_financial_query_service),
) -> FinancialSummaryResponse:
    """Devuelve el resumen principal del dominio financiero."""

    summary = service.get_summary(
        order_id=order_id,
        order_number=order_number,
        technician_name=technician_name,
        admin_name=admin_name,
        status_name=status_name,
        date_from=date_from,
        date_to=date_to,
    )
    return FinancialSummaryResponse(**asdict(summary))


@router.get(
    "/credit-note-requests",
    response_model=CreditNoteRequestListResponse,
    summary="Listado de solicitudes de nota de credito",
)
def list_credit_note_requests(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None),
    request_number: str | None = Query(default=None),
    order_id: int | None = Query(default=None, ge=1),
    order_number: str | None = Query(default=None),
    status_name: str | None = Query(default=None),
    technician_name: str | None = Query(default=None),
    admin_name: str | None = Query(default=None),
    subject_name: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="request_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: FinancialQueryService = Depends(get_financial_query_service),
) -> dict:
    """Lista solicitudes de nota de credito con filtros opcionales."""

    result = service.list_credit_note_requests(
        limit=limit,
        offset=offset,
        search=search,
        request_number=request_number,
        order_id=order_id,
        order_number=order_number,
        status_name=status_name,
        technician_name=technician_name,
        admin_name=admin_name,
        subject_name=subject_name,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [CreditNoteRequestResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(
        total=result.total,
        limit=result.limit,
        offset=result.offset,
        items=items,
    )


@router.get(
    "/order-prices",
    response_model=OrderPriceListResponse,
    summary="Listado de ingresos por orden",
)
def list_order_prices(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_id: int | None = Query(default=None, ge=1),
    service_name: str | None = Query(default=None),
    order_number: str | None = Query(default=None),
    standard_service_name: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: FinancialQueryService = Depends(get_financial_query_service),
) -> dict:
    """Lista ingresos por orden con filtros opcionales."""

    result = service.list_order_prices(
        limit=limit,
        offset=offset,
        order_id=order_id,
        service_name=service_name,
        order_number=order_number,
        standard_service_name=standard_service_name,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [OrderPriceResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(
        total=result.total,
        limit=result.limit,
        offset=result.offset,
        items=items,
    )


@router.get(
    "/notifications",
    response_model=NotificationListResponse,
    summary="Listado de notificaciones financieras",
)
def list_notifications(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_id: int | None = Query(default=None, ge=1),
    order_number: str | None = Query(default=None),
    nc_id: int | None = Query(default=None, ge=1),
    notification_type: str | None = Query(default=None),
    is_read: bool | None = Query(default=None),
    technician_name: str | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: FinancialQueryService = Depends(get_financial_query_service),
) -> dict:
    """Lista notificaciones financieras con filtros opcionales."""

    result = service.list_notifications(
        limit=limit,
        offset=offset,
        order_id=order_id,
        order_number=order_number,
        nc_id=nc_id,
        notification_type=notification_type,
        is_read=is_read,
        technician_name=technician_name,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [NotificationResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(
        total=result.total,
        limit=result.limit,
        offset=result.offset,
        items=items,
    )


def _build_paginated_response(
    total: int,
    limit: int,
    offset: int,
    items: list[dict],
) -> dict:
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
    return {
        "meta": metadata.model_dump(),
        "items": items,
    }
