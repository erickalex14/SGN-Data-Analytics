"""Repositorio PostgreSQL para construir el mart tecnico."""

from importlib.resources import files
import logging

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger(__name__)


class PostgreSQLTechnicalMartRepository:
    """Construye dimensiones y hechos tecnicos a partir del staging."""

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
            files("novitec_dwh.contexts.technical.infrastructure.sql")
            .joinpath("technical_mart.sql")
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
            "etl_technical_quality_audit",
            "fact_technical_equipment_access",
            "fact_technical_equipment",
            "fact_technical_report_photos",
            "fact_technical_reports",
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
        """Obtiene la corrida tecnica mas reciente disponible en staging."""

        sql = f"SELECT MAX(extraction_id) FROM {self._staging_schema}.stg_technical_reports"

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()

        extraction_id = row[0] if row else None
        if not extraction_id:
            raise ValueError(
                "No se encontro ninguna corrida tecnica en staging para construir el mart."
            )

        return str(extraction_id)

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga todas las fechas necesarias para la corrida del mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_technical_date (
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
                SELECT fecha_informe AS source_date
                FROM {self._staging_schema}.stg_technical_reports
                WHERE extraction_id = %s

                UNION
                SELECT fecha_creacion::DATE
                FROM {self._staging_schema}.stg_technical_reports
                WHERE extraction_id = %s
                  AND fecha_creacion IS NOT NULL

                UNION
                SELECT fecha_facturacion
                FROM {self._staging_schema}.stg_technical_equipment
                WHERE extraction_id = %s
                  AND fecha_facturacion IS NOT NULL

                UNION
                SELECT created_at::DATE
                FROM {self._staging_schema}.stg_technical_equipment_series
                WHERE extraction_id = %s
                  AND created_at IS NOT NULL

                UNION
                SELECT created_at::DATE
                FROM {self._staging_schema}.stg_technical_service_types
                WHERE extraction_id = %s
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
                    ),
                )
            connection.commit()

    def load_technician_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de tecnicos usada por el mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_technical_technician (
                tecnico_id, tecnico_nombre, first_extraction_id, last_extraction_id
            )
            SELECT
                tecnico_id,
                CONCAT('Tecnico ', tecnico_id::TEXT),
                %s,
                %s
            FROM (
                SELECT DISTINCT tecnico_id
                FROM {self._staging_schema}.stg_technical_reports
                WHERE extraction_id = %s
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

    def load_service_type_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de tipos de servicio."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_technical_service_type (
                source_id, service_name, service_description, standard_price,
                is_active, first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombre), '\\s+', ' ', 'g'), ''), CONCAT('Servicio ', source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(descripcion), '\\s+', ' ', 'g'), ''),
                precio,
                activo,
                %s,
                %s
            FROM {self._staging_schema}.stg_technical_service_types
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET service_name = EXCLUDED.service_name,
                service_description = EXCLUDED.service_description,
                standard_price = EXCLUDED.standard_price,
                is_active = EXCLUDED.is_active,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_brand_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de marcas usada por el mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_technical_brand (
                brand_name, source_id, first_extraction_id, last_extraction_id
            )
            SELECT
                src.brand_name,
                src.source_id,
                %s,
                %s
            FROM (
                SELECT DISTINCT ON (brand_name_normalized)
                    brand_name_normalized AS brand_name,
                    source_id
                FROM (
                    SELECT
                        source_id,
                        COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombre), '\\s+', ' ', 'g'), ''), CONCAT('Marca ', source_id::TEXT)) AS brand_name_normalized
                    FROM {self._staging_schema}.stg_technical_brands
                    WHERE extraction_id = %s

                    UNION ALL

                    SELECT
                        NULL::INTEGER AS source_id,
                        REGEXP_REPLACE(BTRIM(marca), '\\s+', ' ', 'g') AS brand_name_normalized
                    FROM {self._staging_schema}.stg_technical_equipment
                    WHERE extraction_id = %s
                      AND NULLIF(REGEXP_REPLACE(BTRIM(marca), '\\s+', ' ', 'g'), '') IS NOT NULL
                ) candidates
                ORDER BY brand_name_normalized, source_id NULLS LAST
            ) src
            ON CONFLICT (brand_name) DO UPDATE
            SET source_id = COALESCE(EXCLUDED.source_id, {self._mart_schema}.dim_technical_brand.source_id),
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_report_fact(self, extraction_id: str) -> int:
        """Carga el hecho principal de informes tecnicos."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_technical_reports (
                extraction_id, source_id, order_id, technician_key, report_date_key,
                created_date_key, equipment_status, has_background, has_process,
                has_conclusion, has_recommendations, has_budget_json,
                is_equipment_operational, background_length, process_length,
                conclusion_length, recommendation_length, report_count, created_at
            )
            SELECT
                src.extraction_id,
                src.source_id,
                src.orden_id,
                tech.technician_key,
                report_date.date_key,
                created_date.date_key,
                src.equipment_status_normalized,
                src.has_background,
                src.has_process,
                src.has_conclusion,
                src.has_recommendations,
                src.has_budget_json,
                CASE
                    WHEN UPPER(src.equipment_status_normalized) = 'OPERATIVO' THEN TRUE
                    ELSE FALSE
                END,
                src.background_length,
                src.process_length,
                src.conclusion_length,
                src.recommendation_length,
                1,
                src.fecha_creacion
            FROM (
                SELECT
                    extraction_id,
                    source_id,
                    orden_id,
                    tecnico_id,
                    fecha_informe,
                    fecha_creacion,
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(estado_equipo), '\\s+', ' ', 'g'), ''), 'No informado') AS equipment_status_normalized,
                    NULLIF(REGEXP_REPLACE(BTRIM(antecedentes), '\\s+', ' ', 'g'), '') IS NOT NULL AS has_background,
                    NULLIF(REGEXP_REPLACE(BTRIM(proceso), '\\s+', ' ', 'g'), '') IS NOT NULL AS has_process,
                    NULLIF(REGEXP_REPLACE(BTRIM(conclusion), '\\s+', ' ', 'g'), '') IS NOT NULL AS has_conclusion,
                    NULLIF(REGEXP_REPLACE(BTRIM(recomendaciones), '\\s+', ' ', 'g'), '') IS NOT NULL AS has_recommendations,
                    NULLIF(BTRIM(presupuesto_json), '') IS NOT NULL AS has_budget_json,
                    LENGTH(COALESCE(antecedentes, ''))::INTEGER AS background_length,
                    LENGTH(COALESCE(proceso, ''))::INTEGER AS process_length,
                    LENGTH(COALESCE(conclusion, ''))::INTEGER AS conclusion_length,
                    LENGTH(COALESCE(recomendaciones, ''))::INTEGER AS recommendation_length
                FROM {self._staging_schema}.stg_technical_reports
                WHERE extraction_id = %s
            ) src
            INNER JOIN {self._mart_schema}.dim_technical_technician tech
                ON tech.tecnico_id = src.tecnico_id
            INNER JOIN {self._mart_schema}.dim_technical_date report_date
                ON report_date.full_date = src.fecha_informe
            LEFT JOIN {self._mart_schema}.dim_technical_date created_date
                ON created_date.full_date = src.fecha_creacion::DATE
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET order_id = EXCLUDED.order_id,
                technician_key = EXCLUDED.technician_key,
                report_date_key = EXCLUDED.report_date_key,
                created_date_key = EXCLUDED.created_date_key,
                equipment_status = EXCLUDED.equipment_status,
                has_background = EXCLUDED.has_background,
                has_process = EXCLUDED.has_process,
                has_conclusion = EXCLUDED.has_conclusion,
                has_recommendations = EXCLUDED.has_recommendations,
                has_budget_json = EXCLUDED.has_budget_json,
                is_equipment_operational = EXCLUDED.is_equipment_operational,
                background_length = EXCLUDED.background_length,
                process_length = EXCLUDED.process_length,
                conclusion_length = EXCLUDED.conclusion_length,
                recommendation_length = EXCLUDED.recommendation_length,
                report_count = EXCLUDED.report_count,
                created_at = EXCLUDED.created_at
        """
        return self._execute_fact_load(sql, extraction_id, "fact_technical_reports")

    def load_report_photo_fact(self, extraction_id: str) -> int:
        """Carga el hecho de evidencia fotografica."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_technical_report_photos (
                extraction_id, source_id, report_source_id, report_date_key,
                technician_key, photo_order, file_name, mime_type, caption,
                has_binary_evidence, has_file_name, is_jpeg, photo_count
            )
            SELECT
                photo.extraction_id,
                photo.source_id,
                photo.informe_id,
                report_date.date_key,
                tech.technician_key,
                photo.orden_foto,
                NULLIF(REGEXP_REPLACE(BTRIM(photo.nombre_archivo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(photo.tipo_mime), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(photo.caption), '\\s+', ' ', 'g'), ''),
                photo.tiene_foto,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(photo.nombre_archivo), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN LOWER(COALESCE(BTRIM(photo.tipo_mime), '')) = 'image/jpeg' THEN TRUE ELSE FALSE END,
                1
            FROM {self._staging_schema}.stg_technical_report_photos photo
            INNER JOIN {self._staging_schema}.stg_technical_reports report
                ON report.extraction_id = photo.extraction_id
               AND report.source_id = photo.informe_id
            INNER JOIN {self._mart_schema}.dim_technical_technician tech
                ON tech.tecnico_id = report.tecnico_id
            INNER JOIN {self._mart_schema}.dim_technical_date report_date
                ON report_date.full_date = report.fecha_informe
            WHERE photo.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET report_source_id = EXCLUDED.report_source_id,
                report_date_key = EXCLUDED.report_date_key,
                technician_key = EXCLUDED.technician_key,
                photo_order = EXCLUDED.photo_order,
                file_name = EXCLUDED.file_name,
                mime_type = EXCLUDED.mime_type,
                caption = EXCLUDED.caption,
                has_binary_evidence = EXCLUDED.has_binary_evidence,
                has_file_name = EXCLUDED.has_file_name,
                is_jpeg = EXCLUDED.is_jpeg,
                photo_count = EXCLUDED.photo_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_technical_report_photos")

    def load_equipment_fact(self, extraction_id: str) -> int:
        """Carga el hecho de equipos tecnicos."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_technical_equipment (
                extraction_id, source_id, service_type_key, brand_key,
                billing_date_key, device_type_name, device_model, serial_number,
                inventory_product_code, has_password_provided, has_failure_description,
                has_observation, has_billing_date, equipment_count
            )
            SELECT
                eq.extraction_id,
                eq.source_id,
                srv.service_type_key,
                brand.brand_key,
                billing_date.date_key,
                NULLIF(REGEXP_REPLACE(BTRIM(eq.tipo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(eq.modelo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(eq.serie), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(eq.producto_inventario_codigo), '\\s+', ' ', 'g'), ''),
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(eq.contrasena_equipo), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(eq.falla), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(eq.observacion), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN eq.fecha_facturacion IS NOT NULL THEN TRUE ELSE FALSE END,
                1
            FROM {self._staging_schema}.stg_technical_equipment eq
            LEFT JOIN {self._mart_schema}.dim_technical_service_type srv
                ON srv.source_id = eq.tipo_servicio_id
            LEFT JOIN {self._mart_schema}.dim_technical_brand brand
                ON brand.brand_name = COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(eq.marca), '\\s+', ' ', 'g'), ''), 'Marca no informada')
            LEFT JOIN {self._mart_schema}.dim_technical_date billing_date
                ON billing_date.full_date = eq.fecha_facturacion
            WHERE eq.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET service_type_key = EXCLUDED.service_type_key,
                brand_key = EXCLUDED.brand_key,
                billing_date_key = EXCLUDED.billing_date_key,
                device_type_name = EXCLUDED.device_type_name,
                device_model = EXCLUDED.device_model,
                serial_number = EXCLUDED.serial_number,
                inventory_product_code = EXCLUDED.inventory_product_code,
                has_password_provided = EXCLUDED.has_password_provided,
                has_failure_description = EXCLUDED.has_failure_description,
                has_observation = EXCLUDED.has_observation,
                has_billing_date = EXCLUDED.has_billing_date,
                equipment_count = EXCLUDED.equipment_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_technical_equipment")

    def load_equipment_access_fact(self, extraction_id: str) -> int:
        """Carga el hecho de accesos proporcionados por el cliente."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_technical_equipment_access (
                extraction_id, source_id, equipment_source_id, has_user_name,
                is_pattern, access_count
            )
            SELECT
                extraction_id,
                source_id,
                equipo_id,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(usuario), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                es_patron,
                1
            FROM {self._staging_schema}.stg_technical_equipment_credentials
            WHERE extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET equipment_source_id = EXCLUDED.equipment_source_id,
                has_user_name = EXCLUDED.has_user_name,
                is_pattern = EXCLUDED.is_pattern,
                access_count = EXCLUDED.access_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_technical_equipment_access")

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Calcula hallazgos de calidad y los registra por corrida."""

        sql = f"""
            INSERT INTO {self._mart_schema}.etl_technical_quality_audit (
                extraction_id, entity_name, rule_name, severity, affected_rows
            )
            SELECT
                %s,
                audit.entity_name,
                audit.rule_name,
                audit.severity,
                audit.affected_rows
            FROM (
                SELECT 'reports', 'informe_sin_proceso', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_technical_reports
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(proceso), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'reports', 'informe_sin_conclusion', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_technical_reports
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(conclusion), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'report_photos', 'foto_sin_nombre_archivo', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_technical_report_photos
                WHERE extraction_id = %s
                  AND tiene_foto = TRUE
                  AND NULLIF(REGEXP_REPLACE(BTRIM(nombre_archivo), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'equipment', 'equipo_sin_serie', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_technical_equipment
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(serie), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'equipment', 'equipo_sin_modelo', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_technical_equipment
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(modelo), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'equipment', 'equipo_sin_tipo_servicio', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_technical_equipment
                WHERE extraction_id = %s
                  AND tipo_servicio_id IS NULL
                  AND NULLIF(REGEXP_REPLACE(BTRIM(tipo_servicio_texto), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'equipment_credentials', 'credencial_sin_usuario', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_technical_equipment_credentials
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(usuario), '\\s+', ' ', 'g'), '') IS NULL
            ) audit(entity_name, rule_name, severity, affected_rows)
            ON CONFLICT (extraction_id, entity_name, rule_name) DO UPDATE
            SET severity = EXCLUDED.severity,
                affected_rows = EXCLUDED.affected_rows,
                created_at = NOW()
        """
        summary_sql = f"""
            SELECT COUNT(*)::INTEGER, COALESCE(SUM(affected_rows), 0)::INTEGER
            FROM {self._mart_schema}.etl_technical_quality_audit
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
            "Auditoria de calidad tecnica actualizada | extraction_id=%s | reglas=%s | hallazgos=%s",
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
            "Hecho tecnico cargado en mart | tabla=%s | extraction_id=%s | total=%s",
            table_name,
            extraction_id,
            total,
        )
        return total
