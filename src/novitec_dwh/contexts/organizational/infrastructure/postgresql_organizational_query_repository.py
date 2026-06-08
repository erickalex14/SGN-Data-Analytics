"""Repositorio PostgreSQL de consultas sobre el mart organizacional."""

import logging

from psycopg.rows import dict_row

from novitec_dwh.contexts.organizational.application.dto_query import (
    OrganizationalGroupPermissionListItem,
    OrganizationalSummary,
    OrganizationalUserBranchListItem,
    OrganizationalUserListItem,
    OrganizationalUserPermissionListItem,
    PaginatedOrganizationalResult,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger("novitec_dwh.organizational.repository")


class PostgreSQLOrganizationalQueryRepository:
    """Consulta el mart organizacional para exponer datos por API."""

    _USER_SORT_FIELDS = {
        "user_name": "usr.user_name",
        "user_login": "usr.user_login",
        "role_name": "rol.role_name",
        "branch_city": "suc.city_name",
        "access_group_name": "grp.group_name",
    }
    _USER_BRANCH_SORT_FIELDS = {
        "user_name": "usr.user_name",
        "user_login": "usr.user_login",
        "branch_number": "suc.branch_number",
        "branch_city": "suc.city_name",
    }
    _GROUP_PERMISSION_SORT_FIELDS = {
        "group_name": "grp.group_name",
        "module_name": "fact.module_name",
        "action_name": "fact.action_name",
    }
    _USER_PERMISSION_SORT_FIELDS = {
        "created_date": "created_date.full_date",
        "user_name": "usr.user_name",
        "user_login": "usr.user_login",
        "module_name": "fact.module_name",
        "action_name": "fact.action_name",
    }

    def __init__(self, connection_factory: PostgreSQLConnectionFactory, mart_schema: str) -> None:
        """Recibe la fabrica de conexiones y el schema del mart."""

        self._connection_factory = connection_factory
        self._mart_schema = mart_schema

    def get_summary(
        self,
        branch_city: str | None = None,
        role_name: str | None = None,
        access_group_name: str | None = None,
        is_active: bool | None = None,
        can_access_nc: bool | None = None,
    ) -> OrganizationalSummary:
        """Obtiene el resumen principal del dominio organizacional."""

        logger.info("Ejecutando consulta de resumen organizacional | schema=%s", self._mart_schema)

        user_filters: list[str] = []
        user_params: list[object] = []
        group_permission_filters: list[str] = []
        group_permission_params: list[object] = []
        user_permission_filters: list[str] = []
        user_permission_params: list[object] = []
        branch_assignment_filters: list[str] = []
        branch_assignment_params: list[object] = []

        if branch_city:
            user_filters.append("suc.city_name ILIKE %s")
            user_params.append(f"%{branch_city}%")
            branch_assignment_filters.append("suc.city_name ILIKE %s")
            branch_assignment_params.append(f"%{branch_city}%")
        if role_name:
            user_filters.append("rol.role_name ILIKE %s")
            user_params.append(f"%{role_name}%")
        if access_group_name:
            user_filters.append("grp.group_name ILIKE %s")
            user_params.append(f"%{access_group_name}%")
            group_permission_filters.append("grp.group_name ILIKE %s")
            group_permission_params.append(f"%{access_group_name}%")
        if is_active is not None:
            user_filters.append("fact.is_active = %s")
            user_params.append(is_active)
        if can_access_nc is not None:
            user_filters.append("fact.can_access_nc = %s")
            user_params.append(can_access_nc)

        user_where_sql = f"WHERE {' AND '.join(user_filters)}" if user_filters else ""
        group_permission_where_sql = (
            f"WHERE {' AND '.join(group_permission_filters)}" if group_permission_filters else ""
        )
        user_permission_where_sql = (
            f"WHERE {' AND '.join(user_permission_filters)}" if user_permission_filters else ""
        )
        branch_assignment_where_sql = (
            f"WHERE {' AND '.join(branch_assignment_filters)}" if branch_assignment_filters else ""
        )

        query = f"""
            WITH latest_extraction AS (
                SELECT MAX(extraction_id) AS extraction_id
                FROM {self._mart_schema}.fact_organizational_users
            ),
            user_summary AS (
                SELECT
                    COUNT(*) AS total_usuarios,
                    COALESCE(SUM(CASE WHEN fact.is_active THEN 1 ELSE 0 END), 0) AS usuarios_activos,
                    COALESCE(SUM(CASE WHEN fact.has_email THEN 1 ELSE 0 END), 0) AS usuarios_con_correo,
                    COALESCE(SUM(CASE WHEN fact.has_phone THEN 1 ELSE 0 END), 0) AS usuarios_con_telefono,
                    COALESCE(SUM(CASE WHEN fact.can_access_nc THEN 1 ELSE 0 END), 0) AS usuarios_con_acceso_nc,
                    COALESCE(SUM(CASE WHEN fact.has_access_group THEN 1 ELSE 0 END), 0) AS usuarios_con_grupo_acceso
                FROM {self._mart_schema}.fact_organizational_users fact
                INNER JOIN {self._mart_schema}.dim_organizational_user usr
                    ON usr.user_key = fact.user_key
                LEFT JOIN {self._mart_schema}.dim_organizational_role rol
                    ON rol.role_key = fact.role_key
                LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                    ON suc.branch_key = fact.branch_key
                LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                    ON grp.access_group_key = fact.access_group_key
                {user_where_sql}
            ),
            branch_summary AS (
                SELECT COUNT(*) AS total_asignaciones_sucursal
                FROM {self._mart_schema}.fact_organizational_user_branches fact
                LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                    ON suc.branch_key = fact.branch_key
                {branch_assignment_where_sql}
            ),
            group_permission_summary AS (
                SELECT
                    COUNT(*) AS total_permisos_grupo,
                    COALESCE(SUM(CASE WHEN fact.is_allowed THEN 1 ELSE 0 END), 0) AS permisos_grupo_permitidos
                FROM {self._mart_schema}.fact_organizational_group_permissions fact
                LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                    ON grp.access_group_key = fact.access_group_key
                {group_permission_where_sql}
            ),
            user_permission_summary AS (
                SELECT
                    COUNT(*) AS total_permisos_usuario,
                    COALESCE(SUM(CASE WHEN fact.is_allowed THEN 1 ELSE 0 END), 0) AS permisos_usuario_permitidos
                FROM {self._mart_schema}.fact_organizational_user_permissions fact
                {user_permission_where_sql}
            )
            SELECT
                latest_extraction.extraction_id,
                user_summary.total_usuarios,
                user_summary.usuarios_activos,
                user_summary.usuarios_con_correo,
                user_summary.usuarios_con_telefono,
                user_summary.usuarios_con_acceso_nc,
                user_summary.usuarios_con_grupo_acceso,
                branch_summary.total_asignaciones_sucursal,
                group_permission_summary.total_permisos_grupo,
                group_permission_summary.permisos_grupo_permitidos,
                user_permission_summary.total_permisos_usuario,
                user_permission_summary.permisos_usuario_permitidos
            FROM latest_extraction
            CROSS JOIN user_summary
            CROSS JOIN branch_summary
            CROSS JOIN group_permission_summary
            CROSS JOIN user_permission_summary
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    query,
                    [
                        *user_params,
                        *branch_assignment_params,
                        *group_permission_params,
                        *user_permission_params,
                    ],
                )
                row = cursor.fetchone()

        return OrganizationalSummary(
            extraction_id=row["extraction_id"],
            total_usuarios=int(row["total_usuarios"]),
            usuarios_activos=int(row["usuarios_activos"]),
            usuarios_con_correo=int(row["usuarios_con_correo"]),
            usuarios_con_telefono=int(row["usuarios_con_telefono"]),
            usuarios_con_acceso_nc=int(row["usuarios_con_acceso_nc"]),
            usuarios_con_grupo_acceso=int(row["usuarios_con_grupo_acceso"]),
            total_asignaciones_sucursal=int(row["total_asignaciones_sucursal"]),
            total_permisos_grupo=int(row["total_permisos_grupo"]),
            permisos_grupo_permitidos=int(row["permisos_grupo_permitidos"]),
            total_permisos_usuario=int(row["total_permisos_usuario"]),
            permisos_usuario_permitidos=int(row["permisos_usuario_permitidos"]),
        )

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

        filters: list[str] = []
        params: list[object] = []

        if search:
            filters.append("(usr.user_login ILIKE %s OR usr.user_name ILIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])
        if role_name:
            filters.append("rol.role_name ILIKE %s")
            params.append(f"%{role_name}%")
        if branch_city:
            filters.append("suc.city_name ILIKE %s")
            params.append(f"%{branch_city}%")
        if access_group_name:
            filters.append("grp.group_name ILIKE %s")
            params.append(f"%{access_group_name}%")
        if is_active is not None:
            filters.append("fact.is_active = %s")
            params.append(is_active)
        if can_access_nc is not None:
            filters.append("fact.can_access_nc = %s")
            params.append(can_access_nc)
        if has_email is not None:
            filters.append("fact.has_email = %s")
            params.append(has_email)
        if has_phone is not None:
            filters.append("fact.has_phone = %s")
            params.append(has_phone)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._USER_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="usr.user_name ASC, fact.source_id DESC",
        )
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_organizational_users fact
            INNER JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_organizational_role rol
                ON rol.role_key = fact.role_key
            LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                ON suc.branch_key = fact.branch_key
            LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                ON grp.access_group_key = fact.access_group_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                usr.user_login,
                usr.user_name,
                rol.role_name,
                suc.city_name,
                grp.group_name AS access_group_name,
                fact.has_phone,
                fact.has_email,
                fact.can_access_nc,
                fact.is_active,
                fact.has_access_group
            FROM {self._mart_schema}.fact_organizational_users fact
            INNER JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_organizational_role rol
                ON rol.role_key = fact.role_key
            LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                ON suc.branch_key = fact.branch_key
            LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                ON grp.access_group_key = fact.access_group_key
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
        """
        return self._fetch_paginated_items(
            count_query=count_query,
            data_query=data_query,
            params=params,
            limit=limit,
            offset=offset,
            item_builder=lambda row: OrganizationalUserListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                user_login=row["user_login"],
                user_name=row["user_name"],
                role_name=row["role_name"],
                city_name=row["city_name"],
                access_group_name=row["access_group_name"],
                has_phone=row["has_phone"],
                has_email=row["has_email"],
                can_access_nc=row["can_access_nc"],
                is_active=row["is_active"],
                has_access_group=row["has_access_group"],
            ),
        )

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

        filters: list[str] = []
        params: list[object] = []

        if user_id is not None:
            filters.append("fact.user_id = %s")
            params.append(user_id)
        if user_login:
            filters.append("usr.user_login ILIKE %s")
            params.append(f"%{user_login}%")
        if branch_id is not None:
            filters.append("fact.branch_id = %s")
            params.append(branch_id)
        if branch_city:
            filters.append("suc.city_name ILIKE %s")
            params.append(f"%{branch_city}%")

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._USER_BRANCH_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="usr.user_name ASC NULLS LAST, fact.source_id DESC",
        )
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_organizational_user_branches fact
            LEFT JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                ON suc.branch_key = fact.branch_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.user_id,
                usr.user_login,
                usr.user_name,
                fact.branch_id,
                suc.branch_number,
                suc.city_name,
                suc.sequential_code
            FROM {self._mart_schema}.fact_organizational_user_branches fact
            LEFT JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                ON suc.branch_key = fact.branch_key
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
        """
        return self._fetch_paginated_items(
            count_query=count_query,
            data_query=data_query,
            params=params,
            limit=limit,
            offset=offset,
            item_builder=lambda row: OrganizationalUserBranchListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                user_id=row["user_id"],
                user_login=row["user_login"],
                user_name=row["user_name"],
                branch_id=row["branch_id"],
                branch_number=row["branch_number"],
                city_name=row["city_name"],
                sequential_code=row["sequential_code"],
            ),
        )

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

        filters: list[str] = []
        params: list[object] = []

        if group_name:
            filters.append("grp.group_name ILIKE %s")
            params.append(f"%{group_name}%")
        if module_name:
            filters.append("fact.module_name ILIKE %s")
            params.append(f"%{module_name}%")
        if action_name:
            filters.append("fact.action_name ILIKE %s")
            params.append(f"%{action_name}%")
        if is_allowed is not None:
            filters.append("fact.is_allowed = %s")
            params.append(is_allowed)
        if is_superadmin is not None:
            filters.append("grp.is_superadmin = %s")
            params.append(is_superadmin)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._GROUP_PERMISSION_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="grp.group_name ASC NULLS LAST, fact.source_id DESC",
        )
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_organizational_group_permissions fact
            LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                ON grp.access_group_key = fact.access_group_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.group_id,
                grp.group_name,
                fact.module_name,
                fact.action_name,
                fact.is_allowed,
                grp.is_superadmin
            FROM {self._mart_schema}.fact_organizational_group_permissions fact
            LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                ON grp.access_group_key = fact.access_group_key
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
        """
        return self._fetch_paginated_items(
            count_query=count_query,
            data_query=data_query,
            params=params,
            limit=limit,
            offset=offset,
            item_builder=lambda row: OrganizationalGroupPermissionListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                group_id=row["group_id"],
                group_name=row["group_name"],
                module_name=row["module_name"],
                action_name=row["action_name"],
                is_allowed=row["is_allowed"],
                is_superadmin=row["is_superadmin"],
            ),
        )

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

        filters: list[str] = []
        params: list[object] = []

        if user_id is not None:
            filters.append("fact.user_id = %s")
            params.append(user_id)
        if user_login:
            filters.append("usr.user_login ILIKE %s")
            params.append(f"%{user_login}%")
        if module_name:
            filters.append("fact.module_name ILIKE %s")
            params.append(f"%{module_name}%")
        if action_name:
            filters.append("fact.action_name ILIKE %s")
            params.append(f"%{action_name}%")
        if is_allowed is not None:
            filters.append("fact.is_allowed = %s")
            params.append(is_allowed)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._USER_PERMISSION_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="created_date.full_date DESC NULLS LAST, fact.source_id DESC",
        )
        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_organizational_user_permissions fact
            LEFT JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_organizational_date created_date
                ON created_date.date_key = fact.created_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                created_date.full_date AS created_date,
                fact.user_id,
                usr.user_login,
                usr.user_name,
                fact.module_name,
                fact.action_name,
                fact.is_allowed
            FROM {self._mart_schema}.fact_organizational_user_permissions fact
            LEFT JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_organizational_date created_date
                ON created_date.date_key = fact.created_date_key
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
        """
        return self._fetch_paginated_items(
            count_query=count_query,
            data_query=data_query,
            params=params,
            limit=limit,
            offset=offset,
            item_builder=lambda row: OrganizationalUserPermissionListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                created_date=row["created_date"],
                user_id=row["user_id"],
                user_login=row["user_login"],
                user_name=row["user_name"],
                module_name=row["module_name"],
                action_name=row["action_name"],
                is_allowed=row["is_allowed"],
            ),
        )

    def _fetch_paginated_items(
        self,
        count_query: str,
        data_query: str,
        params: list[object],
        limit: int,
        offset: int,
        item_builder,
    ) -> PaginatedOrganizationalResult:
        """Ejecuta consulta paginada y mapea filas a DTOs."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(count_query, params)
                total = int(cursor.fetchone()["total"])
                cursor.execute(data_query, [*params, limit, offset])
                rows = cursor.fetchall()

        logger.info(
            "Consulta organizacional paginada completada | total=%s | devueltos=%s | limit=%s | offset=%s",
            total,
            len(rows),
            limit,
            offset,
        )
        return PaginatedOrganizationalResult(
            total=total,
            limit=limit,
            offset=offset,
            items=[item_builder(row) for row in rows],
        )

    def _build_order_by_sql(
        self,
        allowed_fields: dict[str, str],
        sort_by: str,
        sort_dir: str,
        fallback_expression: str,
    ) -> str:
        """Construye un ORDER BY seguro a partir de columnas permitidas."""

        column_expression = allowed_fields.get(sort_by)
        direction = "ASC" if sort_dir.lower() == "asc" else "DESC"
        if column_expression is None:
            return fallback_expression
        return f"{column_expression} {direction}"
