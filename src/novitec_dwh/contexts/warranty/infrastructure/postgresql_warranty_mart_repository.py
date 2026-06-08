"""Repositorio PostgreSQL para construir el mart del dominio de garantias."""

from importlib.resources import files
import logging

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger(__name__)


class PostgreSQLWarrantyMartRepository:
    """Construye dimensiones, hechos y auditoria de calidad de garantias."""

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
            files("novitec_dwh.contexts.warranty.infrastructure.sql")
            .joinpath("warranty_mart.sql")
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
            "etl_warranty_quality_audit",
            "fact_warranty_user_assignments",
            "fact_warranty_company_orders",
            "fact_warranty_personal_orders",
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
        """Obtiene la corrida mas reciente disponible en staging."""

        sql = f"SELECT MAX(extraction_id) FROM {self._staging_schema}.stg_warranty_service_centers"

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()

        extraction_id = row[0] if row else None
        if not extraction_id:
            raise ValueError(
                "No se encontro ninguna corrida de garantias en staging para construir el mart."
            )

        return str(extraction_id)

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga todas las fechas necesarias para la corrida del mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_warranty_date (
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
                SELECT creado_en::DATE AS source_date
                FROM {self._staging_schema}.stg_warranty_service_centers
                WHERE extraction_id = %s

                UNION

                SELECT fecha_de_ingreso::DATE AS source_date
                FROM {self._staging_schema}.stg_warranty_personal_orders
                WHERE extraction_id = %s
                  AND fecha_de_ingreso IS NOT NULL

                UNION

                SELECT cas_fecha_envio AS source_date
                FROM {self._staging_schema}.stg_warranty_personal_orders
                WHERE extraction_id = %s
                  AND cas_fecha_envio IS NOT NULL

                UNION

                SELECT cas_fecha_retorno AS source_date
                FROM {self._staging_schema}.stg_warranty_personal_orders
                WHERE extraction_id = %s
                  AND cas_fecha_retorno IS NOT NULL

                UNION

                SELECT fecha_prometido AS source_date
                FROM {self._staging_schema}.stg_warranty_personal_orders
                WHERE extraction_id = %s
                  AND fecha_prometido IS NOT NULL

                UNION

                SELECT fecha_ingreso::DATE AS source_date
                FROM {self._staging_schema}.stg_warranty_company_orders
                WHERE extraction_id = %s

                UNION

                SELECT fecha_prometido AS source_date
                FROM {self._staging_schema}.stg_warranty_company_orders
                WHERE extraction_id = %s
                  AND fecha_prometido IS NOT NULL
            ) dates
            ON CONFLICT (date_key) DO NOTHING
        """

        params = (extraction_id,) * 7
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            connection.commit()

    def load_service_center_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de centros autorizados."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_warranty_service_center (
                source_id, service_center_name, prefix_code, brand_name, phone_number,
                email, address, city_name, contact_name, notes, is_active,
                first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombre), '\\s+', ' ', 'g'), ''), CONCAT('CAS ', source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(prefijo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(marca), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(telefono), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(correo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(direccion), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(ciudad), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(contacto), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(notas), '\\s+', ' ', 'g'), ''),
                activo,
                %s,
                %s
            FROM {self._staging_schema}.stg_warranty_service_centers
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET service_center_name = EXCLUDED.service_center_name,
                prefix_code = EXCLUDED.prefix_code,
                brand_name = EXCLUDED.brand_name,
                phone_number = EXCLUDED.phone_number,
                email = EXCLUDED.email,
                address = EXCLUDED.address,
                city_name = EXCLUDED.city_name,
                contact_name = EXCLUDED.contact_name,
                notes = EXCLUDED.notes,
                is_active = EXCLUDED.is_active,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_user_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de usuarios y tecnicos."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_warranty_user (
                source_id, user_login, user_name, first_extraction_id, last_extraction_id
            )
            SELECT
                ranked.user_id,
                ranked.user_login,
                ranked.user_name,
                %s,
                %s
            FROM (
                SELECT DISTINCT ON (src.user_id)
                    src.user_id,
                    src.user_login,
                    src.user_name
                FROM (
                    SELECT
                        usuario_id AS user_id,
                        NULLIF(REGEXP_REPLACE(BTRIM(usuario_login), '\\s+', ' ', 'g'), '') AS user_login,
                        COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(usuario_nombre), '\\s+', ' ', 'g'), ''), CONCAT('Usuario ', usuario_id::TEXT)) AS user_name,
                        1 AS priority
                    FROM {self._staging_schema}.stg_warranty_user_assignments
                    WHERE extraction_id = %s

                    UNION ALL

                    SELECT DISTINCT
                        tecnico_id AS user_id,
                        NULL::TEXT AS user_login,
                        CONCAT('Tecnico ', tecnico_id::TEXT) AS user_name,
                        2 AS priority
                    FROM {self._staging_schema}.stg_warranty_personal_orders
                    WHERE extraction_id = %s

                    UNION ALL

                    SELECT DISTINCT
                        tecnico_id AS user_id,
                        NULL::TEXT AS user_login,
                        CONCAT('Tecnico ', tecnico_id::TEXT) AS user_name,
                        2 AS priority
                    FROM {self._staging_schema}.stg_warranty_company_orders
                    WHERE extraction_id = %s
                ) src
                WHERE src.user_id IS NOT NULL
                ORDER BY src.user_id, src.priority
            ) ranked
            ON CONFLICT (source_id) DO UPDATE
            SET user_login = COALESCE(EXCLUDED.user_login, {self._mart_schema}.dim_warranty_user.user_login),
                user_name = EXCLUDED.user_name,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        params = (
            extraction_id,
            extraction_id,
            extraction_id,
            extraction_id,
            extraction_id,
        )
        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
            connection.commit()

    def load_personal_order_fact(self, extraction_id: str) -> int:
        """Carga el hecho de ordenes personales con garantia."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_warranty_personal_orders (
                extraction_id, source_id, opened_date_key, promised_date_key, shipped_date_key,
                returned_date_key, delivered_date_key, finalized_date_key, service_center_key,
                technician_key, branch_id, client_id, equipment_id, order_number, order_status,
                warranty_status, warranty_type, service_center_name, case_number, cycle_days,
                sla_days, has_case_number, has_return_date, is_closed, order_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                opened_dim.date_key,
                promised_dim.date_key,
                shipped_dim.date_key,
                returned_dim.date_key,
                delivered_dim.date_key,
                finalized_dim.date_key,
                sc.service_center_key,
                usr.user_key,
                src.sucursal_id,
                src.cliente_id,
                src.equipo_id,
                src.nro_orden,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.estado_orden), '\\s+', ' ', 'g'), ''), 'No informado'),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.estado_garantia), '\\s+', ' ', 'g'), ''), 'No informado'),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.garantia_tipo), '\\s+', ' ', 'g'), ''), 'No informado'),
                COALESCE(
                    NULLIF(REGEXP_REPLACE(BTRIM(src.garantia_cas), '\\s+', ' ', 'g'), ''),
                    sc.service_center_name,
                    'CAS no informado'
                ),
                NULLIF(REGEXP_REPLACE(BTRIM(src.cas_numero_caso), '\\s+', ' ', 'g'), ''),
                CASE
                    WHEN src.fecha_de_ingreso IS NOT NULL AND src.fecha_finalizacion IS NOT NULL
                        THEN (src.fecha_finalizacion::DATE - src.fecha_de_ingreso::DATE)
                    WHEN src.fecha_de_ingreso IS NOT NULL AND src.fecha_entrega IS NOT NULL
                        THEN (src.fecha_entrega::DATE - src.fecha_de_ingreso::DATE)
                    ELSE NULL
                END,
                CASE
                    WHEN src.fecha_de_ingreso IS NOT NULL AND src.fecha_prometido IS NOT NULL
                        THEN (src.fecha_prometido - src.fecha_de_ingreso::DATE)
                    ELSE NULL
                END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.cas_numero_caso), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN src.cas_fecha_retorno IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE
                    WHEN src.fecha_entrega IS NOT NULL OR src.fecha_finalizacion IS NOT NULL THEN TRUE
                    ELSE FALSE
                END,
                1
            FROM {self._staging_schema}.stg_warranty_personal_orders src
            LEFT JOIN {self._mart_schema}.dim_warranty_date opened_dim
                ON opened_dim.full_date = src.fecha_de_ingreso::DATE
            LEFT JOIN {self._mart_schema}.dim_warranty_date promised_dim
                ON promised_dim.full_date = src.fecha_prometido
            LEFT JOIN {self._mart_schema}.dim_warranty_date shipped_dim
                ON shipped_dim.full_date = src.cas_fecha_envio
            LEFT JOIN {self._mart_schema}.dim_warranty_date returned_dim
                ON returned_dim.full_date = src.cas_fecha_retorno
            LEFT JOIN {self._mart_schema}.dim_warranty_date delivered_dim
                ON delivered_dim.full_date = src.fecha_entrega::DATE
            LEFT JOIN {self._mart_schema}.dim_warranty_date finalized_dim
                ON finalized_dim.full_date = src.fecha_finalizacion::DATE
            LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                ON sc.source_id = src.cas_id
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.source_id = src.tecnico_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET opened_date_key = EXCLUDED.opened_date_key,
                promised_date_key = EXCLUDED.promised_date_key,
                shipped_date_key = EXCLUDED.shipped_date_key,
                returned_date_key = EXCLUDED.returned_date_key,
                delivered_date_key = EXCLUDED.delivered_date_key,
                finalized_date_key = EXCLUDED.finalized_date_key,
                service_center_key = EXCLUDED.service_center_key,
                technician_key = EXCLUDED.technician_key,
                branch_id = EXCLUDED.branch_id,
                client_id = EXCLUDED.client_id,
                equipment_id = EXCLUDED.equipment_id,
                order_number = EXCLUDED.order_number,
                order_status = EXCLUDED.order_status,
                warranty_status = EXCLUDED.warranty_status,
                warranty_type = EXCLUDED.warranty_type,
                service_center_name = EXCLUDED.service_center_name,
                case_number = EXCLUDED.case_number,
                cycle_days = EXCLUDED.cycle_days,
                sla_days = EXCLUDED.sla_days,
                has_case_number = EXCLUDED.has_case_number,
                has_return_date = EXCLUDED.has_return_date,
                is_closed = EXCLUDED.is_closed,
                order_count = EXCLUDED.order_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_warranty_personal_orders")

    def load_company_order_fact(self, extraction_id: str) -> int:
        """Carga el hecho de ordenes empresariales asociadas a CAS."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_warranty_company_orders (
                extraction_id, source_id, opened_date_key, promised_date_key, service_center_key,
                technician_key, branch_id, company_id, equipment_id, order_number, order_status,
                ticket_number, hourly_rate, worked_hours, estimated_revenue, cycle_days, sla_days,
                has_ticket_number, has_worked_hours, order_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                opened_dim.date_key,
                promised_dim.date_key,
                sc.service_center_key,
                usr.user_key,
                src.sucursal_id,
                src.empresa_id,
                src.equipo_id,
                src.nro_orden,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.estado), '\\s+', ' ', 'g'), ''), 'No informado'),
                NULLIF(REGEXP_REPLACE(BTRIM(src.nro_ticket), '\\s+', ' ', 'g'), ''),
                src.valor_hora,
                src.horas_trabajadas,
                CASE
                    WHEN src.valor_hora IS NOT NULL AND src.horas_trabajadas IS NOT NULL
                        THEN ROUND(src.valor_hora * src.horas_trabajadas, 2)
                    ELSE NULL
                END,
                CASE
                    WHEN src.fecha_prometido IS NOT NULL
                        THEN (src.fecha_prometido - src.fecha_ingreso::DATE)
                    ELSE NULL
                END,
                CASE
                    WHEN src.fecha_prometido IS NOT NULL
                        THEN (src.fecha_prometido - src.fecha_ingreso::DATE)
                    ELSE NULL
                END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.nro_ticket), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN src.horas_trabajadas IS NOT NULL AND src.horas_trabajadas > 0 THEN TRUE ELSE FALSE END,
                1
            FROM {self._staging_schema}.stg_warranty_company_orders src
            LEFT JOIN {self._mart_schema}.dim_warranty_date opened_dim
                ON opened_dim.full_date = src.fecha_ingreso::DATE
            LEFT JOIN {self._mart_schema}.dim_warranty_date promised_dim
                ON promised_dim.full_date = src.fecha_prometido
            LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                ON sc.source_id = src.cas_id
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.source_id = src.tecnico_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET opened_date_key = EXCLUDED.opened_date_key,
                promised_date_key = EXCLUDED.promised_date_key,
                service_center_key = EXCLUDED.service_center_key,
                technician_key = EXCLUDED.technician_key,
                branch_id = EXCLUDED.branch_id,
                company_id = EXCLUDED.company_id,
                equipment_id = EXCLUDED.equipment_id,
                order_number = EXCLUDED.order_number,
                order_status = EXCLUDED.order_status,
                ticket_number = EXCLUDED.ticket_number,
                hourly_rate = EXCLUDED.hourly_rate,
                worked_hours = EXCLUDED.worked_hours,
                estimated_revenue = EXCLUDED.estimated_revenue,
                cycle_days = EXCLUDED.cycle_days,
                sla_days = EXCLUDED.sla_days,
                has_ticket_number = EXCLUDED.has_ticket_number,
                has_worked_hours = EXCLUDED.has_worked_hours,
                order_count = EXCLUDED.order_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_warranty_company_orders")

    def load_user_assignment_fact(self, extraction_id: str) -> int:
        """Carga el hecho de asignaciones entre usuarios y CAS."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_warranty_user_assignments (
                extraction_id, source_id, user_key, service_center_key, user_id,
                service_center_id, assignment_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                usr.user_key,
                sc.service_center_key,
                src.usuario_id,
                src.cas_id,
                1
            FROM {self._staging_schema}.stg_warranty_user_assignments src
            LEFT JOIN {self._mart_schema}.dim_warranty_user usr
                ON usr.source_id = src.usuario_id
            LEFT JOIN {self._mart_schema}.dim_warranty_service_center sc
                ON sc.source_id = src.cas_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET user_key = EXCLUDED.user_key,
                service_center_key = EXCLUDED.service_center_key,
                user_id = EXCLUDED.user_id,
                service_center_id = EXCLUDED.service_center_id,
                assignment_count = EXCLUDED.assignment_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_warranty_user_assignments")

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Calcula hallazgos de calidad y los registra por corrida."""

        sql = f"""
            INSERT INTO {self._mart_schema}.etl_warranty_quality_audit (
                extraction_id, entity_name, rule_name, severity, affected_rows
            )
            SELECT
                %s,
                audit.entity_name,
                audit.rule_name,
                audit.severity,
                audit.affected_rows
            FROM (
                SELECT 'service_centers', 'cas_sin_contacto', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_warranty_service_centers
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(telefono), '\\s+', ' ', 'g'), '') IS NULL
                  AND NULLIF(REGEXP_REPLACE(BTRIM(correo), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'user_assignments', 'asignacion_con_cas_inexistente', 'critical', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_warranty_user_assignments src
                LEFT JOIN {self._staging_schema}.stg_warranty_service_centers cas
                    ON cas.extraction_id = src.extraction_id
                   AND cas.source_id = src.cas_id
                WHERE src.extraction_id = %s
                  AND cas.source_id IS NULL

                UNION ALL
                SELECT 'personal_orders', 'orden_personal_sin_cas', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_warranty_personal_orders
                WHERE extraction_id = %s
                  AND cas_id IS NULL

                UNION ALL
                SELECT 'personal_orders', 'retorno_antes_envio', 'critical', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_warranty_personal_orders
                WHERE extraction_id = %s
                  AND cas_fecha_envio IS NOT NULL
                  AND cas_fecha_retorno IS NOT NULL
                  AND cas_fecha_retorno < cas_fecha_envio

                UNION ALL
                SELECT 'company_orders', 'orden_empresa_sin_cas', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_warranty_company_orders
                WHERE extraction_id = %s
                  AND cas_id IS NULL

                UNION ALL
                SELECT 'company_orders', 'orden_empresa_sin_ticket', 'info', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_warranty_company_orders
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(nro_ticket), '\\s+', ' ', 'g'), '') IS NULL
            ) audit(entity_name, rule_name, severity, affected_rows)
            ON CONFLICT (extraction_id, entity_name, rule_name) DO UPDATE
            SET severity = EXCLUDED.severity,
                affected_rows = EXCLUDED.affected_rows,
                created_at = NOW()
        """
        summary_sql = f"""
            SELECT COUNT(*)::INTEGER, COALESCE(SUM(affected_rows), 0)::INTEGER
            FROM {self._mart_schema}.etl_warranty_quality_audit
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
            "Auditoria de calidad de garantias actualizada | extraction_id=%s | reglas=%s | hallazgos=%s",
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
            "Hecho de garantias cargado en mart | tabla=%s | extraction_id=%s | total=%s",
            table_name,
            extraction_id,
            total,
        )
        return total
