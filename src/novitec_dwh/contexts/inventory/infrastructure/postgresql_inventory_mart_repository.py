"""Repositorio PostgreSQL para construir el mart de inventario."""

from importlib.resources import files
import logging

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger(__name__)


class PostgreSQLInventoryMartRepository:
    """Construye dimensiones y hechos de inventario a partir del staging."""

    def __init__(
        self,
        connection_factory: PostgreSQLConnectionFactory,
        staging_schema: str,
        mart_schema: str,
    ) -> None:
        """Recibe dependencias de conexion y nombres de schema."""

        self._connection_factory = connection_factory
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema

    def prepare_schema(self) -> None:
        """Crea el schema analitico y sus tablas si no existen."""

        ddl_template = (
            files("novitec_dwh.contexts.inventory.infrastructure.sql")
            .joinpath("inventory_mart.sql")
            .read_text(encoding="utf-8")
        )
        ddl_statement = ddl_template.replace("{mart_schema}", self._mart_schema)

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ddl_statement)
            connection.commit()

    def prepare_extraction(self, extraction_id: str) -> None:
        """Elimina datos previos de la misma corrida para soportar reprocesos."""

        tables = [
            "etl_inventory_quality_audit",
            "fact_inventory_purchase_lists",
            "fact_inventory_spare_part_requests",
            "fact_inventory_order_spare_parts",
            "fact_inventory_spare_parts",
        ]
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                for table_name in tables:
                    cursor.execute(
                        f"DELETE FROM {self._mart_schema}.{table_name} WHERE extraction_id = %s",
                        (extraction_id,),
                    )
            connection.commit()

    def resolve_latest_extraction_id(self) -> str:
        """Obtiene la corrida de inventario mas reciente disponible en staging."""

        sql = f"SELECT MAX(extraction_id) FROM {self._staging_schema}.stg_inventory_spare_parts"

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()

        extraction_id = row[0] if row else None
        if not extraction_id:
            raise ValueError(
                "No se encontro ninguna corrida de inventario en staging para construir el mart."
            )

        return str(extraction_id)

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga todas las fechas necesarias para la corrida del mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_inventory_date (
                date_key, full_date, year_number, quarter_number, month_number,
                month_name, day_number, iso_week_number, day_of_week_number,
                day_of_week_name, is_weekend
            )
            SELECT DISTINCT
                TO_CHAR(source_date, 'YYYYMMDD')::INTEGER,
                source_date,
                EXTRACT(YEAR FROM source_date)::INTEGER,
                EXTRACT(QUARTER FROM source_date)::INTEGER,
                EXTRACT(MONTH FROM source_date)::INTEGER,
                TO_CHAR(source_date, 'TMMonth'),
                EXTRACT(DAY FROM source_date)::INTEGER,
                EXTRACT(WEEK FROM source_date)::INTEGER,
                EXTRACT(ISODOW FROM source_date)::INTEGER,
                TO_CHAR(source_date, 'TMDay'),
                CASE WHEN EXTRACT(ISODOW FROM source_date) IN (6, 7) THEN TRUE ELSE FALSE END
            FROM (
                SELECT fecha_solicitud AS source_date
                FROM {self._staging_schema}.stg_inventory_spare_part_requests
                WHERE extraction_id = %s

                UNION
                SELECT fecha_gestion::DATE
                FROM {self._staging_schema}.stg_inventory_spare_part_requests
                WHERE extraction_id = %s
                  AND fecha_gestion IS NOT NULL

                UNION
                SELECT fecha_creacion
                FROM {self._staging_schema}.stg_inventory_purchase_lists
                WHERE extraction_id = %s

                UNION
                SELECT created_at::DATE
                FROM {self._staging_schema}.stg_inventory_purchase_lists
                WHERE extraction_id = %s

                UNION
                SELECT fecha::DATE
                FROM {self._staging_schema}.stg_inventory_order_spare_parts
                WHERE extraction_id = %s
                  AND fecha IS NOT NULL

                UNION
                SELECT creado_en::DATE
                FROM {self._staging_schema}.stg_inventory_spare_parts
                WHERE extraction_id = %s
                  AND creado_en IS NOT NULL

                UNION
                SELECT modificado_en::DATE
                FROM {self._staging_schema}.stg_inventory_spare_parts
                WHERE extraction_id = %s
                  AND modificado_en IS NOT NULL
            ) dates
            ON CONFLICT (date_key) DO NOTHING
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                    ),
                )
            connection.commit()

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de tecnicos usada por el mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_inventory_technician (
                tecnico_id, tecnico_nombre, first_extraction_id, last_extraction_id
            )
            SELECT
                tecnico_id,
                tecnico_nombre_normalizado,
                %s,
                %s
            FROM (
                SELECT DISTINCT ON (tecnico_id)
                    tecnico_id,
                    COALESCE(
                        NULLIF(REGEXP_REPLACE(BTRIM(tecnico_nombre), '\\s+', ' ', 'g'), ''),
                        CONCAT('Tecnico ', tecnico_id::TEXT)
                    ) AS tecnico_nombre_normalizado
                FROM {self._staging_schema}.stg_inventory_spare_part_requests
                WHERE extraction_id = %s
                ORDER BY tecnico_id, tecnico_nombre_normalizado
            ) src
            ON CONFLICT (tecnico_id) DO UPDATE
            SET tecnico_nombre = EXCLUDED.tecnico_nombre,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_spare_part_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de repuestos usada por el mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_inventory_spare_part (
                source_id, spare_part_code, part_number, spare_part_name, brand_source_id,
                device_type_source_id, first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(codigo), '\\s+', ' ', 'g'), ''), CONCAT('REP-', source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(nro_parte), '\\s+', ' ', 'g'), ''),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombre), '\\s+', ' ', 'g'), ''), CONCAT('Repuesto ', source_id::TEXT)),
                CASE
                    WHEN NULLIF(REGEXP_REPLACE(BTRIM(marca_id), '\\s+', ' ', 'g'), '') ~ '^[0-9]+$'
                        THEN NULLIF(REGEXP_REPLACE(BTRIM(marca_id), '\\s+', ' ', 'g'), '')::INTEGER
                    ELSE NULL
                END,
                CASE
                    WHEN NULLIF(REGEXP_REPLACE(BTRIM(tipo_dispositivo_id), '\\s+', ' ', 'g'), '') ~ '^[0-9]+$'
                        THEN NULLIF(REGEXP_REPLACE(BTRIM(tipo_dispositivo_id), '\\s+', ' ', 'g'), '')::INTEGER
                    ELSE NULL
                END,
                %s,
                %s
            FROM {self._staging_schema}.stg_inventory_spare_parts
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET spare_part_code = EXCLUDED.spare_part_code,
                part_number = EXCLUDED.part_number,
                spare_part_name = EXCLUDED.spare_part_name,
                brand_source_id = EXCLUDED.brand_source_id,
                device_type_source_id = EXCLUDED.device_type_source_id,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_spare_part_fact(self, extraction_id: str) -> int:
        """Carga el hecho principal de repuestos."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_inventory_spare_parts (
                extraction_id, source_id, spare_part_key, created_date_key,
                updated_date_key, current_stock, current_cost, warehouse_number,
                has_stock, has_part_number, spare_part_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                dim.spare_part_key,
                created_date.date_key,
                updated_date.date_key,
                src.stock,
                src.costo,
                src.bodega,
                CASE WHEN src.stock > 0 THEN TRUE ELSE FALSE END,
                CASE WHEN src.part_number_normalizado IS NOT NULL THEN TRUE ELSE FALSE END,
                1
            FROM (
                SELECT
                    extraction_id,
                    source_id,
                    stock,
                    costo,
                    bodega,
                    creado_en,
                    modificado_en,
                    NULLIF(REGEXP_REPLACE(BTRIM(nro_parte), '\\s+', ' ', 'g'), '') AS part_number_normalizado
                FROM {self._staging_schema}.stg_inventory_spare_parts
                WHERE extraction_id = %s
            ) src
            INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.source_id = src.source_id
            LEFT JOIN {self._mart_schema}.dim_inventory_date created_date
                ON created_date.full_date = src.creado_en::DATE
            LEFT JOIN {self._mart_schema}.dim_inventory_date updated_date
                ON updated_date.full_date = src.modificado_en::DATE
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET spare_part_key = EXCLUDED.spare_part_key,
                created_date_key = EXCLUDED.created_date_key,
                updated_date_key = EXCLUDED.updated_date_key,
                current_stock = EXCLUDED.current_stock,
                current_cost = EXCLUDED.current_cost,
                warehouse_number = EXCLUDED.warehouse_number,
                has_stock = EXCLUDED.has_stock,
                has_part_number = EXCLUDED.has_part_number,
                spare_part_count = EXCLUDED.spare_part_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_inventory_spare_parts")

    def load_order_consumption_fact(self, extraction_id: str) -> int:
        """Carga el hecho de consumo de repuestos por orden."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_inventory_order_spare_parts (
                extraction_id, source_id, order_id, spare_part_key, movement_date_key,
                installer_user_id, quantity, has_installer_user, consumption_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.orden_id,
                dim.spare_part_key,
                movement_date.date_key,
                src.usuario_id,
                src.cantidad,
                CASE WHEN src.usuario_id IS NOT NULL THEN TRUE ELSE FALSE END,
                1
            FROM {self._staging_schema}.stg_inventory_order_spare_parts src
            INNER JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.source_id = src.repuesto_id
            LEFT JOIN {self._mart_schema}.dim_inventory_date movement_date
                ON movement_date.full_date = src.fecha::DATE
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET order_id = EXCLUDED.order_id,
                spare_part_key = EXCLUDED.spare_part_key,
                movement_date_key = EXCLUDED.movement_date_key,
                installer_user_id = EXCLUDED.installer_user_id,
                quantity = EXCLUDED.quantity,
                has_installer_user = EXCLUDED.has_installer_user,
                consumption_count = EXCLUDED.consumption_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_inventory_order_spare_parts")

    def load_spare_part_request_fact(self, extraction_id: str) -> int:
        """Carga el hecho de solicitudes de repuesto."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_inventory_spare_part_requests (
                extraction_id, source_id, request_number, order_id, technician_key,
                spare_part_key, request_date_key, management_date_key, approved_by,
                request_status, quantity, is_approved, is_rejected, is_pending,
                has_purchase_link, request_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.nro_solicitud,
                src.orden_id,
                tech.technician_key,
                dim.spare_part_key,
                request_date.date_key,
                management_date.date_key,
                src.aprobado_por_normalizado,
                src.estado_normalizado,
                src.cantidad,
                CASE WHEN src.estado_normalizado = 'Aprobada' THEN TRUE ELSE FALSE END,
                CASE WHEN src.estado_normalizado = 'Rechazada' THEN TRUE ELSE FALSE END,
                CASE WHEN src.estado_normalizado = 'Pendiente' THEN TRUE ELSE FALSE END,
                CASE WHEN src.link_compra_normalizado IS NOT NULL THEN TRUE ELSE FALSE END,
                1
            FROM (
                SELECT
                    extraction_id,
                    source_id,
                    nro_solicitud,
                    orden_id,
                    tecnico_id,
                    repuesto_id,
                    fecha_solicitud,
                    fecha_gestion,
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(aprobado_por), '\\s+', ' ', 'g'), ''), NULL) AS aprobado_por_normalizado,
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(link_compra), '\\s+', ' ', 'g'), ''), NULL) AS link_compra_normalizado,
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(estado), '\\s+', ' ', 'g'), ''), 'Pendiente') AS estado_normalizado,
                    cantidad
                FROM {self._staging_schema}.stg_inventory_spare_part_requests
                WHERE extraction_id = %s
            ) src
            INNER JOIN {self._mart_schema}.dim_inventory_technician tech
                ON tech.tecnico_id = src.tecnico_id
            LEFT JOIN {self._mart_schema}.dim_inventory_spare_part dim
                ON dim.source_id = src.repuesto_id
            INNER JOIN {self._mart_schema}.dim_inventory_date request_date
                ON request_date.full_date = src.fecha_solicitud
            LEFT JOIN {self._mart_schema}.dim_inventory_date management_date
                ON management_date.full_date = src.fecha_gestion::DATE
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET request_number = EXCLUDED.request_number,
                order_id = EXCLUDED.order_id,
                technician_key = EXCLUDED.technician_key,
                spare_part_key = EXCLUDED.spare_part_key,
                request_date_key = EXCLUDED.request_date_key,
                management_date_key = EXCLUDED.management_date_key,
                approved_by = EXCLUDED.approved_by,
                request_status = EXCLUDED.request_status,
                quantity = EXCLUDED.quantity,
                is_approved = EXCLUDED.is_approved,
                is_rejected = EXCLUDED.is_rejected,
                is_pending = EXCLUDED.is_pending,
                has_purchase_link = EXCLUDED.has_purchase_link,
                request_count = EXCLUDED.request_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_inventory_spare_part_requests")

    def load_purchase_list_fact(self, extraction_id: str) -> int:
        """Carga el hecho de listas de compra."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_inventory_purchase_lists (
                extraction_id, source_id, list_number, creator_user_id, creation_date_key,
                created_date_key, list_status, has_observation, purchase_list_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.nro_lista,
                src.creado_por_id,
                creation_date.date_key,
                created_date.date_key,
                src.estado_normalizado,
                CASE WHEN src.observacion_normalizada IS NOT NULL THEN TRUE ELSE FALSE END,
                1
            FROM (
                SELECT
                    extraction_id,
                    source_id,
                    nro_lista,
                    creado_por_id,
                    fecha_creacion,
                    created_at,
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(estado), '\\s+', ' ', 'g'), ''), 'Pendiente') AS estado_normalizado,
                    NULLIF(REGEXP_REPLACE(BTRIM(observacion), '\\s+', ' ', 'g'), '') AS observacion_normalizada
                FROM {self._staging_schema}.stg_inventory_purchase_lists
                WHERE extraction_id = %s
            ) src
            INNER JOIN {self._mart_schema}.dim_inventory_date creation_date
                ON creation_date.full_date = src.fecha_creacion
            INNER JOIN {self._mart_schema}.dim_inventory_date created_date
                ON created_date.full_date = src.created_at::DATE
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET list_number = EXCLUDED.list_number,
                creator_user_id = EXCLUDED.creator_user_id,
                creation_date_key = EXCLUDED.creation_date_key,
                created_date_key = EXCLUDED.created_date_key,
                list_status = EXCLUDED.list_status,
                has_observation = EXCLUDED.has_observation,
                purchase_list_count = EXCLUDED.purchase_list_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_inventory_purchase_lists")

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Calcula hallazgos de calidad y los registra por corrida."""

        sql = f"""
            INSERT INTO {self._mart_schema}.etl_inventory_quality_audit (
                extraction_id, entity_name, rule_name, severity, affected_rows
            )
            SELECT
                %s,
                audit.entity_name,
                audit.rule_name,
                audit.severity,
                audit.affected_rows
            FROM (
                SELECT 'spare_parts', 'repuesto_sin_codigo', 'critical', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_inventory_spare_parts
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(codigo), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'spare_parts', 'repuesto_con_stock_negativo', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_inventory_spare_parts
                WHERE extraction_id = %s
                  AND stock < 0

                UNION ALL
                SELECT 'spare_parts', 'repuesto_con_costo_no_positivo', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_inventory_spare_parts
                WHERE extraction_id = %s
                  AND costo <= 0

                UNION ALL
                SELECT 'order_spare_parts', 'consumo_sin_usuario_instalador', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_inventory_order_spare_parts
                WHERE extraction_id = %s
                  AND usuario_id IS NULL

                UNION ALL
                SELECT 'spare_part_requests', 'solicitud_aprobada_sin_aprobador', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_inventory_spare_part_requests
                WHERE extraction_id = %s
                  AND estado = 'Aprobada'
                  AND NULLIF(REGEXP_REPLACE(BTRIM(aprobado_por), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'spare_part_requests', 'solicitud_sin_repuesto_vinculado', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_inventory_spare_part_requests
                WHERE extraction_id = %s
                  AND repuesto_id IS NULL

                UNION ALL
                SELECT 'purchase_lists', 'lista_compra_sin_creador', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_inventory_purchase_lists
                WHERE extraction_id = %s
                  AND creado_por_id IS NULL
            ) audit(entity_name, rule_name, severity, affected_rows)
            ON CONFLICT (extraction_id, entity_name, rule_name) DO UPDATE
            SET severity = EXCLUDED.severity,
                affected_rows = EXCLUDED.affected_rows,
                created_at = NOW()
        """
        summary_sql = f"""
            SELECT COUNT(*)::INTEGER, COALESCE(SUM(affected_rows), 0)::INTEGER
            FROM {self._mart_schema}.etl_inventory_quality_audit
            WHERE extraction_id = %s
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                        extraction_id,
                    ),
                )
                cursor.execute(summary_sql, (extraction_id,))
                row = cursor.fetchone()
            connection.commit()

        logger.info(
            "Auditoria de calidad de inventario actualizada | extraction_id=%s | reglas=%s | hallazgos=%s",
            extraction_id,
            row[0],
            row[1],
        )
        return int(row[0]), int(row[1])

    def _execute_fact_load(self, sql: str, extraction_id: str, table_name: str) -> int:
        """Ejecuta una carga de hecho y devuelve el total final de la corrida."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id,))
                cursor.execute(
                    f"SELECT COUNT(*) FROM {self._mart_schema}.{table_name} WHERE extraction_id = %s",
                    (extraction_id,),
                )
                total = int(cursor.fetchone()[0])
            connection.commit()

        logger.info(
            "Hecho de inventario cargado en mart | tabla=%s | extraction_id=%s | total=%s",
            table_name,
            extraction_id,
            total,
        )
        return total
