"""Endpoints HTTP del dominio organizacional."""

from dataclasses import asdict
from math import ceil

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_organizational_query_service
from novitec_dwh.api.schemas.financial import PaginationMetadataResponse
from novitec_dwh.api.schemas.organizational import (
    OrganizationalGroupPermissionListResponse,
    OrganizationalGroupPermissionResponse,
    OrganizationalSummaryResponse,
    OrganizationalUserBranchListResponse,
    OrganizationalUserBranchResponse,
    OrganizationalUserListResponse,
    OrganizationalUserPermissionListResponse,
    OrganizationalUserPermissionResponse,
    OrganizationalUserResponse,
)
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.organizational.application.services import (
    OrganizationalQueryService,
)

router = APIRouter(
    prefix="/organizational",
    tags=["organizational"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/summary", response_model=OrganizationalSummaryResponse, summary="Resumen organizacional")
def get_organizational_summary(
    branch_city: str | None = Query(default=None),
    role_name: str | None = Query(default=None),
    access_group_name: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    can_access_nc: bool | None = Query(default=None),
    service: OrganizationalQueryService = Depends(get_organizational_query_service),
) -> OrganizationalSummaryResponse:
    """Devuelve el resumen principal del dominio organizacional."""

    summary = service.get_summary(
        branch_city=branch_city,
        role_name=role_name,
        access_group_name=access_group_name,
        is_active=is_active,
        can_access_nc=can_access_nc,
    )
    return OrganizationalSummaryResponse(**asdict(summary))


@router.get("/users", response_model=OrganizationalUserListResponse, summary="Listado de usuarios")
def list_organizational_users(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    search: str | None = Query(default=None),
    role_name: str | None = Query(default=None),
    branch_city: str | None = Query(default=None),
    access_group_name: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    can_access_nc: bool | None = Query(default=None),
    has_email: bool | None = Query(default=None),
    has_phone: bool | None = Query(default=None),
    sort_by: str = Query(default="user_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: OrganizationalQueryService = Depends(get_organizational_query_service),
) -> dict:
    """Lista usuarios con filtros opcionales."""

    result = service.list_users(
        limit=limit,
        offset=offset,
        search=search,
        role_name=role_name,
        branch_city=branch_city,
        access_group_name=access_group_name,
        is_active=is_active,
        can_access_nc=can_access_nc,
        has_email=has_email,
        has_phone=has_phone,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [OrganizationalUserResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/user-branches",
    response_model=OrganizationalUserBranchListResponse,
    summary="Listado de asignaciones usuario-sucursal",
)
def list_organizational_user_branches(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: int | None = Query(default=None),
    user_login: str | None = Query(default=None),
    branch_id: int | None = Query(default=None),
    branch_city: str | None = Query(default=None),
    sort_by: str = Query(default="user_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: OrganizationalQueryService = Depends(get_organizational_query_service),
) -> dict:
    """Lista asignaciones usuario-sucursal con filtros opcionales."""

    result = service.list_user_branches(
        limit=limit,
        offset=offset,
        user_id=user_id,
        user_login=user_login,
        branch_id=branch_id,
        branch_city=branch_city,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [OrganizationalUserBranchResponse(**asdict(item)).model_dump() for item in result.items]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/group-permissions",
    response_model=OrganizationalGroupPermissionListResponse,
    summary="Listado de permisos de grupo",
)
def list_organizational_group_permissions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    group_name: str | None = Query(default=None),
    module_name: str | None = Query(default=None),
    action_name: str | None = Query(default=None),
    is_allowed: bool | None = Query(default=None),
    is_superadmin: bool | None = Query(default=None),
    sort_by: str = Query(default="group_name"),
    sort_dir: str = Query(default="asc", pattern="^(asc|desc)$"),
    service: OrganizationalQueryService = Depends(get_organizational_query_service),
) -> dict:
    """Lista permisos de grupo con filtros opcionales."""

    result = service.list_group_permissions(
        limit=limit,
        offset=offset,
        group_name=group_name,
        module_name=module_name,
        action_name=action_name,
        is_allowed=is_allowed,
        is_superadmin=is_superadmin,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [
        OrganizationalGroupPermissionResponse(**asdict(item)).model_dump()
        for item in result.items
    ]
    return _build_paginated_response(result.total, result.limit, result.offset, items)


@router.get(
    "/user-permissions",
    response_model=OrganizationalUserPermissionListResponse,
    summary="Listado de permisos de usuario",
)
def list_organizational_user_permissions(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    user_id: int | None = Query(default=None),
    user_login: str | None = Query(default=None),
    module_name: str | None = Query(default=None),
    action_name: str | None = Query(default=None),
    is_allowed: bool | None = Query(default=None),
    sort_by: str = Query(default="created_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    service: OrganizationalQueryService = Depends(get_organizational_query_service),
) -> dict:
    """Lista permisos de usuario con filtros opcionales."""

    result = service.list_user_permissions(
        limit=limit,
        offset=offset,
        user_id=user_id,
        user_login=user_login,
        module_name=module_name,
        action_name=action_name,
        is_allowed=is_allowed,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    items = [
        OrganizationalUserPermissionResponse(**asdict(item)).model_dump()
        for item in result.items
    ]
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
