"""Esquemas Pydantic del dominio organizacional para FastAPI."""

from datetime import date

from pydantic import BaseModel

from novitec_dwh.api.schemas.financial import PaginationMetadataResponse


class OrganizationalSummaryResponse(BaseModel):
    """Representa el resumen principal del dominio organizacional."""

    extraction_id: str | None
    total_usuarios: int
    usuarios_activos: int
    usuarios_con_correo: int
    usuarios_con_telefono: int
    usuarios_con_acceso_nc: int
    usuarios_con_grupo_acceso: int
    total_asignaciones_sucursal: int
    total_permisos_grupo: int
    permisos_grupo_permitidos: int
    total_permisos_usuario: int
    permisos_usuario_permitidos: int


class OrganizationalUserResponse(BaseModel):
    """Representa un usuario interno expuesto por API."""

    extraction_id: str
    source_id: int
    user_login: str
    user_name: str
    role_name: str | None
    city_name: str | None
    access_group_name: str | None
    has_phone: bool
    has_email: bool
    can_access_nc: bool
    is_active: bool
    has_access_group: bool


class OrganizationalUserBranchResponse(BaseModel):
    """Representa una asignacion usuario-sucursal expuesta por API."""

    extraction_id: str
    source_id: int
    user_id: int
    user_login: str | None
    user_name: str | None
    branch_id: int
    branch_number: int | None
    city_name: str | None
    sequential_code: str | None


class OrganizationalGroupPermissionResponse(BaseModel):
    """Representa un permiso de grupo expuesto por API."""

    extraction_id: str
    source_id: int
    group_id: int
    group_name: str | None
    module_name: str
    action_name: str
    is_allowed: bool
    is_superadmin: bool | None


class OrganizationalUserPermissionResponse(BaseModel):
    """Representa un permiso de usuario expuesto por API."""

    extraction_id: str
    source_id: int
    created_date: date | None
    user_id: int
    user_login: str | None
    user_name: str | None
    module_name: str
    action_name: str
    is_allowed: bool


class OrganizationalUserListResponse(BaseModel):
    """Envuelve el listado paginado de usuarios."""

    meta: PaginationMetadataResponse
    items: list[OrganizationalUserResponse]


class OrganizationalUserBranchListResponse(BaseModel):
    """Envuelve el listado paginado de asignaciones usuario-sucursal."""

    meta: PaginationMetadataResponse
    items: list[OrganizationalUserBranchResponse]


class OrganizationalGroupPermissionListResponse(BaseModel):
    """Envuelve el listado paginado de permisos de grupo."""

    meta: PaginationMetadataResponse
    items: list[OrganizationalGroupPermissionResponse]


class OrganizationalUserPermissionListResponse(BaseModel):
    """Envuelve el listado paginado de permisos de usuario."""

    meta: PaginationMetadataResponse
    items: list[OrganizationalUserPermissionResponse]
