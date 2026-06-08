"""DTOs de consulta del dominio organizacional."""

from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar

ItemType = TypeVar("ItemType")


@dataclass(slots=True)
class OrganizationalSummary:
    """Resume los indicadores principales del dominio organizacional."""

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


@dataclass(slots=True)
class OrganizationalUserListItem:
    """Representa un usuario interno consultable por API."""

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


@dataclass(slots=True)
class OrganizationalUserBranchListItem:
    """Representa una asignacion de usuario a sucursal."""

    extraction_id: str
    source_id: int
    user_id: int
    user_login: str | None
    user_name: str | None
    branch_id: int
    branch_number: int | None
    city_name: str | None
    sequential_code: str | None


@dataclass(slots=True)
class OrganizationalGroupPermissionListItem:
    """Representa un permiso asignado a un grupo de acceso."""

    extraction_id: str
    source_id: int
    group_id: int
    group_name: str | None
    module_name: str
    action_name: str
    is_allowed: bool
    is_superadmin: bool | None


@dataclass(slots=True)
class OrganizationalUserPermissionListItem:
    """Representa un permiso asignado a un usuario."""

    extraction_id: str
    source_id: int
    created_date: date | None
    user_id: int
    user_login: str | None
    user_name: str | None
    module_name: str
    action_name: str
    is_allowed: bool


@dataclass(slots=True)
class PaginatedOrganizationalResult(Generic[ItemType]):
    """Envuelve resultados paginados del dominio organizacional."""

    total: int
    limit: int
    offset: int
    items: list[ItemType]
