"""Contratos de lectura del dominio organizacional."""

from typing import Protocol

from novitec_dwh.contexts.organizational.application.dto_query import (
    OrganizationalGroupPermissionListItem,
    OrganizationalSummary,
    OrganizationalUserBranchListItem,
    OrganizationalUserListItem,
    OrganizationalUserPermissionListItem,
    PaginatedOrganizationalResult,
)


class OrganizationalQueryRepository(Protocol):
    """Define las consultas de solo lectura sobre el mart organizacional."""

    def get_summary(
        self,
        branch_city: str | None = None,
        role_name: str | None = None,
        access_group_name: str | None = None,
        is_active: bool | None = None,
        can_access_nc: bool | None = None,
    ) -> OrganizationalSummary:
        """Obtiene los indicadores principales del dominio organizacional."""

    def list_users(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        role_name: str | None = None,
        branch_city: str | None = None,
        access_group_name: str | None = None,
        is_active: bool | None = None,
        can_access_nc: bool | None = None,
        has_email: bool | None = None,
        has_phone: bool | None = None,
        sort_by: str = "user_name",
        sort_dir: str = "asc",
    ) -> PaginatedOrganizationalResult[OrganizationalUserListItem]:
        """Lista usuarios con filtros opcionales."""

    def list_user_branches(
        self,
        limit: int,
        offset: int,
        user_id: int | None = None,
        user_login: str | None = None,
        branch_id: int | None = None,
        branch_city: str | None = None,
        sort_by: str = "user_name",
        sort_dir: str = "asc",
    ) -> PaginatedOrganizationalResult[OrganizationalUserBranchListItem]:
        """Lista asignaciones usuario-sucursal con filtros opcionales."""

    def list_group_permissions(
        self,
        limit: int,
        offset: int,
        group_name: str | None = None,
        module_name: str | None = None,
        action_name: str | None = None,
        is_allowed: bool | None = None,
        is_superadmin: bool | None = None,
        sort_by: str = "group_name",
        sort_dir: str = "asc",
    ) -> PaginatedOrganizationalResult[OrganizationalGroupPermissionListItem]:
        """Lista permisos de grupo con filtros opcionales."""

    def list_user_permissions(
        self,
        limit: int,
        offset: int,
        user_id: int | None = None,
        user_login: str | None = None,
        module_name: str | None = None,
        action_name: str | None = None,
        is_allowed: bool | None = None,
        sort_by: str = "created_date",
        sort_dir: str = "desc",
    ) -> PaginatedOrganizationalResult[OrganizationalUserPermissionListItem]:
        """Lista permisos de usuario con filtros opcionales."""
