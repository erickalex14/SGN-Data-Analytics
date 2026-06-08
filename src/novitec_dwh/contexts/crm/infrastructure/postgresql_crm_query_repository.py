"""Repositorio PostgreSQL de consultas sobre el mart CRM."""

import logging
from datetime import date

from psycopg.rows import dict_row

from novitec_dwh.contexts.crm.application.dto_query import (
    CrmCompanyListItem,
    CrmCustomerBranchListItem,
    CrmCustomerListItem,
    CrmSummary,
    PaginatedCrmResult,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger("novitec_dwh.crm.repository")


class PostgreSQLCrmQueryRepository:
    """Consulta el mart CRM para exponer datos por API."""

    _CUSTOMER_SORT_FIELDS = {
        "full_name": "dim.full_name",
        "identification": "dim.identification",
        "phone_number": "dim.phone_number",
    }
    _COMPANY_SORT_FIELDS = {
        "company_name": "dim.company_name",
        "ruc": "dim.ruc",
        "created_date": "created_date.full_date",
    }
    _BRANCH_SORT_FIELDS = {
        "branch_name": "fact.branch_name",
        "branch_code": "fact.branch_code",
        "branch_number": "fact.branch_number",
        "created_date": "created_date.full_date",
        "province": "fact.province",
    }

    def __init__(
        self,
        connection_factory: PostgreSQLConnectionFactory,
        mart_schema: str,
    ) -> None:
        """Recibe la fabrica de conexiones y el schema del mart."""

        self._connection_factory = connection_factory
        self._mart_schema = mart_schema

    def get_summary(
        self,
        search: str | None = None,
        province: str | None = None,
        is_active: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> CrmSummary:
        """Obtiene el resumen principal del dominio CRM."""

        logger.info("Ejecutando consulta de resumen CRM | schema=%s", self._mart_schema)

        customer_filters: list[str] = []
        customer_params: list[object] = []
        company_filters: list[str] = []
        company_params: list[object] = []
        branch_filters: list[str] = []
        branch_params: list[object] = []

        if search:
            customer_filters.append(
                "(dim.full_name ILIKE %s OR dim.identification ILIKE %s OR dim.phone_number ILIKE %s)"
            )
            customer_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            company_filters.append(
                "(dim.company_name ILIKE %s OR dim.ruc ILIKE %s OR COALESCE(dim.email, '') ILIKE %s)"
            )
            company_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
            branch_filters.append(
                "(fact.branch_code ILIKE %s OR fact.branch_name ILIKE %s OR COALESCE(fact.province, '') ILIKE %s)"
            )
            branch_params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if province:
            branch_filters.append("fact.province ILIKE %s")
            branch_params.append(f"%{province}%")
        if is_active is not None:
            branch_filters.append("fact.is_active = %s")
            branch_params.append(is_active)
        if date_from:
            company_filters.append("created_date.full_date >= %s")
            company_params.append(date_from)
            branch_filters.append("created_date.full_date >= %s")
            branch_params.append(date_from)
        if date_to:
            company_filters.append("created_date.full_date <= %s")
            company_params.append(date_to)
            branch_filters.append("created_date.full_date <= %s")
            branch_params.append(date_to)

        customer_where_sql = f"WHERE {' AND '.join(customer_filters)}" if customer_filters else ""
        company_where_sql = f"WHERE {' AND '.join(company_filters)}" if company_filters else ""
        branch_where_sql = f"WHERE {' AND '.join(branch_filters)}" if branch_filters else ""

        query = f"""
            WITH latest_extraction AS (
                SELECT MAX(extraction_id) AS extraction_id
                FROM {self._mart_schema}.fact_crm_customers
            ),
            customer_summary AS (
                SELECT
                    COUNT(*) AS total_clientes,
                    COALESCE(SUM(CASE WHEN fact.has_email THEN 1 ELSE 0 END), 0) AS clientes_con_correo,
                    COALESCE(SUM(CASE WHEN fact.has_address THEN 1 ELSE 0 END), 0) AS clientes_con_direccion,
                    COALESCE(SUM(CASE WHEN fact.has_phone THEN 1 ELSE 0 END), 0) AS clientes_con_contacto
                FROM {self._mart_schema}.fact_crm_customers fact
                INNER JOIN {self._mart_schema}.dim_crm_customer dim
                    ON dim.customer_key = fact.customer_key
                {customer_where_sql}
            ),
            company_summary AS (
                SELECT
                    COUNT(*) AS total_empresas,
                    COALESCE(SUM(CASE WHEN fact.has_email THEN 1 ELSE 0 END), 0) AS empresas_con_correo,
                    COALESCE(SUM(CASE WHEN fact.has_phone THEN 1 ELSE 0 END), 0) AS empresas_con_telefono
                FROM {self._mart_schema}.fact_crm_companies fact
                INNER JOIN {self._mart_schema}.dim_crm_company dim
                    ON dim.company_key = fact.company_key
                LEFT JOIN {self._mart_schema}.dim_crm_date created_date
                    ON created_date.date_key = fact.created_date_key
                {company_where_sql}
            ),
            branch_summary AS (
                SELECT
                    COUNT(*) AS total_sucursalescliente,
                    COALESCE(SUM(CASE WHEN fact.is_active THEN 1 ELSE 0 END), 0) AS sucursalescliente_activas
                FROM {self._mart_schema}.fact_crm_customer_branches fact
                LEFT JOIN {self._mart_schema}.dim_crm_date created_date
                    ON created_date.date_key = fact.created_date_key
                {branch_where_sql}
            )
            SELECT
                latest_extraction.extraction_id,
                customer_summary.total_clientes,
                customer_summary.clientes_con_correo,
                customer_summary.clientes_con_direccion,
                customer_summary.clientes_con_contacto,
                company_summary.total_empresas,
                company_summary.empresas_con_correo,
                company_summary.empresas_con_telefono,
                branch_summary.total_sucursalescliente,
                branch_summary.sucursalescliente_activas
            FROM latest_extraction
            CROSS JOIN customer_summary
            CROSS JOIN company_summary
            CROSS JOIN branch_summary
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    query,
                    [*customer_params, *company_params, *branch_params],
                )
                row = cursor.fetchone()

        logger.info(
            "Consulta de resumen CRM completada | extraction_id=%s | clientes=%s | empresas=%s | sucursales=%s",
            row["extraction_id"],
            row["total_clientes"],
            row["total_empresas"],
            row["total_sucursalescliente"],
        )

        return CrmSummary(
            extraction_id=row["extraction_id"],
            total_clientes=int(row["total_clientes"]),
            clientes_con_correo=int(row["clientes_con_correo"]),
            clientes_con_direccion=int(row["clientes_con_direccion"]),
            clientes_con_contacto=int(row["clientes_con_contacto"]),
            total_empresas=int(row["total_empresas"]),
            empresas_con_correo=int(row["empresas_con_correo"]),
            empresas_con_telefono=int(row["empresas_con_telefono"]),
            total_sucursalescliente=int(row["total_sucursalescliente"]),
            sucursalescliente_activas=int(row["sucursalescliente_activas"]),
        )

    def list_customers(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        identification: str | None = None,
        has_email: bool | None = None,
        has_address: bool | None = None,
        sort_by: str = "full_name",
        sort_dir: str = "asc",
    ) -> PaginatedCrmResult[CrmCustomerListItem]:
        """Lista clientes con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if search:
            filters.append(
                "(dim.full_name ILIKE %s OR dim.identification ILIKE %s OR dim.phone_number ILIKE %s)"
            )
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if identification:
            filters.append("dim.identification ILIKE %s")
            params.append(f"%{identification}%")
        if has_email is not None:
            filters.append("fact.has_email = %s")
            params.append(has_email)
        if has_address is not None:
            filters.append("fact.has_address = %s")
            params.append(has_address)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._CUSTOMER_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="dim.full_name ASC, fact.source_id ASC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_crm_customers fact
            INNER JOIN {self._mart_schema}.dim_crm_customer dim
                ON dim.customer_key = fact.customer_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                dim.full_name,
                dim.first_name,
                dim.last_name,
                dim.identification,
                dim.phone_number,
                dim.email,
                dim.address,
                fact.has_email,
                fact.has_address,
                fact.has_phone
            FROM {self._mart_schema}.fact_crm_customers fact
            INNER JOIN {self._mart_schema}.dim_crm_customer dim
                ON dim.customer_key = fact.customer_key
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
            item_builder=lambda row: CrmCustomerListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                full_name=row["full_name"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                identification=row["identification"],
                phone_number=row["phone_number"],
                email=row["email"],
                address=row["address"],
                has_email=row["has_email"],
                has_address=row["has_address"],
                has_phone=row["has_phone"],
            ),
        )

    def list_companies(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        ruc: str | None = None,
        has_email: bool | None = None,
        has_phone: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "company_name",
        sort_dir: str = "asc",
    ) -> PaginatedCrmResult[CrmCompanyListItem]:
        """Lista empresas con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if search:
            filters.append(
                "(dim.company_name ILIKE %s OR dim.ruc ILIKE %s OR COALESCE(dim.email, '') ILIKE %s)"
            )
            params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        if ruc:
            filters.append("dim.ruc ILIKE %s")
            params.append(f"%{ruc}%")
        if has_email is not None:
            filters.append("fact.has_email = %s")
            params.append(has_email)
        if has_phone is not None:
            filters.append("fact.has_phone = %s")
            params.append(has_phone)
        if date_from:
            filters.append("created_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("created_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._COMPANY_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="dim.company_name ASC, fact.source_id ASC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_crm_companies fact
            INNER JOIN {self._mart_schema}.dim_crm_company dim
                ON dim.company_key = fact.company_key
            LEFT JOIN {self._mart_schema}.dim_crm_date created_date
                ON created_date.date_key = fact.created_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                dim.company_name,
                dim.ruc,
                dim.phone_number,
                dim.email,
                dim.address,
                created_date.full_date AS created_date,
                fact.has_phone,
                fact.has_email,
                fact.has_address
            FROM {self._mart_schema}.fact_crm_companies fact
            INNER JOIN {self._mart_schema}.dim_crm_company dim
                ON dim.company_key = fact.company_key
            LEFT JOIN {self._mart_schema}.dim_crm_date created_date
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
            item_builder=lambda row: CrmCompanyListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                company_name=row["company_name"],
                ruc=row["ruc"],
                phone_number=row["phone_number"],
                email=row["email"],
                address=row["address"],
                created_date=row["created_date"],
                has_phone=row["has_phone"],
                has_email=row["has_email"],
                has_address=row["has_address"],
            ),
        )

    def list_customer_branches(
        self,
        limit: int,
        offset: int,
        branch_code: str | None = None,
        branch_name: str | None = None,
        province: str | None = None,
        novitec_branch_name: str | None = None,
        is_active: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "branch_name",
        sort_dir: str = "asc",
    ) -> PaginatedCrmResult[CrmCustomerBranchListItem]:
        """Lista sucursales cliente con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if branch_code:
            filters.append("fact.branch_code ILIKE %s")
            params.append(f"%{branch_code}%")
        if branch_name:
            filters.append("fact.branch_name ILIKE %s")
            params.append(f"%{branch_name}%")
        if province:
            filters.append("fact.province ILIKE %s")
            params.append(f"%{province}%")
        if novitec_branch_name:
            filters.append("fact.novitec_branch_name ILIKE %s")
            params.append(f"%{novitec_branch_name}%")
        if is_active is not None:
            filters.append("fact.is_active = %s")
            params.append(is_active)
        if date_from:
            filters.append("created_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("created_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._BRANCH_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="fact.branch_name ASC, fact.source_id ASC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_crm_customer_branches fact
            LEFT JOIN {self._mart_schema}.dim_crm_date created_date
                ON created_date.date_key = fact.created_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                created_date.full_date AS created_date,
                fact.branch_code,
                fact.branch_number,
                fact.branch_name,
                fact.province,
                fact.novitec_branch_name,
                fact.is_active
            FROM {self._mart_schema}.fact_crm_customer_branches fact
            LEFT JOIN {self._mart_schema}.dim_crm_date created_date
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
            item_builder=lambda row: CrmCustomerBranchListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                created_date=row["created_date"],
                branch_code=row["branch_code"],
                branch_number=row["branch_number"],
                branch_name=row["branch_name"],
                province=row["province"],
                novitec_branch_name=row["novitec_branch_name"],
                is_active=row["is_active"],
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
    ) -> PaginatedCrmResult:
        """Ejecuta una consulta paginada y mapea los resultados a DTOs."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(count_query, params)
                total = int(cursor.fetchone()["total"])
                cursor.execute(data_query, [*params, limit, offset])
                rows = cursor.fetchall()

        logger.info(
            "Consulta CRM paginada completada | total=%s | devueltos=%s | limit=%s | offset=%s",
            total,
            len(rows),
            limit,
            offset,
        )
        return PaginatedCrmResult(
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
