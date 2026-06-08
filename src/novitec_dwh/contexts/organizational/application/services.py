"""Servicios de aplicacion del dominio organizacional."""

import logging

from novitec_dwh.contexts.organizational.application.dto_query import (
    OrganizationalGroupPermissionListItem,
    OrganizationalSummary,
    OrganizationalUserBranchListItem,
    OrganizationalUserListItem,
    OrganizationalUserPermissionListItem,
    PaginatedOrganizationalResult,
)
from novitec_dwh.contexts.organizational.application.query_contracts import (
    OrganizationalQueryRepository,
)

logger = logging.getLogger("novitec_dwh.organizational.service")


class OrganizationalQueryService:
    """Orquesta las lecturas del dominio organizacional para la API."""

    def __init__(self, repository: OrganizationalQueryRepository) -> None:
        """Recibe el repositorio de consultas del mart organizacional."""

        self._repository = repository

    def get_summary(
        self,
        branch_city: str | None = None,
        role_name: str | None = None,
        access_group_name: str | None = None,
        is_active: bool | None = None,
        can_access_nc: bool | None = None,
    ) -> OrganizationalSummary:
        """Devuelve el resumen principal del dominio organizacional."""

        logger.info(
            "Consultando resumen organizacional | filtros=%s",
            self._build_filter_log(
                branch_city=branch_city,
                role_name=role_name,
                access_group_name=access_group_name,
                is_active=is_active,
                can_access_nc=can_access_nc,
            ),
        )
        result = self._repository.get_summary(
            branch_city=branch_city,
            role_name=role_name,
            access_group_name=access_group_name,
            is_active=is_active,
            can_access_nc=can_access_nc,
        )
        logger.info(
            "Resumen organizacional generado | usuarios=%s | asignaciones=%s | permisos_grupo=%s | permisos_usuario=%s",
            result.total_usuarios,
            result.total_asignaciones_sucursal,
            result.total_permisos_grupo,
            result.total_permisos_usuario,
        )
        return result

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
        """Devuelve usuarios paginados y filtrables."""

        logger.info(
            "Consultando usuarios organizacionales | filtros=%s",
            self._build_filter_log(
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
            ),
        )
        result = self._repository.list_users(
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
        logger.info(
            "Usuarios organizacionales consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve asignaciones usuario-sucursal paginadas y filtrables."""

        logger.info(
            "Consultando asignaciones usuario-sucursal | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                user_id=user_id,
                user_login=user_login,
                branch_id=branch_id,
                branch_city=branch_city,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_user_branches(
            limit=limit,
            offset=offset,
            user_id=user_id,
            user_login=user_login,
            branch_id=branch_id,
            branch_city=branch_city,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Asignaciones usuario-sucursal consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve permisos de grupo paginados y filtrables."""

        logger.info(
            "Consultando permisos de grupo | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                group_name=group_name,
                module_name=module_name,
                action_name=action_name,
                is_allowed=is_allowed,
                is_superadmin=is_superadmin,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_group_permissions(
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
        logger.info(
            "Permisos de grupo consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve permisos de usuario paginados y filtrables."""

        logger.info(
            "Consultando permisos de usuario | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                user_id=user_id,
                user_login=user_login,
                module_name=module_name,
                action_name=action_name,
                is_allowed=is_allowed,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_user_permissions(
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
        logger.info(
            "Permisos de usuario consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
