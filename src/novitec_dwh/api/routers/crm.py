"""Endpoints HTTP del dominio CRM."""

from dataclasses import asdict
from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_crm_query_service
from novitec_dwh.api.schemas.crm import (
    CrmCompanyListResponse,
    CrmCompanyResponse,
    CrmCustomerBranchListResponse,
    CrmCustomerBranchResponse,
    CrmCustomerListResponse,
    CrmCustomerResponse,
    CrmSummaryResponse,
)
from novitec_dwh.api.schemas.financial import PaginationMetadataResponse
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.crm.application.services import CrmQueryService

router = APIRouter(
    prefix="/crm",
    tags=["crm"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/summary", response_model=CrmSummaryResponse, summary="Resumen CRM")
def get_crm_summary(
    search: str | None = Query(default=None),
    province: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    service: CrmQueryService = Depends(get_crm_query_service),
) -> CrmSummaryResponse:
    """Devuelve el resumen principal del dominio CRM."""

    summary = service.get_summary(
        search=search,
        province=province,
        is_active=is_active,
        date_from=date_from,
        date_to=date_to,
    )
    return CrmSummaryResponse(**asdict(summary))


@router.get("/customers", response_model=CrmCustomerListResponse, summary="Listado de clientes")
def list_crm_customers(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None),
    identification: str | None = Query(default=None),
    has_email: bool | None = Query(default=None),
    has_address: bool | None = Query(default=None),
    sort_by: str = Query(default="full_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: CrmQueryService = Depends(get_crm_query_service),
) -> dict:
    """Lista clientes con filtros opcionales."""

    result = service.list_customers(
        limit=limit,
        offset=offset,
        search=search,
        identification=identification,
        has_email=has_email,
        has_address=has_address,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [CrmCustomerResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get("/companies", response_model=CrmCompanyListResponse, summary="Listado de empresas")
def list_crm_companies(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None),
    ruc: str | None = Query(default=None),
    has_email: bool | None = Query(default=None),
    has_phone: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="company_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: CrmQueryService = Depends(get_crm_query_service),
) -> dict:
    """Lista empresas con filtros opcionales."""

    result = service.list_companies(
        limit=limit,
        offset=offset,
        search=search,
        ruc=ruc,
        has_email=has_email,
        has_phone=has_phone,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [CrmCompanyResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/customer-branches",
    response_model=CrmCustomerBranchListResponse,
    summary="Listado de sucursales cliente",
)
def list_crm_customer_branches(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    branch_code: str | None = Query(default=None),
    branch_name: str | None = Query(default=None),
    province: str | None = Query(default=None),
    novitec_branch_name: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    sort_by: str = Query(default="branch_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: CrmQueryService = Depends(get_crm_query_service),
) -> dict:
    """Lista sucursales cliente con filtros opcionales."""

    result = service.list_customer_branches(
        limit=limit,
        offset=offset,
        branch_code=branch_code,
        branch_name=branch_name,
        province=province,
        novitec_branch_name=novitec_branch_name,
        is_active=is_active,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [CrmCustomerBranchResponse(**asdict(item)).model_dump() for item in result.items]
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
