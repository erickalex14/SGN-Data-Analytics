"""Endpoints HTTP del dominio de inventario."""

from dataclasses import asdict
from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_inventory_query_service
from novitec_dwh.api.schemas.financial import PaginationMetadataResponse
from novitec_dwh.api.schemas.inventory import (
    InventoryOrderSparePartListResponse,
    InventoryOrderSparePartResponse,
    InventoryPurchaseListListResponse,
    InventoryPurchaseListResponse,
    InventorySparePartListResponse,
    InventorySparePartRequestListResponse,
    InventorySparePartRequestResponse,
    InventorySparePartResponse,
    InventorySummaryResponse,
)
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.inventory.application.services import InventoryQueryService

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/summary", response_model=InventorySummaryResponse, summary="Resumen de inventario")
def get_inventory_summary(
    technician_name: str | None = Query(default=None),
    spare_part_code: str | None = Query(default=None),
    request_status: str | None = Query(default=None),
    warehouse_number: int | None = Query(default=None, ge=0),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    service: InventoryQueryService = Depends(get_inventory_query_service),
) -> InventorySummaryResponse:
    """Devuelve el resumen principal del dominio de inventario."""

    summary = service.get_summary(
        technician_name=technician_name,
        spare_part_code=spare_part_code,
        request_status=request_status,
        warehouse_number=warehouse_number,
        date_from=date_from,
        date_to=date_to,
    )
    return InventorySummaryResponse(**asdict(summary))


@router.get("/spare-parts", response_model=InventorySparePartListResponse, summary="Listado de repuestos")
def list_inventory_spare_parts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    spare_part_code: str | None = Query(default=None),
    part_number: str | None = Query(default=None),
    spare_part_name: str | None = Query(default=None),
    warehouse_number: int | None = Query(default=None, ge=0),
    has_stock: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="updated_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: InventoryQueryService = Depends(get_inventory_query_service),
) -> dict:
    """Lista repuestos con filtros opcionales."""

    result = service.list_spare_parts(
        limit=limit,
        offset=offset,
        spare_part_code=spare_part_code,
        part_number=part_number,
        spare_part_name=spare_part_name,
        warehouse_number=warehouse_number,
        has_stock=has_stock,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [InventorySparePartResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/order-spare-parts",
    response_model=InventoryOrderSparePartListResponse,
    summary="Listado de consumos de repuestos por orden",
)
def list_inventory_order_spare_parts(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    order_id: int | None = Query(default=None, ge=1),
    spare_part_code: str | None = Query(default=None),
    spare_part_name: str | None = Query(default=None),
    installer_user_id: int | None = Query(default=None, ge=1),
    has_installer_user: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="movement_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: InventoryQueryService = Depends(get_inventory_query_service),
) -> dict:
    """Lista consumos de repuestos por orden con filtros opcionales."""

    result = service.list_order_spare_parts(
        limit=limit,
        offset=offset,
        order_id=order_id,
        spare_part_code=spare_part_code,
        spare_part_name=spare_part_name,
        installer_user_id=installer_user_id,
        has_installer_user=has_installer_user,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [InventoryOrderSparePartResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/spare-part-requests",
    response_model=InventorySparePartRequestListResponse,
    summary="Listado de solicitudes de repuesto",
)
def list_inventory_spare_part_requests(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    request_number: str | None = Query(default=None),
    order_id: int | None = Query(default=None, ge=1),
    technician_name: str | None = Query(default=None),
    spare_part_code: str | None = Query(default=None),
    request_status: str | None = Query(default=None),
    approved_by: str | None = Query(default=None),
    has_purchase_link: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="request_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: InventoryQueryService = Depends(get_inventory_query_service),
) -> dict:
    """Lista solicitudes de repuesto con filtros opcionales."""

    result = service.list_spare_part_requests(
        limit=limit,
        offset=offset,
        request_number=request_number,
        order_id=order_id,
        technician_name=technician_name,
        spare_part_code=spare_part_code,
        request_status=request_status,
        approved_by=approved_by,
        has_purchase_link=has_purchase_link,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [InventorySparePartRequestResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/purchase-lists",
    response_model=InventoryPurchaseListListResponse,
    summary="Listado de listas de compra",
)
def list_inventory_purchase_lists(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    list_number: str | None = Query(default=None),
    creator_user_id: int | None = Query(default=None, ge=1),
    list_status: str | None = Query(default=None),
    has_observation: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="creation_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: InventoryQueryService = Depends(get_inventory_query_service),
) -> dict:
    """Lista listas de compra con filtros opcionales."""

    result = service.list_purchase_lists(
        limit=limit,
        offset=offset,
        list_number=list_number,
        creator_user_id=creator_user_id,
        list_status=list_status,
        has_observation=has_observation,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [InventoryPurchaseListResponse(**asdict(item)).model_dump() for item in result.items]
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
