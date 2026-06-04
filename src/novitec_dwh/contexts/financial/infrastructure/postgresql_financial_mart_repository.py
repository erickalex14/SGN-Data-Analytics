"""Repositorio PostgreSQL para construir el mart financiero."""

from importlib.resources import files
import logging

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger(__name__)


class PostgreSQLFinancialMartRepository:
    """Construye dimensiones y hechos financieros a partir del staging."""

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
            files("novitec_dwh.contexts.financial.infrastructure.sql")
            .joinpath("financial_mart.sql")
            .read_text(encoding="utf-8")
        )
        ddl_statement = ddl_template.replace("{mart_schema}", self._mart_schema)

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ddl_statement)
            connection.commit()

    def prepare_extraction(self, extraction_id: str) -> None:
        """Elimina datos previos de la misma corrida para soportar reprocesos."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    DELETE FROM {self._mart_schema}.etl_financial_quality_audit
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
                cursor.execute(
                    f"""
                    DELETE FROM {self._mart_schema}.fact_financial_credit_note_notifications
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
                cursor.execute(
                    f"""
                    DELETE FROM {self._mart_schema}.fact_financial_order_prices
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
                cursor.execute(
                    f"""
                    DELETE FROM {self._mart_schema}.fact_financial_credit_note_requests
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
            connection.commit()

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga todas las fechas necesarias para la corrida del mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_financial_date (
                date_key,
                full_date,
                year_number,
                quarter_number,
                month_number,
                month_name,
                day_number,
                iso_week_number,
                day_of_week_number,
                day_of_week_name,
                is_weekend
            )
            SELECT DISTINCT
                TO_CHAR(source_date, 'YYYYMMDD')::INTEGER AS date_key,
                source_date AS full_date,
                EXTRACT(YEAR FROM source_date)::INTEGER AS year_number,
                EXTRACT(QUARTER FROM source_date)::INTEGER AS quarter_number,
                EXTRACT(MONTH FROM source_date)::INTEGER AS month_number,
                TO_CHAR(source_date, 'TMMonth') AS month_name,
                EXTRACT(DAY FROM source_date)::INTEGER AS day_number,
                EXTRACT(WEEK FROM source_date)::INTEGER AS iso_week_number,
                EXTRACT(ISODOW FROM source_date)::INTEGER AS day_of_week_number,
                TO_CHAR(source_date, 'TMDay') AS day_of_week_name,
                CASE WHEN EXTRACT(ISODOW FROM source_date) IN (6, 7) THEN TRUE ELSE FALSE END AS is_weekend
            FROM (
                SELECT fecha_solicitud AS source_date
                FROM {self._staging_schema}.stg_financial_credit_note_requests
                WHERE extraction_id = %s

                UNION

                SELECT created_at::DATE AS source_date
                FROM {self._staging_schema}.stg_financial_credit_note_requests
                WHERE extraction_id = %s
                  AND created_at IS NOT NULL

                UNION

                SELECT creado_en::DATE AS source_date
                FROM {self._staging_schema}.stg_financial_order_prices
                WHERE extraction_id = %s
                  AND creado_en IS NOT NULL

                UNION

                SELECT created_at::DATE AS source_date
                FROM {self._staging_schema}.stg_financial_credit_note_notifications
                WHERE extraction_id = %s
            ) dates
            ON CONFLICT (date_key) DO NOTHING
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de tecnicos usada por el mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_financial_technician (
                tecnico_id,
                tecnico_nombre,
                first_extraction_id,
                last_extraction_id
            )
            SELECT
                src.tecnico_id,
                src.tecnico_nombre_normalizado,
                %s,
                %s
            FROM (
                SELECT DISTINCT
                    tecnico_id,
                    COALESCE(
                        NULLIF(REGEXP_REPLACE(BTRIM(tecnico_nombre), '\s+', ' ', 'g'), ''),
                        'No identificado'
                    ) AS tecnico_nombre_normalizado
                FROM {self._staging_schema}.stg_financial_credit_note_requests
                WHERE extraction_id = %s

                UNION

                SELECT DISTINCT
                    usuario_id AS tecnico_id,
                    COALESCE(
                        NULLIF(REGEXP_REPLACE(BTRIM(usuario_nombre), '\s+', ' ', 'g'), ''),
                        'No identificado'
                    ) AS tecnico_nombre_normalizado
                FROM {self._staging_schema}.stg_financial_credit_note_notifications
                WHERE extraction_id = %s
            ) src
            ON CONFLICT (tecnico_id) DO UPDATE
            SET tecnico_nombre = EXCLUDED.tecnico_nombre,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    sql,
                    (extraction_id, extraction_id, extraction_id, extraction_id),
                )
            connection.commit()

    def load_credit_note_request_fact(self, extraction_id: str) -> int:
        """Carga el hecho de solicitudes de nota de credito."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_financial_credit_note_requests (
                extraction_id,
                source_id,
                request_number,
                order_id,
                order_number,
                request_date_key,
                created_date_key,
                technician_key,
                status_name,
                subject_name,
                admin_name,
                rejection_reason,
                request_count,
                is_pending,
                is_approved,
                is_rejected,
                created_at
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.request_number_normalizado,
                src.orden_id,
                src.order_number_normalizado,
                request_date.date_key,
                created_date.date_key,
                technician.technician_key,
                src.status_name_normalizado,
                src.subject_name_normalizado,
                src.admin_name_normalizado,
                src.rejection_reason_normalizado,
                1,
                CASE WHEN src.status_name_normalizado = 'Pendiente' THEN TRUE ELSE FALSE END,
                CASE WHEN src.status_name_normalizado = 'Aprobada' THEN TRUE ELSE FALSE END,
                CASE WHEN src.status_name_normalizado = 'Rechazada' THEN TRUE ELSE FALSE END,
                src.created_at
            FROM (
                SELECT
                    extraction_id,
                    source_id,
                    orden_id,
                    tecnico_id,
                    fecha_solicitud,
                    created_at,
                    COALESCE(
                        NULLIF(REGEXP_REPLACE(BTRIM(nro_solicitud), '\s+', ' ', 'g'), ''),
                        CONCAT('SIN-SOLICITUD-', source_id::TEXT)
                    ) AS request_number_normalizado,
                    NULLIF(REGEXP_REPLACE(BTRIM(nro_orden), '\s+', ' ', 'g'), '') AS order_number_normalizado,
                    COALESCE(
                        NULLIF(REGEXP_REPLACE(BTRIM(asunto), '\s+', ' ', 'g'), ''),
                        'Sin asunto informado'
                    ) AS subject_name_normalizado,
                    NULLIF(REGEXP_REPLACE(BTRIM(nombre_admin), '\s+', ' ', 'g'), '') AS admin_name_normalizado,
                    NULLIF(REGEXP_REPLACE(BTRIM(motivo_rechazo), '\s+', ' ', 'g'), '') AS rejection_reason_normalizado,
                    CASE
                        WHEN UPPER(BTRIM(estado)) = 'PENDIENTE' THEN 'Pendiente'
                        WHEN UPPER(BTRIM(estado)) = 'APROBADA' THEN 'Aprobada'
                        WHEN UPPER(BTRIM(estado)) = 'RECHAZADA' THEN 'Rechazada'
                        ELSE 'Desconocido'
                    END AS status_name_normalizado
                FROM {self._staging_schema}.stg_financial_credit_note_requests
                WHERE extraction_id = %s
            ) src
            INNER JOIN {self._mart_schema}.dim_financial_date request_date
                ON request_date.full_date = src.fecha_solicitud
            LEFT JOIN {self._mart_schema}.dim_financial_date created_date
                ON created_date.full_date = src.created_at::DATE
            INNER JOIN {self._mart_schema}.dim_financial_technician technician
                ON technician.tecnico_id = src.tecnico_id
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET request_number = EXCLUDED.request_number,
                order_id = EXCLUDED.order_id,
                order_number = EXCLUDED.order_number,
                request_date_key = EXCLUDED.request_date_key,
                created_date_key = EXCLUDED.created_date_key,
                technician_key = EXCLUDED.technician_key,
                status_name = EXCLUDED.status_name,
                subject_name = EXCLUDED.subject_name,
                admin_name = EXCLUDED.admin_name,
                rejection_reason = EXCLUDED.rejection_reason,
                request_count = EXCLUDED.request_count,
                is_pending = EXCLUDED.is_pending,
                is_approved = EXCLUDED.is_approved,
                is_rejected = EXCLUDED.is_rejected,
                created_at = EXCLUDED.created_at
        """

        return self._execute_fact_load(
            sql=sql,
            extraction_id=extraction_id,
            table_name="fact_financial_credit_note_requests",
            params=(extraction_id,),
        )

    def load_order_price_fact(self, extraction_id: str) -> int:
        """Carga el hecho de ingresos directos por orden."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_financial_order_prices (
                extraction_id,
                source_id,
                order_id,
                order_number,
                created_date_key,
                price_standard_id,
                service_name,
                standard_service_name,
                amount,
                standard_amount,
                record_count,
                created_at
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.orden_id,
                src.order_number_normalizado,
                created_date.date_key,
                src.precio_estandar_id,
                src.service_name_normalizado,
                src.standard_service_name_normalizado,
                src.precio,
                src.precio_estandar,
                1,
                src.creado_en
            FROM (
                SELECT
                    extraction_id,
                    source_id,
                    orden_id,
                    precio_estandar_id,
                    precio,
                    precio_estandar,
                    creado_en,
                    NULLIF(REGEXP_REPLACE(BTRIM(nro_orden), '\s+', ' ', 'g'), '') AS order_number_normalizado,
                    COALESCE(
                        NULLIF(REGEXP_REPLACE(BTRIM(servicio), '\s+', ' ', 'g'), ''),
                        'Servicio no informado'
                    ) AS service_name_normalizado,
                    NULLIF(
                        REGEXP_REPLACE(BTRIM(servicio_estandar), '\s+', ' ', 'g'),
                        ''
                    ) AS standard_service_name_normalizado
                FROM {self._staging_schema}.stg_financial_order_prices
                WHERE extraction_id = %s
            ) src
            LEFT JOIN {self._mart_schema}.dim_financial_date created_date
                ON created_date.full_date = src.creado_en::DATE
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET order_id = EXCLUDED.order_id,
                order_number = EXCLUDED.order_number,
                created_date_key = EXCLUDED.created_date_key,
                price_standard_id = EXCLUDED.price_standard_id,
                service_name = EXCLUDED.service_name,
                standard_service_name = EXCLUDED.standard_service_name,
                amount = EXCLUDED.amount,
                standard_amount = EXCLUDED.standard_amount,
                record_count = EXCLUDED.record_count,
                created_at = EXCLUDED.created_at
        """

        return self._execute_fact_load(
            sql=sql,
            extraction_id=extraction_id,
            table_name="fact_financial_order_prices",
            params=(extraction_id,),
        )

    def load_credit_note_notification_fact(self, extraction_id: str) -> int:
        """Carga el hecho de eventos de notificaciones de notas de credito."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_financial_credit_note_notifications (
                extraction_id,
                source_id,
                order_id,
                order_number,
                nc_id,
                notification_date_key,
                technician_key,
                notification_type,
                is_read,
                notification_count,
                created_at
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.orden_id,
                src.order_number_normalizado,
                src.nc_id,
                notification_date.date_key,
                technician.technician_key,
                src.notification_type_normalizado,
                src.leida,
                1,
                src.created_at
            FROM (
                SELECT
                    extraction_id,
                    source_id,
                    usuario_id,
                    orden_id,
                    nc_id,
                    leida,
                    created_at,
                    NULLIF(REGEXP_REPLACE(BTRIM(nro_orden), '\s+', ' ', 'g'), '') AS order_number_normalizado,
                    CASE
                        WHEN LOWER(BTRIM(tipo)) = 'nc_solicitud' THEN 'nc_solicitud'
                        WHEN LOWER(BTRIM(tipo)) = 'nc_aprobada' THEN 'nc_aprobada'
                        WHEN LOWER(BTRIM(tipo)) = 'nc_rechazada' THEN 'nc_rechazada'
                        ELSE 'nc_otro'
                    END AS notification_type_normalizado
                FROM {self._staging_schema}.stg_financial_credit_note_notifications
                WHERE extraction_id = %s
            ) src
            INNER JOIN {self._mart_schema}.dim_financial_date notification_date
                ON notification_date.full_date = src.created_at::DATE
            INNER JOIN {self._mart_schema}.dim_financial_technician technician
                ON technician.tecnico_id = src.usuario_id
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET order_id = EXCLUDED.order_id,
                order_number = EXCLUDED.order_number,
                nc_id = EXCLUDED.nc_id,
                notification_date_key = EXCLUDED.notification_date_key,
                technician_key = EXCLUDED.technician_key,
                notification_type = EXCLUDED.notification_type,
                is_read = EXCLUDED.is_read,
                notification_count = EXCLUDED.notification_count,
                created_at = EXCLUDED.created_at
        """

        return self._execute_fact_load(
            sql=sql,
            extraction_id=extraction_id,
            table_name="fact_financial_credit_note_notifications",
            params=(extraction_id,),
        )

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Calcula hallazgos de calidad y los registra por corrida."""

        sql = f"""
            INSERT INTO {self._mart_schema}.etl_financial_quality_audit (
                extraction_id,
                entity_name,
                rule_name,
                severity,
                affected_rows
            )
            SELECT
                %s AS extraction_id,
                audit.entity_name,
                audit.rule_name,
                audit.severity,
                audit.affected_rows
            FROM (
                SELECT
                    'credit_note_requests' AS entity_name,
                    'estado_desconocido' AS rule_name,
                    'warning' AS severity,
                    COUNT(*)::INTEGER AS affected_rows
                FROM {self._staging_schema}.stg_financial_credit_note_requests
                WHERE extraction_id = %s
                  AND UPPER(BTRIM(estado)) NOT IN ('PENDIENTE', 'APROBADA', 'RECHAZADA')

                UNION ALL

                SELECT
                    'credit_note_requests',
                    'solicitudes_aprobadas_sin_admin',
                    'warning',
                    COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_financial_credit_note_requests
                WHERE extraction_id = %s
                  AND UPPER(BTRIM(estado)) = 'APROBADA'
                  AND NULLIF(REGEXP_REPLACE(BTRIM(nombre_admin), '\s+', ' ', 'g'), '') IS NULL

                UNION ALL

                SELECT
                    'credit_note_requests',
                    'asunto_vacio',
                    'warning',
                    COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_financial_credit_note_requests
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(asunto), '\s+', ' ', 'g'), '') IS NULL

                UNION ALL

                SELECT
                    'order_prices',
                    'precio_no_positivo',
                    'warning',
                    COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_financial_order_prices
                WHERE extraction_id = %s
                  AND precio <= 0

                UNION ALL

                SELECT
                    'order_prices',
                    'servicio_vacio',
                    'warning',
                    COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_financial_order_prices
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(servicio), '\s+', ' ', 'g'), '') IS NULL

                UNION ALL

                SELECT
                    'notifications',
                    'tipo_desconocido',
                    'warning',
                    COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_financial_credit_note_notifications
                WHERE extraction_id = %s
                  AND LOWER(BTRIM(tipo)) NOT IN ('nc_solicitud', 'nc_aprobada', 'nc_rechazada')

                UNION ALL

                SELECT
                    'notifications',
                    'usuario_sin_nombre',
                    'warning',
                    COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_financial_credit_note_notifications
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(usuario_nombre), '\s+', ' ', 'g'), '') IS NULL
            ) audit
            ON CONFLICT (extraction_id, entity_name, rule_name) DO UPDATE
            SET severity = EXCLUDED.severity,
                affected_rows = EXCLUDED.affected_rows,
                created_at = NOW()
        """

        summary_sql = f"""
            SELECT
                COUNT(*)::INTEGER AS total_rules,
                COALESCE(SUM(affected_rows), 0)::INTEGER AS total_findings
            FROM {self._mart_schema}.etl_financial_quality_audit
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
            "Auditoria de calidad financiera actualizada | extraction_id=%s | reglas=%s | hallazgos=%s",
            extraction_id,
            row[0],
            row[1],
        )
        return int(row[0]), int(row[1])

    def _execute_fact_load(
        self,
        sql: str,
        extraction_id: str,
        table_name: str,
        params: tuple[object, ...],
    ) -> int:
        """Ejecuta una carga de hecho y devuelve el total final de la corrida."""

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                cursor.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM {self._mart_schema}.{table_name}
                    WHERE extraction_id = %s
                    """,
                    (extraction_id,),
                )
                total = int(cursor.fetchone()[0])
            connection.commit()

        logger.info(
            "Hecho financiero cargado en mart | tabla=%s | extraction_id=%s | total=%s",
            table_name,
            extraction_id,
            total,
        )
        return total
