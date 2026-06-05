"""Repositorio PostgreSQL de consultas sobre el mart de inventario."""

import logging
from datetime import date

from psycopg.rows import dict_row

from novitec_dwh.contexts.inventory.application.dto_query import (
    InventoryOrderSparePartListItem,
    InventoryPurchaseListListItem,
    InventorySparePartListItem,
    InventorySparePartRequestListItem,
    InventorySummary,
    PaginatedInventoryResult,
)
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger("novitec_dwh.inventory.repository")


class PostgreSQLInventoryQueryRepository:
    """Consulta el mart de inventario para exponer datos por API."""

    _SPARE_PART_SORT_FIELDS = {
        "updated_date": "updated_date.full_date",
        "created_date": "created_date.full_date",
        "spare_part_code": "dim.spare_part_code",
        "spare_part_name": "dim.spare_part_name",
        "current_stock": "fact.current_stock",
        "current_cost": "fact.current_cost",
    }
    _ORDER_CONSUMPTION_SORT_FIELDS = {
        "movement_date": "movement_date.full_date",
        "order_id": "fact.order_id",
        "quantity": "fact.quantity",
        "spare_part_code": "dim.spare_part_code",
    }
    _REQUEST_SORT_FIELDS = {
        "request_date": "request_date.full_date",
        "management_date": "management_date.full_date",
        "quantity": "fact.quantity",
        "technician_name": "tech.tecnico_nombre",
        "request_status": "fact.request_status",
    }
    _PURCHASE_LIST_SORT_FIELDS = {
        "creation_date": "creation_date.full_date",
        "created_date": "created_date.full_date",
        "list_number": "fact.list_number",
        "list_status": "fact.list_status",
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
        spare_part_code: str | None = None,
        request_status: str | None = None,
        warehouse_number: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> InventorySummary:
        """Obtiene el resumen principal del dominio de inventario."""

        logger.info("Ejecutando consulta de resumen de inventario | schema=%s", self._mart_schema)

        spare_part_filters: list[str] = []
        spare_part_params: list[object] = []
        consumption_filters: list[str] = []
        consumption_params: list[object] = []
        request_filters: list[str] = []
        request_params: list[object] = []
        purchase_list_filters: list[str] = []
        purchase_list_params: list[object] = []

        if spare_part_code:
            spare_part_filters.append("dim.spare_part_code ILIKE %s")
            spare_part_params.append(f"%{spare_part_code}%")
            consumption_filters.append("dim.spare_part_code ILIKE %s")
            consumption_params.append(f"%{spare_part_code}%")
            request_filters.append("dim.spare_part_code ILIKE %s")
            request_params.append(f"%{spare_part_code}%")
        if warehouse_number is not None:
            spare_part_filters.append("fact.warehouse_number = %s")
            spare_part_params.append(warehouse_number)
        if date_from:
            spare_part_filters.append("COALESCE(updated_date.full_date, created_date.full_date) >= %s")
            spare_part_params.append(date_from)
            consumption_filters.append("movement_date.full_date >= %s")
            consumption_params.append(date_from)
            request_filters.append("request_date.full_date >= %s")
            request_params.append(date_from)
            purchase_list_filters.append("creation_date.full_date >= %s")
            purchase_list_params.append(date_from)
        if date_to:
            spare_part_filters.append("COALESCE(updated_date.full_date, created_date.full_date) <= %s")
            spare_part_params.append(date_to)
            consumption_filters.append("movement_date.full_date <= %s")
            consumption_params.append(date_to)
            request_filters.append("request_date.full_date <= %s")
            request_params.append(date_to)
            purchase_list_filters.append("creation_date.full_date <= %s")
            purchase_list_params.append(date_to)
        if technician_name:
            request_filters.append("tech.tecnico_nombre ILIKE %s")
            request_params.append(f"%{technician_name}%")
        if request_status:
            request_filters.append("fact.request_status = %s")
            request_params.append(request_status)

        spare_part_where_sql = f"WHERE {' AND '.join(spare_part_filters)}" if spare_part_filters else ""
        consumption_where_sql = f"WHERE {' AND '.join(consumption_filters)}" if consumption_filters else ""
        request_where_sql = f"WHERE {' AND '.join(request_filters)}" if request_filters else ""
        purchase_list_where_sql = (
            f"WHERE {' AND '.join(purchase_list_filters)}" if purchase_list_filters else ""
        )

        query = f"""
            WITH latest_extraction AS (
                SELECT MAX(extraction_id) AS extraction_id
                FROM {self._mart_schema}.fact_inventory_spare_parts
            ),
            spare_part_summary AS (
                SELECT
                    COUNT(*) AS total_repuestos,
                    COALESCE(SUM(CASE WHEN fact.has_stock THEN 1 ELSE 0 END), 0) AS repuestos_con_stock,
                    COALESCE(SUM(fact.current_stock), 0) AS stock_total_unidades,
                    COALESCE(SUM(fact.current_stock * fact.current_cost), 0) AS costo_total_inventario
                FROM {self._mart_schema}.fact_inventory_spare_parts fact
                INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                    ON dim.spare_part_key = fact.spare_part_key
                LEFT JOIN {self._mart_schema}.dim_inventory_date created_date
                    ON created_date.date_key = fact.created_date_key
                LEFT JOIN {self._mart_schema}.dim_inventory_date updated_date
                    ON updated_date.date_key = fact.updated_date_key
                {spare_part_where_sql}
            ),
            consumption_summary AS (
                SELECT
                    COUNT(*) AS total_consumos_orden,
                    COALESCE(SUM(fact.quantity), 0) AS cantidad_total_consumida
                FROM {self._mart_schema}.fact_inventory_order_spare_parts fact
                INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                    ON dim.spare_part_key = fact.spare_part_key
                LEFT JOIN {self._mart_schema}.dim_inventory_date movement_date
                    ON movement_date.date_key = fact.movement_date_key
                {consumption_where_sql}
            ),
            request_summary AS (
                SELECT
                    COUNT(*) AS total_solicitudes_repuesto,
                    COALESCE(SUM(CASE WHEN fact.is_approved THEN 1 ELSE 0 END), 0) AS solicitudes_aprobadas,
                    COALESCE(SUM(CASE WHEN fact.is_rejected THEN 1 ELSE 0 END), 0) AS solicitudes_rechazadas,
                    COALESCE(SUM(CASE WHEN fact.is_pending THEN 1 ELSE 0 END), 0) AS solicitudes_pendientes
                FROM {self._mart_schema}.fact_inventory_spare_part_requests fact
                INNER JOIN {self._mart_schema}.dim_inventory_technician tech
                    ON tech.technician_key = fact.technician_key
                LEFT JOIN {self._mart_schema}.dim_inventory_spare_part dim
                    ON dim.spare_part_key = fact.spare_part_key
                INNER JOIN {self._mart_schema}.dim_inventory_date request_date
                    ON request_date.date_key = fact.request_date_key
                {request_where_sql}
            ),
            purchase_list_summary AS (
                SELECT COUNT(*) AS total_listas_compra
                FROM {self._mart_schema}.fact_inventory_purchase_lists fact
                INNER JOIN {self._mart_schema}.dim_inventory_date creation_date
                    ON creation_date.date_key = fact.creation_date_key
                {purchase_list_where_sql}
            )
            SELECT
                latest_extraction.extraction_id,
                spare_part_summary.total_repuestos,
                spare_part_summary.repuestos_con_stock,
                spare_part_summary.stock_total_unidades,
                spare_part_summary.costo_total_inventario,
                consumption_summary.total_consumos_orden,
                consumption_summary.cantidad_total_consumida,
                request_summary.total_solicitudes_repuesto,
                request_summary.solicitudes_aprobadas,
                request_summary.solicitudes_rechazadas,
                request_summary.solicitudes_pendientes,
                purchase_list_summary.total_listas_compra
            FROM latest_extraction
            CROSS JOIN spare_part_summary
            CROSS JOIN consumption_summary
            CROSS JOIN request_summary
            CROSS JOIN purchase_list_summary
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    query,
                    [
                        *spare_part_params,
                        *consumption_params,
                        *request_params,
                        *purchase_list_params,
                    ],
                )
                row = cursor.fetchone()

        logger.info(
            "Consulta de resumen de inventario completada | extraction_id=%s | repuestos=%s | consumos=%s | solicitudes=%s | listas=%s",
            row["extraction_id"],
            row["total_repuestos"],
            row["total_consumos_orden"],
            row["total_solicitudes_repuesto"],
            row["total_listas_compra"],
        )

        return InventorySummary(
            extraction_id=row["extraction_id"],
            total_repuestos=int(row["total_repuestos"]),
            repuestos_con_stock=int(row["repuestos_con_stock"]),
            stock_total_unidades=int(row["stock_total_unidades"]),
            costo_total_inventario=row["costo_total_inventario"],
            total_consumos_orden=int(row["total_consumos_orden"]),
            cantidad_total_consumida=int(row["cantidad_total_consumida"]),
            total_solicitudes_repuesto=int(row["total_solicitudes_repuesto"]),
            solicitudes_aprobadas=int(row["solicitudes_aprobadas"]),
            solicitudes_rechazadas=int(row["solicitudes_rechazadas"]),
            solicitudes_pendientes=int(row["solicitudes_pendientes"]),
            total_listas_compra=int(row["total_listas_compra"]),
        )

    def list_spare_parts(
        self,
        limit: int,
        offset: int,
        spare_part_code: str | None = None,
        part_number: str | None = None,
        spare_part_name: str | None = None,
        warehouse_number: int | None = None,
        has_stock: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "updated_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventorySparePartListItem]:
        """Lista repuestos con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if spare_part_code:
            filters.append("dim.spare_part_code ILIKE %s")
            params.append(f"%{spare_part_code}%")
        if part_number:
            filters.append("dim.part_number ILIKE %s")
            params.append(f"%{part_number}%")
        if spare_part_name:
            filters.append("dim.spare_part_name ILIKE %s")
            params.append(f"%{spare_part_name}%")
        if warehouse_number is not None:
            filters.append("fact.warehouse_number = %s")
            params.append(warehouse_number)
        if has_stock is not None:
            filters.append("fact.has_stock = %s")
            params.append(has_stock)
        if date_from:
            filters.append("COALESCE(updated_date.full_date, created_date.full_date) >= %s")
            params.append(date_from)
        if date_to:
            filters.append("COALESCE(updated_date.full_date, created_date.full_date) <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._SPARE_PART_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="updated_date.full_date DESC NULLS LAST, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_inventory_spare_parts fact
            INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.spare_part_key = fact.spare_part_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date created_date
                ON created_date.date_key = fact.created_date_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date updated_date
                ON updated_date.date_key = fact.updated_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                dim.spare_part_code,
                dim.part_number,
                dim.spare_part_name,
                created_date.full_date AS created_date,
                updated_date.full_date AS updated_date,
                fact.current_stock,
                fact.current_cost,
                fact.warehouse_number,
                fact.has_stock,
                fact.has_part_number
            FROM {self._mart_schema}.fact_inventory_spare_parts fact
            INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.spare_part_key = fact.spare_part_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date created_date
                ON created_date.date_key = fact.created_date_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date updated_date
                ON updated_date.date_key = fact.updated_date_key
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
            item_builder=lambda row: InventorySparePartListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                spare_part_code=row["spare_part_code"],
                part_number=row["part_number"],
                spare_part_name=row["spare_part_name"],
                created_date=row["created_date"],
                updated_date=row["updated_date"],
                current_stock=row["current_stock"],
                current_cost=row["current_cost"],
                warehouse_number=row["warehouse_number"],
                has_stock=row["has_stock"],
                has_part_number=row["has_part_number"],
            ),
        )

    def list_order_spare_parts(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        spare_part_code: str | None = None,
        spare_part_name: str | None = None,
        installer_user_id: int | None = None,
        has_installer_user: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "movement_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventoryOrderSparePartListItem]:
        """Lista consumos de repuestos por orden con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if order_id is not None:
            filters.append("fact.order_id = %s")
            params.append(order_id)
        if spare_part_code:
            filters.append("dim.spare_part_code ILIKE %s")
            params.append(f"%{spare_part_code}%")
        if spare_part_name:
            filters.append("dim.spare_part_name ILIKE %s")
            params.append(f"%{spare_part_name}%")
        if installer_user_id is not None:
            filters.append("fact.installer_user_id = %s")
            params.append(installer_user_id)
        if has_installer_user is not None:
            filters.append("fact.has_installer_user = %s")
            params.append(has_installer_user)
        if date_from:
            filters.append("movement_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("movement_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._ORDER_CONSUMPTION_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="movement_date.full_date DESC NULLS LAST, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_inventory_order_spare_parts fact
            INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.spare_part_key = fact.spare_part_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date movement_date
                ON movement_date.date_key = fact.movement_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.order_id,
                dim.spare_part_code,
                dim.spare_part_name,
                movement_date.full_date AS movement_date,
                fact.installer_user_id,
                fact.quantity,
                fact.has_installer_user
            FROM {self._mart_schema}.fact_inventory_order_spare_parts fact
            INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.spare_part_key = fact.spare_part_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date movement_date
                ON movement_date.date_key = fact.movement_date_key
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
            item_builder=lambda row: InventoryOrderSparePartListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                order_id=row["order_id"],
                spare_part_code=row["spare_part_code"],
                spare_part_name=row["spare_part_name"],
                movement_date=row["movement_date"],
                installer_user_id=row["installer_user_id"],
                quantity=row["quantity"],
                has_installer_user=row["has_installer_user"],
            ),
        )

    def list_spare_part_requests(
        self,
        limit: int,
        offset: int,
        request_number: str | None = None,
        order_id: int | None = None,
        technician_name: str | None = None,
        spare_part_code: str | None = None,
        request_status: str | None = None,
        approved_by: str | None = None,
        has_purchase_link: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "request_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventorySparePartRequestListItem]:
        """Lista solicitudes de repuesto con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if request_number:
            filters.append("fact.request_number ILIKE %s")
            params.append(f"%{request_number}%")
        if order_id is not None:
            filters.append("fact.order_id = %s")
            params.append(order_id)
        if technician_name:
            filters.append("tech.tecnico_nombre ILIKE %s")
            params.append(f"%{technician_name}%")
        if spare_part_code:
            filters.append("dim.spare_part_code ILIKE %s")
            params.append(f"%{spare_part_code}%")
        if request_status:
            filters.append("fact.request_status = %s")
            params.append(request_status)
        if approved_by:
            filters.append("fact.approved_by ILIKE %s")
            params.append(f"%{approved_by}%")
        if has_purchase_link is not None:
            filters.append("fact.has_purchase_link = %s")
            params.append(has_purchase_link)
        if date_from:
            filters.append("request_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("request_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._REQUEST_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="request_date.full_date DESC, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_inventory_spare_part_requests fact
            INNER JOIN {self._mart_schema}.dim_inventory_technician tech
                ON tech.technician_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.spare_part_key = fact.spare_part_key
            INNER JOIN {self._mart_schema}.dim_inventory_date request_date
                ON request_date.date_key = fact.request_date_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date management_date
                ON management_date.date_key = fact.management_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.request_number,
                fact.order_id,
                tech.tecnico_nombre AS technician_name,
                dim.spare_part_code,
                dim.spare_part_name,
                request_date.full_date AS request_date,
                management_date.full_date AS management_date,
                fact.approved_by,
                fact.request_status,
                fact.quantity,
                fact.is_approved,
                fact.is_rejected,
                fact.is_pending,
                fact.has_purchase_link
            FROM {self._mart_schema}.fact_inventory_spare_part_requests fact
            INNER JOIN {self._mart_schema}.dim_inventory_technician tech
                ON tech.technician_key = fact.technician_key
            LEFT JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.spare_part_key = fact.spare_part_key
            INNER JOIN {self._mart_schema}.dim_inventory_date request_date
                ON request_date.date_key = fact.request_date_key
            LEFT JOIN {self._mart_schema}.dim_inventory_date management_date
                ON management_date.date_key = fact.management_date_key
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
            item_builder=lambda row: InventorySparePartRequestListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                request_number=row["request_number"],
                order_id=row["order_id"],
                technician_name=row["technician_name"],
                spare_part_code=row["spare_part_code"],
                spare_part_name=row["spare_part_name"],
                request_date=row["request_date"],
                management_date=row["management_date"],
                approved_by=row["approved_by"],
                request_status=row["request_status"],
                quantity=row["quantity"],
                is_approved=row["is_approved"],
                is_rejected=row["is_rejected"],
                is_pending=row["is_pending"],
                has_purchase_link=row["has_purchase_link"],
            ),
        )

    def list_purchase_lists(
        self,
        limit: int,
        offset: int,
        list_number: str | None = None,
        creator_user_id: int | None = None,
        list_status: str | None = None,
        has_observation: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "creation_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventoryPurchaseListListItem]:
        """Lista listas de compra con filtros opcionales."""

        filters: list[str] = []
        params: list[object] = []

        if list_number:
            filters.append("fact.list_number ILIKE %s")
            params.append(f"%{list_number}%")
        if creator_user_id is not None:
            filters.append("fact.creator_user_id = %s")
            params.append(creator_user_id)
        if list_status:
            filters.append("fact.list_status = %s")
            params.append(list_status)
        if has_observation is not None:
            filters.append("fact.has_observation = %s")
            params.append(has_observation)
        if date_from:
            filters.append("creation_date.full_date >= %s")
            params.append(date_from)
        if date_to:
            filters.append("creation_date.full_date <= %s")
            params.append(date_to)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""
        order_sql = self._build_order_by_sql(
            allowed_fields=self._PURCHASE_LIST_SORT_FIELDS,
            sort_by=sort_by,
            sort_dir=sort_dir,
            fallback_expression="creation_date.full_date DESC, fact.source_id DESC",
        )

        count_query = f"""
            SELECT COUNT(*) AS total
            FROM {self._mart_schema}.fact_inventory_purchase_lists fact
            INNER JOIN {self._mart_schema}.dim_inventory_date creation_date
                ON creation_date.date_key = fact.creation_date_key
            INNER JOIN {self._mart_schema}.dim_inventory_date created_date
                ON created_date.date_key = fact.created_date_key
            {where_sql}
        """
        data_query = f"""
            SELECT
                fact.extraction_id,
                fact.source_id,
                fact.list_number,
                fact.creator_user_id,
                creation_date.full_date AS creation_date,
                created_date.full_date AS created_date,
                fact.list_status,
                fact.has_observation
            FROM {self._mart_schema}.fact_inventory_purchase_lists fact
            INNER JOIN {self._mart_schema}.dim_inventory_date creation_date
                ON creation_date.date_key = fact.creation_date_key
            INNER JOIN {self._mart_schema}.dim_inventory_date created_date
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
            item_builder=lambda row: InventoryPurchaseListListItem(
                extraction_id=row["extraction_id"],
                source_id=row["source_id"],
                list_number=row["list_number"],
                creator_user_id=row["creator_user_id"],
                creation_date=row["creation_date"],
                created_date=row["created_date"],
                list_status=row["list_status"],
                has_observation=row["has_observation"],
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
    ) -> PaginatedInventoryResult:
        """Ejecuta una consulta paginada y mapea los resultados a DTOs."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor(row_factory=dict_row) as cursor:
                cursor.execute(count_query, params)
                total = int(cursor.fetchone()["total"])
                cursor.execute(data_query, [*params, limit, offset])
                rows = cursor.fetchall()

        logger.info(
            "Consulta de inventario paginada completada | total=%s | devueltos=%s | limit=%s | offset=%s",
            total,
            len(rows),
            limit,
            offset,
        )
        return PaginatedInventoryResult(
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
