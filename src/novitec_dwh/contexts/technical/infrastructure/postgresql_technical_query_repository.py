"""Repositorio PostgreSQL de consultas sobre el mart tecnico."""

import logging
from datetime import date

from psycopg.rows import dict_row

from novitec_dwh.contexts.technical.application.dto_query import (
    PaginatedTechnicalResult,
    TechnicalEquipmentAccessListItem,
    TechnicalEquipmentListItem,
    TechnicalReportListItem,
    TechnicalReportPhotoListItem,
    TechnicalSummary,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger("novitec_dwh.technical.repository")


class PostgreSQLTechnicalQueryRepository:
    """Consulta el mart tecnico para exponer datos por API."""

    _REPORT_SORT_FIELDS = {
        "report_date": "report_date.full_date",
        "created_at": "fact.created_at",
        "order_id": "fact.order_id",
        "technician_name": "tech.tecnico_nombre",
        "equipment_status": "fact.equipment_status",
    }
    _PHOTO_SORT_FIELDS = {
        "report_date": "report_date.full_date",
        "technician_name": "tech.tecnico_nombre",
        "photo_order": "fact.photo_order",
        "file_name": "fact.file_name",
    }
    _EQUIPMENT_SORT_FIELDS = {
        "billing_date": "billing_date.full_date",
        "service_name": "service_type.service_name",
        "brand_name": "brand.brand_name",
        "device_type_name": "fact.device_type_name",
        "device_model": "fact.device_model",
    }
    _ACCESS_SORT_FIELDS = {
        "equipment_source_id": "fact.equipment_source_id",
        "access_count": "fact.access_count",
        "is_pattern": "fact.is_pattern",
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
        technician_name: str | None = None,
        equipment_status: str | None = None,
        service_name: str | None = None,
        brand_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> TechnicalSummary:
        """Obtiene el resumen principal del dominio tecnico."""

        logger.info("Ejecutando consulta de resumen tecnico | schema=%s", self._mart_schema)

        report_filters: list[str] = []
        report_params: list[object] = []
        equipment_filters: list[str] = []
        equipment_params: list[object] = []
        access_filters: list[str] = []
        access_params: list[object] = []

        if technician_name:
            report_filters.append("tech.tecnico_nombre ILIKE %s")
            report_params.append(f"%{technician_name}%")
        if equipment_status:
            report_filters.append("fact.equipment_status = %s")
            report_params.append(equipment_status)
        if date_from:
            report_filters.append("report_date.full_date >= %s")
            report_params.append(date_from)
        if date_to:
            report_filters.append("report_date.full_date <= %s")
            report_params.append(date_to)
        if service_name:
            equipment_filters.append("service_type.service_name ILIKE %s")
            equipment_params.append(f"%{service_name}%")
        if brand_name:
            equipment_filters.append("brand.brand_name ILIKE %s")
            equipment_params.append(f"%{brand_name}%")
        if date_from:
            equipment_filters.append("billing_date.full_date >= %s")
            equipment_params.append(date_from)
        if date_to:
            equipment_filters.append("billing_date.full_date <= %s")
            equipment_params.append(date_to)
        if technician_name:
            access_filters.append("report_tech.tecnico_nombre ILIKE %s")
            access_params.append(f"%{technician_name}%")

        report_where_sql = f"WHERE {' AND '.join(report_filters)}" if report_filters else ""
        equipment_where_sql = f"WHERE {' AND '.join(equipment_filters)}" if equipment_filters else ""
        access_where_sql = f"WHERE {' AND '.join(access_filters)}" if access_filters else ""

        query = f"""
            WITH latest_extraction AS (
                SELECT MAX(extraction_id) AS extraction_id
                FROM {self._mart_schema}.fact_technical_reports
            ),
            report_summary AS (
                SELECT
                    COUNT(*) AS total_informes,
                    COALESCE(SUM(CASE WHEN fact.is_equipment_operational THEN 1 ELSE 0 END), 0) AS informes_equipo_operativo,
                    COALESCE(SUM(CASE WHEN fact.has_budget_json THEN 1 ELSE 0 END), 0) AS informes_con_presupuesto
                FROM {self._mart_schema}.fact_technical_reports fact
                INNER JOIN {self._mart_schema}.dim_technical_technician tech
                    ON tech.technician_key = fact.technician_key
                INNER JOIN {self._mart_schema}.dim_technical_date report_date
                    ON report_date.date_key = fact.report_date_key
                {report_where_sql}
            ),
            photo_summary AS (
                SELECT COUNT(*) AS total_fotos_informes
                FROM {self._mart_schema}.fact_technical_report_photos fact
                INNER JOIN {self._mart_schema}.dim_technical_technician tech
                    ON tech.technician_key = fact.technician_key
                INNER JOIN {self._mart_schema}.dim_technical_date report_date
                    ON report_date.date_key = fact.report_date_key
                {report_where_sql}
            ),
            equipment_summary AS (
                SELECT
                    COUNT(*) AS total_equipos,
                    COALESCE(SUM(CASE WHEN fact.has_password_provided THEN 1 ELSE 0 END), 0) AS equipos_con_contrasena
                FROM {self._mart_schema}.fact_technical_equipment fact
                LEFT JOIN {self._mart_schema}.dim_technical_service_type service_type
                    ON service_type.service_type_key = fact.service_type_key
                LEFT JOIN {self._mart_schema}.dim_technical_brand brand
                    ON brand.brand_key = fact.brand_key
                LEFT JOIN {self._mart_schema}.dim_technical_date billing_date
                    ON billing_date.date_key = fact.billing_date_key
                {equipment_where_sql}
            ),
            access_summary AS (
                SELECT COUNT(*) AS total_accesos_equipos
                FROM {self._mart_schema}.fact_technical_equipment_access fact
                LEFT JOIN {self._mart_schema}.fact_technical_reports report
                    ON report.extraction_id = fact.extraction_id
                   AND report.order_id = fact.equipment_source_id
                LEFT JOIN {self._mart_schema}.dim_technical_technician report_tech
                    ON report_tech.technician_key = report.technician_key
                {access_where_sql}
            )
            SELECT
                latest_extraction.extraction_id,
                report_summary.total_informes,
                report_summary.informes_equipo_operativo,
                report_summary.informes_con_presupuesto,
                photo_summary.total_fotos_informes,
                equipment_summary.total_equipos,
                equipment_summary.equipos_con_contrasena,
                access_summary.total_accesos_equipos
            FROM latest_extraction
            CROSS JOIN report_summary
            CROSS JOIN photo_summary
            CROSS JOIN equipment_summary
            CROSS JOIN access_summary
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, [*report_params, *report_params, *equipment_params, *access_params])
                row = cursor.fetchone()

        logger.info(
            "Consulta de resumen tecnico completada | extraction_id=%s | informes=%s | fotos=%s | equipos=%s | accesos=%s",
            row["extraction_id"],
            row["total_informes"],
            row["total_fotos_informes"],
            row["total_equipos"],
            row["total_accesos_equipos"],
        )

        return TechnicalSummary(
            extraction_id=row["extraction_id"],
            total_informes=int(row["total_informes"]),
            informes_equipo_operativo=int(row["informes_equipo_operativo"]),
            informes_con_presupuesto=int(row["informes_con_presupuesto"]),
            total_fotos_informes=int(row["total_fotos_informes"]),
            total_equipos=int(row["total_equipos"]),
            equipos_con_contrasena=int(row["equipos_con_contrasena"]),
            total_accesos_equipos=int(row["total_accesos_equipos"]),
        )

    def list_reports(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        technician_name: str | None = None,
        equipment_status: str | None = None,
        has_budget_json: bool | None = None,
        is_equipment_operational: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "report_date",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalReportListItem]:
        """Lista informes tecnicos con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if order_id is not None:
            filters.append("fact.order_id = %s")
            params.append(order_id)
        if technician_name:
            filters.append("tech.tecnico_nombre ILIKE %s")
            params.append(f"%{technician_name}%")
        if equipment_status:
            filters.append("fact.equipment_status = %s")
            params.append(equipment_status)
        if has_budget_json is not None:
            filters.append("fact.has_budget_json = %s")
            params.append(has_budget_json)
        if is_equipment_operational is not None:
            filters.append("fact.is_equipment_operational = %s")
            params.append(is_equipment_operational)
        if date_from:
            filters.append("report_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("report_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._REPORT_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="report_date.full_date DESC, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_technical_reports fact
            INNER JOIN {self._mart_schema}.dim_technical_technician tech
                ON tech.technician_key = fact.technician_key
            INNER JOIN {self._mart_schema}.dim_technical_date report_date
                ON report_date.date_key = fact.report_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.order_id,
                report_date.full_date AS report_date,
                fact.created_at,
                tech.tecnico_nombre AS technician_name,
                fact.equipment_status,
                fact.has_background,
                fact.has_process,
                fact.has_conclusion,
                fact.has_recommendations,
                fact.has_budget_json,
                fact.is_equipment_operational,
                fact.background_length,
                fact.process_length,
                fact.conclusion_length,
                fact.recommendation_length
            FROM {self._mart_schema}.fact_technical_reports fact
            INNER JOIN {self._mart_schema}.dim_technical_technician tech
                ON tech.technician_key = fact.technician_key
            INNER JOIN {self._mart_schema}.dim_technical_date report_date
                ON report_date.date_key = fact.report_date_key
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
            item_builder=lambda row: TechnicalReportListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                order_id=row["order_id"],
                report_date=row["report_date"],
                created_at=row["created_at"],
                technician_name=row["technician_name"],
                equipment_status=row["equipment_status"],
                has_background=row["has_background"],
                has_process=row["has_process"],
                has_conclusion=row["has_conclusion"],
                has_recommendations=row["has_recommendations"],
                has_budget_json=row["has_budget_json"],
                is_equipment_operational=row["is_equipment_operational"],
                background_length=row["background_length"],
                process_length=row["process_length"],
                conclusion_length=row["conclusion_length"],
                recommendation_length=row["recommendation_length"],
            ),
        )

    def list_report_photos(
        self,
        limit: int,
        offset: int,
        report_source_id: int | None = None,
        technician_name: str | None = None,
        has_binary_evidence: bool | None = None,
        mime_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "report_date",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalReportPhotoListItem]:
        """Lista fotos de informes con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if report_source_id is not None:
            filters.append("fact.report_source_id = %s")
            params.append(report_source_id)
        if technician_name:
            filters.append("tech.tecnico_nombre ILIKE %s")
            params.append(f"%{technician_name}%")
        if has_binary_evidence is not None:
            filters.append("fact.has_binary_evidence = %s")
            params.append(has_binary_evidence)
        if mime_type:
            filters.append("fact.mime_type ILIKE %s")
            params.append(f"%{mime_type}%")
        if date_from:
            filters.append("report_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("report_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._PHOTO_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="report_date.full_date DESC NULLS LAST, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_technical_report_photos fact
            LEFT JOIN {self._mart_schema}.dim_technical_technician tech
                ON tech.technician_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_technical_date report_date
                ON report_date.date_key = fact.report_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.report_source_id,
                report_date.full_date AS report_date,
                tech.tecnico_nombre AS technician_name,
                fact.photo_order,
                fact.file_name,
                fact.mime_type,
                fact.caption,
                fact.has_binary_evidence,
                fact.has_file_name,
                fact.is_jpeg
            FROM {self._mart_schema}.fact_technical_report_photos fact
            LEFT JOIN {self._mart_schema}.dim_technical_technician tech
                ON tech.technician_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_technical_date report_date
                ON report_date.date_key = fact.report_date_key
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
            item_builder=lambda row: TechnicalReportPhotoListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                report_source_id=row["report_source_id"],
                report_date=row["report_date"],
                technician_name=row["technician_name"],
                photo_order=row["photo_order"],
                file_name=row["file_name"],
                mime_type=row["mime_type"],
                caption=row["caption"],
                has_binary_evidence=row["has_binary_evidence"],
                has_file_name=row["has_file_name"],
                is_jpeg=row["is_jpeg"],
            ),
        )

    def list_equipment(
        self,
        limit: int,
        offset: int,
        service_name: str | None = None,
        brand_name: str | None = None,
        device_type_name: str | None = None,
        inventory_product_code: str | None = None,
        has_password_provided: bool | None = None,
        has_failure_description: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "billing_date",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalEquipmentListItem]:
        """Lista equipos tecnicos con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if service_name:
            filters.append("service_type.service_name ILIKE %s")
            params.append(f"%{service_name}%")
        if brand_name:
            filters.append("brand.brand_name ILIKE %s")
            params.append(f"%{brand_name}%")
        if device_type_name:
            filters.append("fact.device_type_name ILIKE %s")
            params.append(f"%{device_type_name}%")
        if inventory_product_code:
            filters.append("fact.inventory_product_code ILIKE %s")
            params.append(f"%{inventory_product_code}%")
        if has_password_provided is not None:
            filters.append("fact.has_password_provided = %s")
            params.append(has_password_provided)
        if has_failure_description is not None:
            filters.append("fact.has_failure_description = %s")
            params.append(has_failure_description)
        if date_from:
            filters.append("billing_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("billing_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._EQUIPMENT_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="billing_date.full_date DESC NULLS LAST, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_technical_equipment fact
            LEFT JOIN {self._mart_schema}.dim_technical_service_type service_type
                ON service_type.service_type_key = fact.service_type_key
            LEFT JOIN {self._mart_schema}.dim_technical_brand brand
                ON brand.brand_key = fact.brand_key
            LEFT JOIN {self._mart_schema}.dim_technical_date billing_date
                ON billing_date.date_key = fact.billing_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                billing_date.full_date AS billing_date,
                service_type.service_name,
                brand.brand_name,
                fact.device_type_name,
                fact.device_model,
                fact.serial_number,
                fact.inventory_product_code,
                fact.has_password_provided,
                fact.has_failure_description,
                fact.has_observation,
                fact.has_billing_date
            FROM {self._mart_schema}.fact_technical_equipment fact
            LEFT JOIN {self._mart_schema}.dim_technical_service_type service_type
                ON service_type.service_type_key = fact.service_type_key
            LEFT JOIN {self._mart_schema}.dim_technical_brand brand
                ON brand.brand_key = fact.brand_key
            LEFT JOIN {self._mart_schema}.dim_technical_date billing_date
                ON billing_date.date_key = fact.billing_date_key
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
            item_builder=lambda row: TechnicalEquipmentListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                billing_date=row["billing_date"],
                service_name=row["service_name"],
                brand_name=row["brand_name"],
                device_type_name=row["device_type_name"],
                device_model=row["device_model"],
                serial_number=row["serial_number"],
                inventory_product_code=row["inventory_product_code"],
                has_password_provided=row["has_password_provided"],
                has_failure_description=row["has_failure_description"],
                has_observation=row["has_observation"],
                has_billing_date=row["has_billing_date"],
            ),
        )

    def list_equipment_access(
        self,
        limit: int,
        offset: int,
        equipment_source_id: int | None = None,
        has_user_name: bool | None = None,
        is_pattern: bool | None = None,
        sort_by: str = "equipment_source_id",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalEquipmentAccessListItem]:
        """Lista accesos de equipo con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if equipment_source_id is not None:
            filters.append("fact.equipment_source_id = %s")
            params.append(equipment_source_id)
        if has_user_name is not None:
            filters.append("fact.has_user_name = %s")
            params.append(has_user_name)
        if is_pattern is not None:
            filters.append("fact.is_pattern = %s")
            params.append(is_pattern)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._ACCESS_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="fact.equipment_source_id DESC, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_technical_equipment_access fact
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.equipment_source_id,
                fact.has_user_name,
                fact.is_pattern,
                fact.access_count
            FROM {self._mart_schema}.fact_technical_equipment_access fact
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
            item_builder=lambda row: TechnicalEquipmentAccessListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                equipment_source_id=row["equipment_source_id"],
                has_user_name=row["has_user_name"],
                is_pattern=row["is_pattern"],
                access_count=row["access_count"],
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
    ) -> PaginatedTechnicalResult:
        """Ejecuta una consulta paginada y mapea los resultados a DTOs."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(count_query, params)
                total = int(cursor.fetchone()["total"])
                cursor.execute(data_query, [*params, limit, offset])
                rows = cursor.fetchall()

        logger.info(
            "Consulta tecnica paginada completada | total=%s | devueltos=%s | limit=%s | offset=%s",
            total,
            len(rows),
            limit,
            offset,
        )
        return PaginatedTechnicalResult(
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
