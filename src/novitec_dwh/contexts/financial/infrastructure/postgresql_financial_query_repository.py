"""Repositorio PostgreSQL de consultas sobre el mart financiero."""

import logging
from datetime import date
from decimal import Decimal

from psycopg.rows import dict_row

from novitec_dwh.contexts.financial.application.dto import (
    CreditNoteRequestListItem,
    FinancialSummary,
    NotificationListItem,
    OrderPriceListItem,
    PaginatedResult,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger("novitec_dwh.financial.repository")


class PostgreSQLFinancialQueryRepository:
    """Consulta el mart financiero para exponer datos por API."""

    _CREDIT_NOTE_SORT_FIELDS = {
        "request_date": "request_date.full_date",
        "request_number": "fact.request_number",
        "order_number": "fact.order_number",
        "status_name": "fact.status_name",
        "technician_name": "technician.tecnico_nombre",
        "admin_name": "fact.admin_name",
        "created_at": "fact.created_at",
    }
    _ORDER_PRICE_SORT_FIELDS = {
        "created_at": "fact.created_at",
        "order_id": "fact.order_id",
        "order_number": "fact.order_number",
        "service_name": "fact.service_name",
        "amount": "fact.amount",
        "standard_amount": "fact.standard_amount",
    }
    _NOTIFICATION_SORT_FIELDS = {
        "created_at": "fact.created_at",
        "order_id": "fact.order_id",
        "order_number": "fact.order_number",
        "nc_id": "fact.nc_id",
        "notification_type": "fact.notification_type",
        "technician_name": "technician.tecnico_nombre",
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
        order_id: int | None = None,
        order_number: str | None = None,
        technician_name: str | None = None,
        admin_name: str | None = None,
        status_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> FinancialSummary:
        """Obtiene el resumen principal del dominio financiero."""

        logger.info(
            "Ejecutando consulta de resumen financiero | schema=%s",
            self._mart_schema,
        )

        credit_note_filters: list[str] = []
        credit_note_params: list[object] = []
        order_price_filters: list[str] = []
        order_price_params: list[object] = []
        notification_filters: list[str] = []
        notification_params: list[object] = []

        if order_id is not None:
            credit_note_filters.append("fact.order_id = %s")
            credit_note_params.append(order_id)
            order_price_filters.append("fact.order_id = %s")
            order_price_params.append(order_id)
            notification_filters.append("fact.order_id = %s")
            notification_params.append(order_id)
        if order_number:
            order_number_value = f"%{order_number}%"
            credit_note_filters.append("fact.order_number ILIKE %s")
            credit_note_params.append(order_number_value)
            order_price_filters.append("fact.order_number ILIKE %s")
            order_price_params.append(order_number_value)
            notification_filters.append("fact.order_number ILIKE %s")
            notification_params.append(order_number_value)
        if technician_name:
            technician_value = f"%{technician_name}%"
            credit_note_filters.append("technician.tecnico_nombre ILIKE %s")
            credit_note_params.append(technician_value)
            notification_filters.append("technician.tecnico_nombre ILIKE %s")
            notification_params.append(technician_value)
        if admin_name:
            credit_note_filters.append("fact.admin_name ILIKE %s")
            credit_note_params.append(f"%{admin_name}%")
        if status_name:
            credit_note_filters.append("fact.status_name = %s")
            credit_note_params.append(status_name)
        if date_from:
            credit_note_filters.append("request_date.full_date >= %s")
            credit_note_params.append(date_from)
            order_price_filters.append("created_date.full_date >= %s")
            order_price_params.append(date_from)
            notification_filters.append("notification_date.full_date >= %s")
            notification_params.append(date_from)
        if date_to:
            credit_note_filters.append("request_date.full_date <= %s")
            credit_note_params.append(date_to)
            order_price_filters.append("created_date.full_date <= %s")
            order_price_params.append(date_to)
            notification_filters.append("notification_date.full_date <= %s")
            notification_params.append(date_to)

        credit_note_where_sql = f"WHERE {' AND '.join(credit_note_filters)}" if credit_note_filters else ""
        order_price_where_sql = f"WHERE {' AND '.join(order_price_filters)}" if order_price_filters else ""
        notification_where_sql = f"WHERE {' AND '.join(notification_filters)}" if notification_filters else ""

        query = f"""
            WITH latest_extraction AS (
                SELECT MAX(extraction_id) AS extraction_id
                FROM {self._mart_schema}.fact_financial_credit_note_requests
            ),
            credit_note_summary AS (
                SELECT
                    COUNT(*) AS total_solicitudes_nc,
                    COALESCE(SUM(CASE WHEN is_approved THEN 1 ELSE 0 END), 0) AS solicitudes_aprobadas,
                    COALESCE(SUM(CASE WHEN is_rejected THEN 1 ELSE 0 END), 0) AS solicitudes_rechazadas,
                    COALESCE(SUM(CASE WHEN is_pending THEN 1 ELSE 0 END), 0) AS solicitudes_pendientes
                FROM {self._mart_schema}.fact_financial_credit_note_requests fact
                INNER JOIN {self._mart_schema}.dim_financial_technician technician
                    ON technician.technician_key = fact.technician_key
                INNER JOIN {self._mart_schema}.dim_financial_date request_date
                    ON request_date.date_key = fact.request_date_key
                {credit_note_where_sql}
            ),
            order_price_summary AS (
                SELECT
                    COUNT(*) AS total_registros_ingreso,
                    COALESCE(SUM(amount), 0) AS monto_total_ingresos
                FROM {self._mart_schema}.fact_financial_order_prices fact
                LEFT JOIN {self._mart_schema}.dim_financial_date created_date
                    ON created_date.date_key = fact.created_date_key
                {order_price_where_sql}
            ),
            notification_summary AS (
                SELECT
                    COUNT(*) AS total_notificaciones,
                    COALESCE(SUM(CASE WHEN is_read THEN 1 ELSE 0 END), 0) AS total_notificaciones_leidas
                FROM {self._mart_schema}.fact_financial_credit_note_notifications fact
                INNER JOIN {self._mart_schema}.dim_financial_technician technician
                    ON technician.technician_key = fact.technician_key
                INNER JOIN {self._mart_schema}.dim_financial_date notification_date
                    ON notification_date.date_key = fact.notification_date_key
                {notification_where_sql}
            )
            SELECT
                latest_extraction.extraction_id,
                credit_note_summary.total_solicitudes_nc,
                credit_note_summary.solicitudes_aprobadas,
                credit_note_summary.solicitudes_rechazadas,
                credit_note_summary.solicitudes_pendientes,
                order_price_summary.total_registros_ingreso,
                order_price_summary.monto_total_ingresos,
                notification_summary.total_notificaciones,
                notification_summary.total_notificaciones_leidas
            FROM latest_extraction
            CROSS JOIN credit_note_summary
            CROSS JOIN order_price_summary
            CROSS JOIN notification_summary
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    query,
                    [
                        *credit_note_params,
                        *order_price_params,
                        *notification_params,
                    ],
                )
                row = cursor.fetchone()

        logger.info(
            "Consulta de resumen financiero completada | extraction_id=%s | solicitudes_nc=%s | ingresos=%s | notificaciones=%s",
            row["extraction_id"],
            row["total_solicitudes_nc"],
            row["total_registros_ingreso"],
            row["total_notificaciones"],
        )

        return FinancialSummary(
            extraction_id=row["extraction_id"],
            total_solicitudes_nc=int(row["total_solicitudes_nc"]),
            solicitudes_aprobadas=int(row["solicitudes_aprobadas"]),
            solicitudes_rechazadas=int(row["solicitudes_rechazadas"]),
            solicitudes_pendientes=int(row["solicitudes_pendientes"]),
            total_registros_ingreso=int(row["total_registros_ingreso"]),
            monto_total_ingresos=Decimal(row["monto_total_ingresos"]),
            total_notificaciones=int(row["total_notificaciones"]),
            total_notificaciones_leidas=int(row["total_notificaciones_leidas"]),
        )

    def list_credit_note_requests(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        request_number: str | None = None,
        order_id: int | None = None,
        order_number: str | None = None,
        status_name: str | None = None,
        technician_name: str | None = None,
        admin_name: str | None = None,
        subject_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "request_date",
        sort_dir: str = "desc",
    ) -> PaginatedResult[CreditNoteRequestListItem]:
        """Lista solicitudes NC con filtros opcionales."""

        logger.info(
            "Ejecutando consulta de solicitudes NC | schema=%s | sort_by=%s | sort_dir=%s",
            self._mart_schema,
            sort_by,
            sort_dir,
        )

        filters: list[str] = []
        params: list[object] = []

        if search:
            filters.append(
                "("
                "fact.request_number ILIKE %s OR "
                "fact.order_number ILIKE %s OR "
                "fact.subject_name ILIKE %s OR "
                "fact.admin_name ILIKE %s OR "
                "technician.tecnico_nombre ILIKE %s"
                ")"
            )
            search_value = f"%{search}%"
            params.extend([search_value, search_value, search_value, search_value, search_value])
        if request_number:
            filters.append("fact.request_number ILIKE %s")
            params.append(f"%{request_number}%")
        if order_id is not None:
            filters.append("fact.order_id = %s")
            params.append(order_id)
        if order_number:
            filters.append("fact.order_number ILIKE %s")
            params.append(f"%{order_number}%")
        if status_name:
            filters.append("fact.status_name = %s")
            params.append(status_name)
        if technician_name:
            filters.append("technician.tecnico_nombre ILIKE %s")
            params.append(f"%{technician_name}%")
        if admin_name:
            filters.append("fact.admin_name ILIKE %s")
            params.append(f"%{admin_name}%")
        if subject_name:
            filters.append("fact.subject_name ILIKE %s")
            params.append(f"%{subject_name}%")
        if date_from:
            filters.append("request_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("request_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._CREDIT_NOTE_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="request_date.full_date DESC, fact.request_number DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_financial_credit_note_requests fact
            INNER JOIN {self._mart_schema}.dim_financial_technician technician
                ON technician.technician_key = fact.technician_key
            INNER JOIN {self._mart_schema}.dim_financial_date request_date
                ON request_date.date_key = fact.request_date_key
            {where_sql}
        """

        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.request_number,
                fact.order_id,
                fact.order_number,
                request_date.full_date AS request_date,
                fact.status_name,
                fact.subject_name,
                fact.admin_name,
                fact.rejection_reason,
                technician.tecnico_nombre AS technician_name,
                fact.created_at
            FROM {self._mart_schema}.fact_financial_credit_note_requests fact
            INNER JOIN {self._mart_schema}.dim_financial_technician technician
                ON technician.technician_key = fact.technician_key
            INNER JOIN {self._mart_schema}.dim_financial_date request_date
                ON request_date.date_key = fact.request_date_key
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
        """

        items = self._fetch_paginated_items(
            count_query=count_query,
            data_query=data_query,
            params=params,
            limit=limit,
            offset=offset,
            item_builder=lambda row: CreditNoteRequestListItem(
                extraction_id=row["extraction_id"],
                request_number=row["request_number"],
                order_id=row["order_id"],
                order_number=row["order_number"],
                request_date=row["request_date"],
                status_name=row["status_name"],
                subject_name=row["subject_name"],
                admin_name=row["admin_name"],
                rejection_reason=row["rejection_reason"],
                technician_name=row["technician_name"],
                created_at=row["created_at"],
            ),
        )
        return items

    def list_order_prices(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        service_name: str | None = None,
        order_number: str | None = None,
        standard_service_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedResult[OrderPriceListItem]:
        """Lista ingresos por orden con filtros opcionales."""

        logger.info(
            "Ejecutando consulta de ingresos por orden | schema=%s | sort_by=%s | sort_dir=%s",
            self._mart_schema,
            sort_by,
            sort_dir,
        )

        filters: list[str] = []
        params: list[object] = []

        if order_id is not None:
            filters.append("fact.order_id = %s")
            params.append(order_id)
        if service_name:
            filters.append("fact.service_name ILIKE %s")
            params.append(f"%{service_name}%")
        if order_number:
            filters.append("fact.order_number ILIKE %s")
            params.append(f"%{order_number}%")
        if standard_service_name:
            filters.append("fact.standard_service_name ILIKE %s")
            params.append(f"%{standard_service_name}%")
        if date_from:
            filters.append("created_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("created_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._ORDER_PRICE_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="fact.created_at DESC NULLS LAST, fact.order_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_financial_order_prices fact
            LEFT JOIN {self._mart_schema}.dim_financial_date created_date
                ON created_date.date_key = fact.created_date_key
            {where_sql}
        """

        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.order_id,
                fact.order_number,
                fact.service_name,
                fact.standard_service_name,
                fact.amount,
                fact.standard_amount,
                fact.created_at
            FROM {self._mart_schema}.fact_financial_order_prices fact
            LEFT JOIN {self._mart_schema}.dim_financial_date created_date
                ON created_date.date_key = fact.created_date_key
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
        """

        items = self._fetch_paginated_items(
            count_query=count_query,
            data_query=data_query,
            params=params,
            limit=limit,
            offset=offset,
            item_builder=lambda row: OrderPriceListItem(
                extraction_id=row["extraction_id"],
                order_id=row["order_id"],
                order_number=row["order_number"],
                service_name=row["service_name"],
                standard_service_name=row["standard_service_name"],
                amount=Decimal(row["amount"]),
                standard_amount=Decimal(row["standard_amount"]) if row["standard_amount"] is not None else None,
                created_at=row["created_at"],
            ),
        )
        return items

    def list_notifications(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        order_number: str | None = None,
        nc_id: int | None = None,
        notification_type: str | None = None,
        is_read: bool | None = None,
        technician_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedResult[NotificationListItem]:
        """Lista notificaciones financieras con filtros opcionales."""

        logger.info(
            "Ejecutando consulta de notificaciones financieras | schema=%s | sort_by=%s | sort_dir=%s",
            self._mart_schema,
            sort_by,
            sort_dir,
        )

        filters: list[str] = []
        params: list[object] = []

        if order_id is not None:
            filters.append("fact.order_id = %s")
            params.append(order_id)
        if order_number:
            filters.append("fact.order_number ILIKE %s")
            params.append(f"%{order_number}%")
        if nc_id is not None:
            filters.append("fact.nc_id = %s")
            params.append(nc_id)
        if notification_type:
            filters.append("fact.notification_type = %s")
            params.append(notification_type)
        if is_read is not None:
            filters.append("fact.is_read = %s")
            params.append(is_read)
        if technician_name:
            filters.append("technician.tecnico_nombre ILIKE %s")
            params.append(f"%{technician_name}%")
        if date_from:
            filters.append("notification_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("notification_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._NOTIFICATION_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="fact.created_at DESC, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_financial_credit_note_notifications fact
            INNER JOIN {self._mart_schema}.dim_financial_technician technician
                ON technician.technician_key = fact.technician_key
            INNER JOIN {self._mart_schema}.dim_financial_date notification_date
                ON notification_date.date_key = fact.notification_date_key
            {where_sql}
        """

        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.order_id,
                fact.order_number,
                fact.nc_id,
                fact.notification_type,
                fact.is_read,
                technician.tecnico_nombre AS technician_name,
                fact.created_at
            FROM {self._mart_schema}.fact_financial_credit_note_notifications fact
            INNER JOIN {self._mart_schema}.dim_financial_technician technician
                ON technician.technician_key = fact.technician_key
            INNER JOIN {self._mart_schema}.dim_financial_date notification_date
                ON notification_date.date_key = fact.notification_date_key
            {where_sql}
            ORDER BY {order_sql}
            LIMIT %s OFFSET %s
        """

        items = self._fetch_paginated_items(
            count_query=count_query,
            data_query=data_query,
            params=params,
            limit=limit,
            offset=offset,
            item_builder=lambda row: NotificationListItem(
                extraction_id=row["extraction_id"],
                order_id=row["order_id"],
                order_number=row["order_number"],
                nc_id=row["nc_id"],
                notification_type=row["notification_type"],
                is_read=row["is_read"],
                technician_name=row["technician_name"],
                created_at=row["created_at"],
            ),
        )
        return items

    def _fetch_paginated_items(
        self,
        count_query: str,
        data_query: str,
        params: list[object],
        limit: int,
        offset: int,
        item_builder,
    ):
        """Ejecuta una consulta paginada y mapea los resultados a DTOs."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(count_query, params)
                total = int(cursor.fetchone()["total"])
                cursor.execute(data_query, [*params, limit, offset])
                rows = cursor.fetchall()

        logger.info(
            "Consulta paginada completada | total=%s | devueltos=%s | limit=%s | offset=%s",
            total,
            len(rows),
            limit,
            offset,
        )

        return PaginatedResult(
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
