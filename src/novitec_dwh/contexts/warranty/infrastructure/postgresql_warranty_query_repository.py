"""Repositorio PostgreSQL de consultas sobre el mart de garantias."""

import logging
from datetime import date

from psycopg.rows import dict_row

from novitec_dwh.contexts.warranty.application.dto_query import (
    PaginatedWarrantyResult,
    WarrantyCompanyOrderListItem,
    WarrantyPersonalOrderListItem,
    WarrantyServiceCenterListItem,
    WarrantySummary,
    WarrantyUserAssignmentListItem,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger("novitec_dwh.warranty.repository")


class PostgreSQLWarrantyQueryRepository:
    """Consulta el mart de garantias para exponer datos por API."""

    _SERVICE_CENTER_SORT_FIELDS = {
        "service_center_name": "service_center_name",
        "prefix_code": "prefix_code",
        "brand_name": "brand_name",
        "city_name": "city_name",
    }
    _PERSONAL_ORDER_SORT_FIELDS = {
        "opened_date": "opened_date.full_date",
        "promised_date": "promised_date.full_date",
        "order_number": "fact.order_number",
        "order_status": "fact.order_status",
        "warranty_status": "fact.warranty_status",
        "cycle_days": "fact.cycle_days",
    }
    _COMPANY_ORDER_SORT_FIELDS = {
        "opened_date": "opened_date.full_date",
        "promised_date": "promised_date.full_date",
        "order_number": "fact.order_number",
        "order_status": "fact.order_status",
        "estimated_revenue": "fact.estimated_revenue",
        "worked_hours": "fact.worked_hours",
    }
    _ASSIGNMENT_SORT_FIELDS = {
        "user_name": "usr.user_name",
        "user_login": "usr.user_login",
        "service_center_name": "sc.service_center_name",
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
        service_center_name: str | None = None,
        technician_id: int | None = None,
        user_id: int | None = None,
        warranty_status: str | None = None,
        warranty_type: str | None = None,
        order_status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> WarrantySummary:
        """Obtiene el resumen principal del dominio de garantias."""

        logger.info("Ejecutando consulta de resumen de garantias | schema=%s", self._mart_schema)

        cas_filters: list[str] = []
        cas_params: list[object] = []
        personal_filters: list[str] = []
        personal_params: list[object] = []
        company_filters: list[str] = []
        company_params: list[object] = []
        assignment_filters: list[str] = []
        assignment_params: list[object] = []

        if service_center_name:
            cas_filters.append("service_center_name ILIKE %s")
            cas_params.append(f"%{service_center_name}%")

            personal_filters.append("fact.service_center_name ILIKE %s")
            personal_params.append(f"%{service_center_name}%")

            company_filters.append("sc.service_center_name ILIKE %s")
            company_params.append(f"%{service_center_name}%")

            assignment_filters.append("sc.service_center_name ILIKE %s")
            assignment_params.append(f"%{service_center_name}%")
        if technician_id is not None:
            personal_filters.append("usr.source_id = %s")
            personal_params.append(technician_id)
            company_filters.append("usr.source_id = %s")
            company_params.append(technician_id)
        if user_id is not None:
            assignment_filters.append("usr.source_id = %s")
            assignment_params.append(user_id)
        if warranty_status:
            personal_filters.append("fact.warranty_status ILIKE %s")
            personal_params.append(f"%{warranty_status}%")
        if warranty_type:
            personal_filters.append("fact.warranty_type ILIKE %s")
            personal_params.append(f"%{warranty_type}%")
        if order_status:
            personal_filters.append("fact.order_status ILIKE %s")
            personal_params.append(f"%{order_status}%")
            company_filters.append("fact.order_status ILIKE %s")
            company_params.append(f"%{order_status}%")
        if date_from:
            personal_filters.append("opened_date.full_date >= %s")
            personal_params.append(date_from)
            company_filters.append("opened_date.full_date >= %s")
            company_params.append(date_from)
        if date_to:
            personal_filters.append("opened_date.full_date <= %s")
            personal_params.append(date_to)
            company_filters.append("opened_date.full_date <= %s")
            company_params.append(date_to)

        cas_where_sql = f"WHERE {' AND '.join(cas_filters)}" if cas_filters else ""
        personal_where_sql = f"WHERE {' AND '.join(personal_filters)}" if personal_filters else ""
        company_where_sql = f"WHERE {' AND '.join(company_filters)}" if company_filters else ""
        assignment_where_sql = f"WHERE {' AND '.join(assignment_filters)}" if assignment_filters else ""

        query = f"""
            WITH latest_extraction AS (
                SELECT MAX(extraction_id) AS extraction_id
                FROM {self._mart_schema}.fact_warranty_personal_orders
            ),
            cas_summary AS (
                SELECT
                    COUNT(*) AS total_cas,
                    COALESCE(SUM(CASE WHEN is_active THEN 1 ELSE 0 END), 0) AS cas_activos
                FROM {self._mart_schema}.dim_warranty_service_center
                {cas_where_sql}
            ),
            personal_summary AS (
                SELECT
                    COUNT(*) AS total_ordenes_personales,
                    COALESCE(SUM(CASE WHEN fact.has_case_number THEN 1 ELSE 0 END), 0) AS ordenes_personales_con_caso,
                    COALESCE(SUM(CASE WHEN fact.is_closed THEN 1 ELSE 0 END), 0) AS ordenes_personales_cerradas
                FROM {self._mart_schema}.fact_warranty_personal_orders fact
                LEFT JOIN {self._mart_schema}.dim_warranty_date opened_date
                    ON opened_date.date_key = fact.opened_date_key
                LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                    ON usr.user_key = fact.technician_key
                {personal_where_sql}
            ),
            company_summary AS (
                SELECT
                    COUNT(*) AS total_ordenes_empresariales,
                    COALESCE(SUM(CASE WHEN fact.has_ticket_number THEN 1 ELSE 0 END), 0) AS ordenes_empresariales_con_ticket,
                    COALESCE(SUM(CASE WHEN fact.has_worked_hours THEN 1 ELSE 0 END), 0) AS ordenes_empresariales_con_horas
                FROM {self._mart_schema}.fact_warranty_company_orders fact
                LEFT JOIN {self._mart_schema}.dim_warranty_date opened_date
                    ON opened_date.date_key = fact.opened_date_key
                LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                    ON usr.user_key = fact.technician_key
                LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                    ON sc.service_center_key = fact.service_center_key
                {company_where_sql}
            ),
            assignment_summary AS (
                SELECT COUNT(*) AS total_asignaciones_usuario_cas
                FROM {self._mart_schema}.fact_warranty_user_assignments fact
                LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                    ON usr.user_key = fact.user_key
                LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                    ON sc.service_center_key = fact.service_center_key
                {assignment_where_sql}
            )
            SELECT
                latest_extraction.extraction_id,
                cas_summary.total_cas,
                cas_summary.cas_activos,
                personal_summary.total_ordenes_personales,
                personal_summary.ordenes_personales_con_caso,
                personal_summary.ordenes_personales_cerradas,
                company_summary.total_ordenes_empresariales,
                company_summary.ordenes_empresariales_con_ticket,
                company_summary.ordenes_empresariales_con_horas,
                assignment_summary.total_asignaciones_usuario_cas
            FROM latest_extraction
            CROSS JOIN cas_summary
            CROSS JOIN personal_summary
            CROSS JOIN company_summary
            CROSS JOIN assignment_summary
        """

        params = [*cas_params, *personal_params, *company_params, *assignment_params]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()

        return WarrantySummary(
            extraction_id=row["extraction_id"],
            total_cas=int(row["total_cas"]),
            cas_activos=int(row["cas_activos"]),
            total_ordenes_personales=int(row["total_ordenes_personales"]),
            ordenes_personales_con_caso=int(row["ordenes_personales_con_caso"]),
            ordenes_personales_cerradas=int(row["ordenes_personales_cerradas"]),
            total_ordenes_empresariales=int(row["total_ordenes_empresariales"]),
            ordenes_empresariales_con_ticket=int(row["ordenes_empresariales_con_ticket"]),
            ordenes_empresariales_con_horas=int(row["ordenes_empresariales_con_horas"]),
            total_asignaciones_usuario_cas=int(row["total_asignaciones_usuario_cas"]),
        )

    def list_service_centers(
        self,
        limit: int,
        offset: int,
        service_center_name: str | None = None,
        prefix_code: str | None = None,
        brand_name: str | None = None,
        city_name: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "service_center_name",
        sort_dir: str = "asc",
    ) -> PaginatedWarrantyResult[WarrantyServiceCenterListItem]:
        """Lista CAS con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if service_center_name:
            filters.append("service_center_name ILIKE %s")
            params.append(f"%{service_center_name}%")
        if prefix_code:
            filters.append("COALESCE(prefix_code, '') ILIKE %s")
            params.append(f"%{prefix_code}%")
        if brand_name:
            filters.append("COALESCE(brand_name, '') ILIKE %s")
            params.append(f"%{brand_name}%")
        if city_name:
            filters.append("COALESCE(city_name, '') ILIKE %s")
            params.append(f"%{city_name}%")
        if is_active is not None:
            filters.append("is_active = %s")
            params.append(is_active)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._SERVICE_CENTER_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="service_center_name ASC, source_id ASC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.dim_warranty_service_center
            {where_sql}
        """
        data_query = f"""
            SELECT
                source_id,
                service_center_name,
                prefix_code,
                brand_name,
                phone_number,
                email,
                city_name,
                contact_name,
                is_active
            FROM {self._mart_schema}.dim_warranty_service_center
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
            item_builder=lambda row: WarrantyServiceCenterListItem(
                source_id=row["source_id"],
                service_center_name=row["service_center_name"],
                prefix_code=row["prefix_code"],
                brand_name=row["brand_name"],
                phone_number=row["phone_number"],
                email=row["email"],
                city_name=row["city_name"],
                contact_name=row["contact_name"],
                is_active=row["is_active"],
            ),
        )

    def list_personal_orders(
        self,
        limit: int,
        offset: int,
        order_number: str | None = None,
        service_center_name: str | None = None,
        technician_id: int | None = None,
        warranty_status: str | None = None,
        warranty_type: str | None = None,
        order_status: str | None = None,
        has_case_number: bool | None = None,
        is_closed: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "opened_date",
        sort_dir: str = "desc",
    ) -> PaginatedWarrantyResult[WarrantyPersonalOrderListItem]:
        """Lista ordenes personales con garantia."""

        filters: list[str] = []
        params: list[object] = []

        if order_number:
            filters.append("COALESCE(fact.order_number, '') ILIKE %s")
            params.append(f"%{order_number}%")
        if service_center_name:
            filters.append("fact.service_center_name ILIKE %s")
            params.append(f"%{service_center_name}%")
        if technician_id is not None:
            filters.append("usr.source_id = %s")
            params.append(technician_id)
        if warranty_status:
            filters.append("fact.warranty_status ILIKE %s")
            params.append(f"%{warranty_status}%")
        if warranty_type:
            filters.append("fact.warranty_type ILIKE %s")
            params.append(f"%{warranty_type}%")
        if order_status:
            filters.append("fact.order_status ILIKE %s")
            params.append(f"%{order_status}%")
        if has_case_number is not None:
            filters.append("fact.has_case_number = %s")
            params.append(has_case_number)
        if is_closed is not None:
            filters.append("fact.is_closed = %s")
            params.append(is_closed)
        if date_from:
            filters.append("opened_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("opened_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._PERSONAL_ORDER_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="opened_date.full_date DESC NULLS LAST, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_warranty_personal_orders fact
            LEFT JOIN {self._mart_schema}.dim_warranty_date opened_date
                ON opened_date.date_key = fact.opened_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.user_key = fact.technician_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.order_number,
                fact.order_status,
                fact.warranty_status,
                fact.warranty_type,
                fact.service_center_name,
                opened_date.full_date AS opened_date,
                promised_date.full_date AS promised_date,
                shipped_date.full_date AS shipped_date,
                returned_date.full_date AS returned_date,
                delivered_date.full_date AS delivered_date,
                finalized_date.full_date AS finalized_date,
                usr.source_id AS technician_id,
                fact.branch_id,
                fact.client_id,
                fact.equipment_id,
                fact.case_number,
                fact.cycle_days,
                fact.sla_days,
                fact.has_case_number,
                fact.has_return_date,
                fact.is_closed
            FROM {self._mart_schema}.fact_warranty_personal_orders fact
            LEFT JOIN {self._mart_schema}.dim_warranty_date opened_date
                ON opened_date.date_key = fact.opened_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_date promised_date
                ON promised_date.date_key = fact.promised_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_date shipped_date
                ON shipped_date.date_key = fact.shipped_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_date returned_date
                ON returned_date.date_key = fact.returned_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_date delivered_date
                ON delivered_date.date_key = fact.delivered_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_date finalized_date
                ON finalized_date.date_key = fact.finalized_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.user_key = fact.technician_key
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
            item_builder=lambda row: WarrantyPersonalOrderListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                order_number=row["order_number"],
                order_status=row["order_status"],
                warranty_status=row["warranty_status"],
                warranty_type=row["warranty_type"],
                service_center_name=row["service_center_name"],
                opened_date=row["opened_date"],
                promised_date=row["promised_date"],
                shipped_date=row["shipped_date"],
                returned_date=row["returned_date"],
                delivered_date=row["delivered_date"],
                finalized_date=row["finalized_date"],
                technician_id=row["technician_id"],
                branch_id=row["branch_id"],
                client_id=row["client_id"],
                equipment_id=row["equipment_id"],
                case_number=row["case_number"],
                cycle_days=row["cycle_days"],
                sla_days=row["sla_days"],
                has_case_number=row["has_case_number"],
                has_return_date=row["has_return_date"],
                is_closed=row["is_closed"],
            ),
        )

    def list_company_orders(
        self,
        limit: int,
        offset: int,
        order_number: str | None = None,
        service_center_name: str | None = None,
        technician_id: int | None = None,
        company_id: int | None = None,
        order_status: str | None = None,
        has_ticket_number: bool | None = None,
        has_worked_hours: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "opened_date",
        sort_dir: str = "desc",
    ) -> PaginatedWarrantyResult[WarrantyCompanyOrderListItem]:
        """Lista ordenes empresariales asociadas a CAS."""

        filters: list[str] = []
        params: list[object] = []

        if order_number:
            filters.append("fact.order_number ILIKE %s")
            params.append(f"%{order_number}%")
        if service_center_name:
            filters.append("COALESCE(sc.service_center_name, '') ILIKE %s")
            params.append(f"%{service_center_name}%")
        if technician_id is not None:
            filters.append("usr.source_id = %s")
            params.append(technician_id)
        if company_id is not None:
            filters.append("fact.company_id = %s")
            params.append(company_id)
        if order_status:
            filters.append("fact.order_status ILIKE %s")
            params.append(f"%{order_status}%")
        if has_ticket_number is not None:
            filters.append("fact.has_ticket_number = %s")
            params.append(has_ticket_number)
        if has_worked_hours is not None:
            filters.append("fact.has_worked_hours = %s")
            params.append(has_worked_hours)
        if date_from:
            filters.append("opened_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("opened_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._COMPANY_ORDER_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="opened_date.full_date DESC NULLS LAST, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_warranty_company_orders fact
            LEFT JOIN {self._mart_schema}.dim_warranty_date opened_date
                ON opened_date.date_key = fact.opened_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.user_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                ON sc.service_center_key = fact.service_center_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.order_number,
                fact.order_status,
                opened_date.full_date AS opened_date,
                promised_date.full_date AS promised_date,
                sc.service_center_name,
                usr.source_id AS technician_id,
                fact.branch_id,
                fact.company_id,
                fact.equipment_id,
                fact.ticket_number,
                fact.hourly_rate,
                fact.worked_hours,
                fact.estimated_revenue,
                fact.cycle_days,
                fact.sla_days,
                fact.has_ticket_number,
                fact.has_worked_hours
            FROM {self._mart_schema}.fact_warranty_company_orders fact
            LEFT JOIN {self._mart_schema}.dim_warranty_date opened_date
                ON opened_date.date_key = fact.opened_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_date promised_date
                ON promised_date.date_key = fact.promised_date_key
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.user_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                ON sc.service_center_key = fact.service_center_key
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
            item_builder=lambda row: WarrantyCompanyOrderListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                order_number=row["order_number"],
                order_status=row["order_status"],
                opened_date=row["opened_date"],
                promised_date=row["promised_date"],
                service_center_name=row["service_center_name"],
                technician_id=row["technician_id"],
                branch_id=row["branch_id"],
                company_id=row["company_id"],
                equipment_id=row["equipment_id"],
                ticket_number=row["ticket_number"],
                hourly_rate=row["hourly_rate"],
                worked_hours=row["worked_hours"],
                estimated_revenue=row["estimated_revenue"],
                cycle_days=row["cycle_days"],
                sla_days=row["sla_days"],
                has_ticket_number=row["has_ticket_number"],
                has_worked_hours=row["has_worked_hours"],
            ),
        )

    def list_user_assignments(
        self,
        limit: int,
        offset: int,
        user_id: int | None = None,
        user_login: str | None = None,
        user_name: str | None = None,
        service_center_name: str | None = None,
        sort_by: str = "user_name",
        sort_dir: str = "asc",
    ) -> PaginatedWarrantyResult[WarrantyUserAssignmentListItem]:
        """Lista asignaciones entre usuarios y CAS."""

        filters: list[str] = []
        params: list[object] = []

        if user_id is not None:
            filters.append("fact.user_id = %s")
            params.append(user_id)
        if user_login:
            filters.append("COALESCE(usr.user_login, '') ILIKE %s")
            params.append(f"%{user_login}%")
        if user_name:
            filters.append("COALESCE(usr.user_name, '') ILIKE %s")
            params.append(f"%{user_name}%")
        if service_center_name:
            filters.append("COALESCE(sc.service_center_name, '') ILIKE %s")
            params.append(f"%{service_center_name}%")

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._ASSIGNMENT_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="usr.user_name ASC NULLS LAST, fact.source_id ASC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_warranty_user_assignments fact
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                ON sc.service_center_key = fact.service_center_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.user_id,
                usr.user_login,
                usr.user_name,
                fact.service_center_id,
                sc.service_center_name
            FROM {self._mart_schema}.fact_warranty_user_assignments fact
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.user_key = fact.user_key
            LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                ON sc.service_center_key = fact.service_center_key
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
            item_builder=lambda row: WarrantyUserAssignmentListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                user_id=row["user_id"],
                user_login=row["user_login"],
                user_name=row["user_name"],
                service_center_id=row["service_center_id"],
                service_center_name=row["service_center_name"],
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
    ) -> PaginatedWarrantyResult:
        """Ejecuta una consulta paginada y mapea los resultados a DTOs."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(count_query, params)
                total = int(cursor.fetchone()["total"])
                cursor.execute(data_query, [*params, limit, offset])
                rows = cursor.fetchall()

        logger.info(
            "Consulta de garantias paginada completada | total=%s | devueltos=%s | limit=%s | offset=%s",
            total,
            len(rows),
            limit,
            offset,
        )
        return PaginatedWarrantyResult(
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
