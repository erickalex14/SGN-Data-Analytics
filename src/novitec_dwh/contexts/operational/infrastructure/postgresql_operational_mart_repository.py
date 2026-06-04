"""Repositorio PostgreSQL para construir el mart operativo."""

from importlib.resources import files
import logging

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger(__name__)


class PostgreSQLOperationalMartRepository:
    """Construye dimensiones y hechos operativos a partir del staging."""

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
            files("novitec_dwh.contexts.operational.infrastructure.sql")
            .joinpath("operational_mart.sql")
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
            "etl_operational_quality_audit",
            "fact_operational_company_order_assignments",
            "fact_operational_preorders",
            "fact_operational_orders",
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
        """Obtiene la corrida operativa mas reciente disponible en staging."""

        sql = f"""
            SELECT MAX(extraction_id)
            FROM {self._staging_schema}.stg_operational_order_view
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()

        extraction_id = row[0] if row else None
        if not extraction_id:
            raise ValueError(
                "No se encontro ninguna corrida operativa en staging para construir el mart."
            )

        return str(extraction_id)

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga todas las fechas necesarias para la corrida del mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_operational_date (
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
                SELECT fecha_de_ingreso::DATE AS source_date
                FROM {self._staging_schema}.stg_operational_order_view
                WHERE extraction_id = %s AND fecha_de_ingreso IS NOT NULL
                UNION
                SELECT fecha_prometido
                FROM {self._staging_schema}.stg_operational_order_view
                WHERE extraction_id = %s AND fecha_prometido IS NOT NULL
                UNION
                SELECT fecha_entrega::DATE
                FROM {self._staging_schema}.stg_operational_order_view
                WHERE extraction_id = %s AND fecha_entrega IS NOT NULL
                UNION
                SELECT fecha_de_ingreso::DATE
                FROM {self._staging_schema}.stg_operational_personal_orders
                WHERE extraction_id = %s AND fecha_de_ingreso IS NOT NULL
                UNION
                SELECT fecha_facturacion
                FROM {self._staging_schema}.stg_operational_personal_orders
                WHERE extraction_id = %s AND fecha_facturacion IS NOT NULL
                UNION
                SELECT fecha_registro::DATE
                FROM {self._staging_schema}.stg_operational_preorders
                WHERE extraction_id = %s AND fecha_registro IS NOT NULL
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
                    ),
                )
            connection.commit()

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de tecnicos usada por el mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_operational_technician (
                tecnico_id, tecnico_nombre, first_extraction_id, last_extraction_id
            )
            SELECT
                src.tecnico_id,
                src.tecnico_nombre,
                %s,
                %s
            FROM (
                SELECT DISTINCT ON (candidate.tecnico_id)
                    candidate.tecnico_id,
                    candidate.tecnico_nombre
                FROM (
                    SELECT
                        tecnico_id,
                        COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(tecnico), '\\s+', ' ', 'g'), ''), 'No identificado') AS tecnico_nombre,
                        1 AS source_priority
                    FROM {self._staging_schema}.stg_operational_order_view
                    WHERE extraction_id = %s
                      AND tecnico_id IS NOT NULL

                    UNION ALL

                    SELECT
                        tecnico_id,
                        CONCAT('Tecnico ', tecnico_id::TEXT) AS tecnico_nombre,
                        2 AS source_priority
                    FROM {self._staging_schema}.stg_operational_order_company_technicians
                    WHERE extraction_id = %s
                ) candidate
                ORDER BY candidate.tecnico_id, candidate.source_priority, candidate.tecnico_nombre
            ) src
            ON CONFLICT (tecnico_id) DO UPDATE
            SET tecnico_nombre = EXCLUDED.tecnico_nombre,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_branch_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de sucursales usada por el mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_operational_branch (
                sucursal_id, sucursal_nombre, first_extraction_id, last_extraction_id
            )
            SELECT
                src.sucursal_id,
                src.sucursal_nombre,
                %s,
                %s
            FROM (
                SELECT DISTINCT ON (sucursal_id)
                    sucursal_id,
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(sucursal), '\\s+', ' ', 'g'), ''), CONCAT('Sucursal ', sucursal_id::TEXT)) AS sucursal_nombre
                FROM {self._staging_schema}.stg_operational_order_view
                WHERE extraction_id = %s
                  AND sucursal_id IS NOT NULL
                ORDER BY sucursal_id, COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(sucursal), '\\s+', ' ', 'g'), ''), CONCAT('Sucursal ', sucursal_id::TEXT))
            ) src
            ON CONFLICT (sucursal_id) DO UPDATE
            SET sucursal_nombre = EXCLUDED.sucursal_nombre,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_order_fact(self, extraction_id: str) -> int:
        """Carga el hecho principal de ordenes operativas."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_operational_orders (
                extraction_id, source_order_id, order_type, order_number,
                intake_date_key, promised_date_key, delivery_date_key, billing_date_key,
                technician_key, branch_key, order_status, replacement_status,
                warranty_status, intake_reason, customer_type, customer_name,
                device_type, device_brand, has_invoice, is_delivered, is_open,
                is_warranty, order_count, cycle_days, promised_cycle_days,
                delay_days, worked_hours, hourly_rate
            )
            SELECT
                ov.extraction_id,
                ov.orden_id,
                ov.tipo_orden,
                COALESCE(NULLIF(BTRIM(ov.nro_orden), ''), CONCAT('SIN-ORDEN-', ov.orden_id::TEXT)),
                intake_date.date_key,
                promised_date.date_key,
                delivery_date.date_key,
                billing_date.date_key,
                tech.technician_key,
                branch.branch_key,
                NULLIF(REGEXP_REPLACE(BTRIM(ov.estado_orden), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(ov.estado_repuesto), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(ov.estado_garantia), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(ov.motivo_ingreso), '\\s+', ' ', 'g'), ''),
                CASE WHEN ov.tipo_orden = 'empresa' THEN 'B2B' ELSE 'B2C' END,
                NULLIF(REGEXP_REPLACE(BTRIM(ov.cliente), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(ov.tipo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(ov.marca), '\\s+', ' ', 'g'), ''),
                CASE
                    WHEN NULLIF(BTRIM(ov.nro_factura), '') IS NOT NULL OR NULLIF(BTRIM(ov.nro_factura_2), '') IS NOT NULL THEN TRUE
                    ELSE FALSE
                END,
                CASE WHEN ov.fecha_entrega IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE
                    WHEN ov.fecha_entrega IS NULL AND COALESCE(ov.estado_orden, '') NOT IN ('Entregada', 'Finalizada', 'Cerrada') THEN TRUE
                    ELSE FALSE
                END,
                CASE WHEN NULLIF(BTRIM(ov.estado_garantia), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                1,
                CASE
                    WHEN ov.fecha_de_ingreso IS NOT NULL AND ov.fecha_entrega IS NOT NULL
                        THEN GREATEST((ov.fecha_entrega::DATE - ov.fecha_de_ingreso::DATE), 0)
                    ELSE NULL
                END,
                CASE
                    WHEN ov.fecha_de_ingreso IS NOT NULL AND ov.fecha_prometido IS NOT NULL
                        THEN GREATEST((ov.fecha_prometido - ov.fecha_de_ingreso::DATE), 0)
                    ELSE NULL
                END,
                CASE
                    WHEN ov.fecha_prometido IS NOT NULL AND ov.fecha_entrega IS NOT NULL
                        THEN GREATEST((ov.fecha_entrega::DATE - ov.fecha_prometido), 0)
                    ELSE NULL
                END,
                co.horas_trabajadas,
                co.valor_hora
            FROM {self._staging_schema}.stg_operational_order_view ov
            LEFT JOIN {self._staging_schema}.stg_operational_company_orders co
                ON co.extraction_id = ov.extraction_id
               AND co.source_id = ov.orden_id
               AND ov.tipo_orden = 'empresa'
            LEFT JOIN {self._staging_schema}.stg_operational_personal_orders po
                ON po.extraction_id = ov.extraction_id
               AND po.source_id = ov.orden_id
               AND ov.tipo_orden = 'personal'
            LEFT JOIN {self._mart_schema}.dim_operational_date intake_date
                ON intake_date.full_date = ov.fecha_de_ingreso::DATE
            LEFT JOIN {self._mart_schema}.dim_operational_date promised_date
                ON promised_date.full_date = ov.fecha_prometido
            LEFT JOIN {self._mart_schema}.dim_operational_date delivery_date
                ON delivery_date.full_date = ov.fecha_entrega::DATE
            LEFT JOIN {self._mart_schema}.dim_operational_date billing_date
                ON billing_date.full_date = po.fecha_facturacion
            LEFT JOIN {self._mart_schema}.dim_operational_technician tech
                ON tech.tecnico_id = ov.tecnico_id
            LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                ON branch.sucursal_id = ov.sucursal_id
            WHERE ov.extraction_id = %s
            ON CONFLICT (extraction_id, source_order_id, order_type) DO UPDATE
            SET order_number = EXCLUDED.order_number,
                intake_date_key = EXCLUDED.intake_date_key,
                promised_date_key = EXCLUDED.promised_date_key,
                delivery_date_key = EXCLUDED.delivery_date_key,
                billing_date_key = EXCLUDED.billing_date_key,
                technician_key = EXCLUDED.technician_key,
                branch_key = EXCLUDED.branch_key,
                order_status = EXCLUDED.order_status,
                replacement_status = EXCLUDED.replacement_status,
                warranty_status = EXCLUDED.warranty_status,
                intake_reason = EXCLUDED.intake_reason,
                customer_type = EXCLUDED.customer_type,
                customer_name = EXCLUDED.customer_name,
                device_type = EXCLUDED.device_type,
                device_brand = EXCLUDED.device_brand,
                has_invoice = EXCLUDED.has_invoice,
                is_delivered = EXCLUDED.is_delivered,
                is_open = EXCLUDED.is_open,
                is_warranty = EXCLUDED.is_warranty,
                order_count = EXCLUDED.order_count,
                cycle_days = EXCLUDED.cycle_days,
                promised_cycle_days = EXCLUDED.promised_cycle_days,
                delay_days = EXCLUDED.delay_days,
                worked_hours = EXCLUDED.worked_hours,
                hourly_rate = EXCLUDED.hourly_rate
        """
        return self._execute_fact_load(sql, extraction_id, "fact_operational_orders")

    def load_preorder_fact(self, extraction_id: str) -> int:
        """Carga el hecho de preordenes."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_operational_preorders (
                extraction_id, source_id, linked_order_id, registration_date_key,
                branch_key, preorder_number, preorder_status, customer_name,
                city_name, has_invoice, has_photos, preorder_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.orden_id,
                registration_date.date_key,
                branch.branch_key,
                COALESCE(NULLIF(BTRIM(src.nro_preorden), ''), CONCAT('SIN-PREORDEN-', src.source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(src.estado), '\\s+', ' ', 'g'), ''),
                CONCAT(src.nombres, ' ', src.apellidos),
                NULLIF(REGEXP_REPLACE(BTRIM(src.ciudad_procedencia), '\\s+', ' ', 'g'), ''),
                CASE WHEN NULLIF(BTRIM(src.nro_factura), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE
                    WHEN src.foto_1 IS NOT NULL OR src.foto_2 IS NOT NULL OR src.foto_3 IS NOT NULL OR src.foto_4 IS NOT NULL THEN TRUE
                    ELSE FALSE
                END,
                1
            FROM {self._staging_schema}.stg_operational_preorders src
            LEFT JOIN {self._mart_schema}.dim_operational_date registration_date
                ON registration_date.full_date = src.fecha_registro::DATE
            LEFT JOIN {self._mart_schema}.dim_operational_branch branch
                ON branch.sucursal_id = src.sucursal_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET linked_order_id = EXCLUDED.linked_order_id,
                registration_date_key = EXCLUDED.registration_date_key,
                branch_key = EXCLUDED.branch_key,
                preorder_number = EXCLUDED.preorder_number,
                preorder_status = EXCLUDED.preorder_status,
                customer_name = EXCLUDED.customer_name,
                city_name = EXCLUDED.city_name,
                has_invoice = EXCLUDED.has_invoice,
                has_photos = EXCLUDED.has_photos,
                preorder_count = EXCLUDED.preorder_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_operational_preorders")

    def load_company_order_assignment_fact(self, extraction_id: str) -> int:
        """Carga el hecho de asignaciones tecnico-orden empresarial."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_operational_company_order_assignments (
                extraction_id, source_id, source_order_id, technician_key, assignment_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.orden_empresa_id,
                tech.technician_key,
                1
            FROM {self._staging_schema}.stg_operational_order_company_technicians src
            INNER JOIN {self._mart_schema}.dim_operational_technician tech
                ON tech.tecnico_id = src.tecnico_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET source_order_id = EXCLUDED.source_order_id,
                technician_key = EXCLUDED.technician_key,
                assignment_count = EXCLUDED.assignment_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_operational_company_order_assignments")

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Calcula hallazgos de calidad y los registra por corrida."""

        sql = f"""
            INSERT INTO {self._mart_schema}.etl_operational_quality_audit (
                extraction_id, entity_name, rule_name, severity, affected_rows
            )
            SELECT
                %s,
                audit.entity_name,
                audit.rule_name,
                audit.severity,
                audit.affected_rows
            FROM (
                SELECT 'orders', 'orden_sin_tecnico', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_operational_order_view
                WHERE extraction_id = %s AND tecnico_id IS NULL

                UNION ALL
                SELECT 'orders', 'orden_sin_fecha_ingreso', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_operational_order_view
                WHERE extraction_id = %s AND fecha_de_ingreso IS NULL

                UNION ALL
                SELECT 'orders', 'orden_entregada_sin_fecha_entrega', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_operational_order_view
                WHERE extraction_id = %s
                  AND UPPER(COALESCE(estado_orden, '')) IN ('ENTREGADA', 'FINALIZADA', 'CERRADA')
                  AND fecha_entrega IS NULL

                UNION ALL
                SELECT 'company_orders', 'orden_empresa_sin_horas', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_operational_company_orders
                WHERE extraction_id = %s
                  AND horas_trabajadas IS NULL

                UNION ALL
                SELECT 'preorders', 'preorden_sin_estado', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_operational_preorders
                WHERE extraction_id = %s
                  AND NULLIF(BTRIM(estado), '') IS NULL

                UNION ALL
                SELECT 'preorders', 'preorden_sin_cliente', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_operational_preorders
                WHERE extraction_id = %s
                  AND (NULLIF(BTRIM(nombres), '') IS NULL OR NULLIF(BTRIM(apellidos), '') IS NULL)
            ) audit(entity_name, rule_name, severity, affected_rows)
            ON CONFLICT (extraction_id, entity_name, rule_name) DO UPDATE
            SET severity = EXCLUDED.severity,
                affected_rows = EXCLUDED.affected_rows,
                created_at = NOW()
        """
        summary_sql = f"""
            SELECT COUNT(*)::INTEGER, COALESCE(SUM(affected_rows), 0)::INTEGER
            FROM {self._mart_schema}.etl_operational_quality_audit
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
                    ),
                )
                cursor.execute(summary_sql, (extraction_id,))
                row = cursor.fetchone()
            connection.commit()

        logger.info(
            "Auditoria de calidad operativa actualizada | extraction_id=%s | reglas=%s | hallazgos=%s",
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
            "Hecho operativo cargado en mart | tabla=%s | extraction_id=%s | total=%s",
            table_name,
            extraction_id,
            total,
        )
        return total
