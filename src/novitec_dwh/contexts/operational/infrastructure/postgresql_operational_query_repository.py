"""Repositorio PostgreSQL de consultas sobre el mart operativo."""

import logging
from datetime import date
from decimal import Decimal

from psycopg.rows import dict_row

from novitec_dwh.contexts.operational.application.dto_query import (
    OperationalAssignmentListItem,
    OperationalOrderListItem,
    OperationalPreorderListItem,
    OperationalSummary,
    PaginatedOperationalResult,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger("novitec_dwh.operational.repository")


class PostgreSQLOperationalQueryRepository:
    """Consulta el mart operativo para exponer datos por API."""

    _ORDER_SORT_FIELDS = {
        "intake_date": "intake_date.full_date",
        "delivery_date": "delivery_date.full_date",
        "order_number": "fact.order_number",
        "order_status": "fact.order_status",
        "technician_name": "tech.tecnico_nombre",
        "branch_name": "branch.sucursal_nombre",
        "cycle_days": "fact.cycle_days",
        "delay_days": "fact.delay_days",
    }
    _PREORDER_SORT_FIELDS = {
        "registration_date": "registration_date.full_date",
        "preorder_number": "fact.preorder_number",
        "preorder_status": "fact.preorder_status",
        "branch_name": "branch.sucursal_nombre",
    }
    _ASSIGNMENT_SORT_FIELDS = {
        "source_order_id": "fact.source_order_id",
        "technician_name": "tech.tecnico_nombre",
        "assignment_count": "fact.assignment_count",
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
        order_type: str | None = None,
        technician_name: str | None = None,
        branch_name: str | None = None,
        status_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> OperationalSummary:
        """Obtiene el resumen principal del dominio operativo."""

        order_filters: list[str] = []
        order_params: list[object] = []
        preorder_filters: list[str] = []
        preorder_params: list[object] = []

        if order_type:
            order_filters.append("fact.order_type = %s")
            order_params.append(order_type)
        if technician_name:
            order_filters.append("tech.tecnico_nombre ILIKE %s")
            order_params.append(f"%{technician_name}%")
        if branch_name:
            order_filters.append("branch.sucursal_nombre ILIKE %s")
            order_params.append(f"%{branch_name}%")
            preorder_filters.append("branch.sucursal_nombre ILIKE %s")
            preorder_params.append(f"%{branch_name}%")
        if status_name:
            order_filters.append("fact.order_status = %s")
            order_params.append(status_name)
        if date_from:
            order_filters.append("intake_date.full_date >= %s")
            order_params.append(date_from)
            preorder_filters.append("registration_date.full_date >= %s")
            preorder_params.append(date_from)
        if date_to:
            order_filters.append("intake_date.full_date <= %s")
            order_params.append(date_to)
            preorder_filters.append("registration_date.full_date <= %s")
            preorder_params.append(date_to)

        order_where_sql = f"WHERE {' AND '.join(order_filters)}" if order_filters else ""
        preorder_where_sql = f"WHERE {' AND '.join(preorder_filters)}" if preorder_filters else ""

        query = f"""
            WITH latest_extraction AS (
                SELECT MAX(extraction_id) AS extraction_id
                FROM {self._mart_schema}.fact_operational_orders
            ),
            order_summary AS (
                SELECT
                    COUNT(*) AS total_ordenes,
                    COALESCE(SUM(CASE WHEN fact.is_open THEN 1 ELSE 0 END), 0) AS ordenes_abiertas,
                    COALESCE(SUM(CASE WHEN fact.is_delivered THEN 1 ELSE 0 END), 0) AS ordenes_entregadas,
                    COALESCE(SUM(CASE WHEN fact.is_warranty THEN 1 ELSE 0 END), 0) AS ordenes_con_garantia,
                    AVG(fact.cycle_days) AS promedio_dias_ciclo
                FROM {self._mart_schema}.fact_operational_orders fact
                LEFT JOIN {self._mart_schema}.dim_operational_date intake_date
                    ON intake_date.date_key = fact.intake_date_key
                LEFT JOIN {self._mart_schema}.dim_operational_technician tech
                    ON tech.technician_key = fact.technician_key
                LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                    ON branch.branch_key = fact.branch_key
                {order_where_sql}
            ),
            preorder_summary AS (
                SELECT COUNT(*) AS total_preordenes
                FROM {self._mart_schema}.fact_operational_preorders fact
                LEFT JOIN {self._mart_schema}.dim_operational_date registration_date
                    ON registration_date.date_key = fact.registration_date_key
                LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                    ON branch.branch_key = fact.branch_key
                {preorder_where_sql}
            ),
            assignment_summary AS (
                SELECT COUNT(*) AS total_asignaciones_tecnicos
                FROM {self._mart_schema}.fact_operational_company_order_assignments
            )
            SELECT
                latest_extraction.extraction_id,
                order_summary.total_ordenes,
                order_summary.ordenes_abiertas,
                order_summary.ordenes_entregadas,
                order_summary.ordenes_con_garantia,
                preorder_summary.total_preordenes,
                assignment_summary.total_asignaciones_tecnicos,
                order_summary.promedio_dias_ciclo
            FROM latest_extraction
            CROSS JOIN order_summary
            CROSS JOIN preorder_summary
            CROSS JOIN assignment_summary
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, [*order_params, *preorder_params])
                row = cursor.fetchone()

        return OperationalSummary(
            extraction_id=row["extraction_id"],
            total_ordenes=int(row["total_ordenes"]),
            ordenes_abiertas=int(row["ordenes_abiertas"]),
            ordenes_entregadas=int(row["ordenes_entregadas"]),
            ordenes_con_garantia=int(row["ordenes_con_garantia"]),
            total_preordenes=int(row["total_preordenes"]),
            total_asignaciones_tecnicos=int(row["total_asignaciones_tecnicos"]),
            promedio_dias_ciclo=Decimal(str(row["promedio_dias_ciclo"])) if row["promedio_dias_ciclo"] is not None else None,
        )

    def list_orders(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        order_type: str | None = None,
        status_name: str | None = None,
        technician_name: str | None = None,
        branch_name: str | None = None,
        customer_type: str | None = None,
        is_open: bool | None = None,
        is_warranty: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "intake_date",
        sort_dir: str = "desc",
    ) -> PaginatedOperationalResult[OperationalOrderListItem]:
        """Lista ordenes operativas con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if search:
            filters.append(
                "(fact.order_number ILIKE %s OR fact.customer_name ILIKE %s OR tech.tecnico_nombre ILIKE %s)"
            )
            search_value = f"%{search}%"
            params.extend([search_value, search_value, search_value])
        if order_type:
            filters.append("fact.order_type = %s")
            params.append(order_type)
        if status_name:
            filters.append("fact.order_status = %s")
            params.append(status_name)
        if technician_name:
            filters.append("tech.tecnico_nombre ILIKE %s")
            params.append(f"%{technician_name}%")
        if branch_name:
            filters.append("branch.sucursal_nombre ILIKE %s")
            params.append(f"%{branch_name}%")
        if customer_type:
            filters.append("fact.customer_type = %s")
            params.append(customer_type)
        if is_open is not None:
            filters.append("fact.is_open = %s")
            params.append(is_open)
        if is_warranty is not None:
            filters.append("fact.is_warranty = %s")
            params.append(is_warranty)
        if date_from:
            filters.append("intake_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("intake_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._ORDER_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="intake_date.full_date DESC NULLS LAST, fact.order_number DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_operational_orders fact
            LEFT JOIN {self._mart_schema}.dim_operational_date intake_date
                ON intake_date.date_key = fact.intake_date_key
            LEFT JOIN {self._mart_schema}.dim_operational_technician tech
                ON tech.technician_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                ON branch.branch_key = fact.branch_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_order_id,
                fact.order_type,
                fact.order_number,
                intake_date.full_date AS intake_date,
                promised_date.full_date AS promised_date,
                delivery_date.full_date AS delivery_date,
                fact.order_status,
                fact.intake_reason,
                fact.customer_type,
                fact.customer_name,
                tech.tecnico_nombre AS technician_name,
                branch.sucursal_nombre AS branch_name,
                fact.cycle_days,
                fact.delay_days,
                fact.worked_hours,
                fact.hourly_rate,
                fact.is_open,
                fact.is_delivered,
                fact.is_warranty
            FROM {self._mart_schema}.fact_operational_orders fact
            LEFT JOIN {self._mart_schema}.dim_operational_date intake_date
                ON intake_date.date_key = fact.intake_date_key
            LEFT JOIN {self._mart_schema}.dim_operational_date promised_date
                ON promised_date.date_key = fact.promised_date_key
            LEFT JOIN {self._mart_schema}.dim_operational_date delivery_date
                ON delivery_date.date_key = fact.delivery_date_key
            LEFT JOIN {self._mart_schema}.dim_operational_technician tech
                ON tech.technician_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                ON branch.branch_key = fact.branch_key
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
            item_builder=lambda row: OperationalOrderListItem(
                extraction_id=row["extraction_id"],
                source_order_id=row["source_order_id"],
                order_type=row["order_type"],
                order_number=row["order_number"],
                intake_date=row["intake_date"],
                promised_date=row["promised_date"],
                delivery_date=row["delivery_date"],
                order_status=row["order_status"],
                intake_reason=row["intake_reason"],
                customer_type=row["customer_type"],
                customer_name=row["customer_name"],
                technician_name=row["technician_name"],
                branch_name=row["branch_name"],
                cycle_days=row["cycle_days"],
                delay_days=row["delay_days"],
                worked_hours=Decimal(str(row["worked_hours"])) if row["worked_hours"] is not None else None,
                hourly_rate=Decimal(str(row["hourly_rate"])) if row["hourly_rate"] is not None else None,
                is_open=row["is_open"],
                is_delivered=row["is_delivered"],
                is_warranty=row["is_warranty"],
            ),
        )

    def list_preorders(
        self,
        limit: int,
        offset: int,
        preorder_status: str | None = None,
        branch_name: str | None = None,
        has_invoice: bool | None = None,
        has_photos: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "registration_date",
        sort_dir: str = "desc",
    ) -> PaginatedOperationalResult[OperationalPreorderListItem]:
        """Lista preordenes operativas con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if preorder_status:
            filters.append("fact.preorder_status = %s")
            params.append(preorder_status)
        if branch_name:
            filters.append("branch.sucursal_nombre ILIKE %s")
            params.append(f"%{branch_name}%")
        if has_invoice is not None:
            filters.append("fact.has_invoice = %s")
            params.append(has_invoice)
        if has_photos is not None:
            filters.append("fact.has_photos = %s")
            params.append(has_photos)
        if date_from:
            filters.append("registration_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("registration_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._PREORDER_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="registration_date.full_date DESC NULLS LAST, fact.preorder_number DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_operational_preorders fact
            LEFT JOIN {self._mart_schema}.dim_operational_date registration_date
                ON registration_date.date_key = fact.registration_date_key
            LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                ON branch.branch_key = fact.branch_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.linked_order_id,
                fact.preorder_number,
                registration_date.full_date AS registration_date,
                fact.preorder_status,
                fact.customer_name,
                branch.sucursal_nombre AS branch_name,
                fact.city_name,
                fact.has_invoice,
                fact.has_photos
            FROM {self._mart_schema}.fact_operational_preorders fact
            LEFT JOIN {self._mart_schema}.dim_operational_date registration_date
                ON registration_date.date_key = fact.registration_date_key
            LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                ON branch.branch_key = fact.branch_key
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
            item_builder=lambda row: OperationalPreorderListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                linked_order_id=row["linked_order_id"],
                preorder_number=row["preorder_number"],
                registration_date=row["registration_date"],
                preorder_status=row["preorder_status"],
                customer_name=row["customer_name"],
                branch_name=row["branch_name"],
                city_name=row["city_name"],
                has_invoice=row["has_invoice"],
                has_photos=row["has_photos"],
            ),
        )

    def list_company_order_assignments(
        self,
        limit: int,
        offset: int,
        source_order_id: int | None = None,
        technician_name: str | None = None,
        sort_by: str = "source_order_id",
        sort_dir: str = "desc",
    ) -> PaginatedOperationalResult[OperationalAssignmentListItem]:
        """Lista asignaciones tecnico-orden empresarial con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if source_order_id is not None:
            filters.append("fact.source_order_id = %s")
            params.append(source_order_id)
        if technician_name:
            filters.append("tech.tecnico_nombre ILIKE %s")
            params.append(f"%{technician_name}%")

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._ASSIGNMENT_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="fact.source_order_id DESC, tech.tecnico_nombre ASC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_operational_company_order_assignments fact
            INNER JOIN {self._mart_schema}.dim_operational_technician tech
                ON tech.technician_key = fact.technician_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.source_order_id,
                tech.tecnico_nombre AS technician_name,
                fact.assignment_count
            FROM {self._mart_schema}.fact_operational_company_order_assignments fact
            INNER JOIN {self._mart_schema}.dim_operational_technician tech
                ON tech.technician_key = fact.technician_key
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
            item_builder=lambda row: OperationalAssignmentListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                source_order_id=row["source_order_id"],
                technician_name=row["technician_name"],
                assignment_count=row["assignment_count"],
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
    ) -> PaginatedOperationalResult:
        """Ejecuta una consulta paginada y mapea los resultados a DTOs."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(count_query, params)
                total = int(cursor.fetchone()["total"])
                cursor.execute(data_query, [*params, limit, offset])
                rows = cursor.fetchall()

        logger.info(
            "Consulta operativa paginada completada | total=%s | devueltos=%s | limit=%s | offset=%s",
            total,
            len(rows),
            limit,
            offset,
        )
        return PaginatedOperationalResult(
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
