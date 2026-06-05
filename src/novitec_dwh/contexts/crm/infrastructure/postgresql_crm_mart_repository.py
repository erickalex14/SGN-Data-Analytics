"""Repositorio PostgreSQL para construir el mart CRM."""

from importlib.resources import files
import logging

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger(__name__)


class PostgreSQLCrmMartRepository:
    """Construye dimensiones y hechos CRM a partir del staging."""

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
            files("novitec_dwh.contexts.crm.infrastructure.sql")
            .joinpath("crm_mart.sql")
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
            "etl_crm_quality_audit",
            "fact_crm_customer_branches",
            "fact_crm_companies",
            "fact_crm_customers",
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
        """Obtiene la corrida CRM mas reciente disponible en staging."""

        sql = f"SELECT MAX(extraction_id) FROM {self._staging_schema}.stg_crm_customers"

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()

        extraction_id = row[0] if row else None
        if not extraction_id:
            raise ValueError(
                "No se encontro ninguna corrida CRM en staging para construir el mart."
            )

        return str(extraction_id)

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga todas las fechas necesarias para la corrida del mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_crm_date (
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
                SELECT created_at::DATE AS source_date
                FROM {self._staging_schema}.stg_crm_companies
                WHERE extraction_id = %s

                UNION

                SELECT created_at::DATE AS source_date
                FROM {self._staging_schema}.stg_crm_customer_branches
                WHERE extraction_id = %s
                  AND created_at IS NOT NULL
            ) dates
            ON CONFLICT (date_key) DO NOTHING
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id))
            connection.commit()

    def load_customer_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de clientes."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_crm_customer (
                source_id, full_name, first_name, last_name, identification,
                phone_number, email, address, first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                CONCAT(
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombres), '\\s+', ' ', 'g'), ''), 'Sin nombre'),
                    ' ',
                    COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(apellidos), '\\s+', ' ', 'g'), ''), 'Sin apellido')
                ),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombres), '\\s+', ' ', 'g'), ''), 'Sin nombre'),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(apellidos), '\\s+', ' ', 'g'), ''), 'Sin apellido'),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(identificacion), '\\s+', ' ', 'g'), ''), CONCAT('SIN-ID-', source_id::TEXT)),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(numero_contacto), '\\s+', ' ', 'g'), ''), 'No informado'),
                NULLIF(REGEXP_REPLACE(BTRIM(correo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(direccion_clientes), '\\s+', ' ', 'g'), ''),
                %s,
                %s
            FROM {self._staging_schema}.stg_crm_customers
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET full_name = EXCLUDED.full_name,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                identification = EXCLUDED.identification,
                phone_number = EXCLUDED.phone_number,
                email = EXCLUDED.email,
                address = EXCLUDED.address,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_company_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza la dimension de empresas."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_crm_company (
                source_id, company_name, ruc, phone_number, email, address,
                first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombre), '\\s+', ' ', 'g'), ''), CONCAT('Empresa ', source_id::TEXT)),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(ruc), '\\s+', ' ', 'g'), ''), CONCAT('SIN-RUC-', source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(telefono), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(correo), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(direccion_empresa), '\\s+', ' ', 'g'), ''),
                %s,
                %s
            FROM {self._staging_schema}.stg_crm_companies
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET company_name = EXCLUDED.company_name,
                ruc = EXCLUDED.ruc,
                phone_number = EXCLUDED.phone_number,
                email = EXCLUDED.email,
                address = EXCLUDED.address,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_customer_fact(self, extraction_id: str) -> int:
        """Carga el hecho de clientes."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_crm_customers (
                extraction_id, source_id, customer_key, has_email, has_address,
                has_phone, customer_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                dim.customer_key,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.correo), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.direccion_clientes), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.numero_contacto), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                1
            FROM {self._staging_schema}.stg_crm_customers src
            INNER JOIN {self._mart_schema}.dim_crm_customer dim
                ON dim.source_id = src.source_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET customer_key = EXCLUDED.customer_key,
                has_email = EXCLUDED.has_email,
                has_address = EXCLUDED.has_address,
                has_phone = EXCLUDED.has_phone,
                customer_count = EXCLUDED.customer_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_crm_customers")

    def load_company_fact(self, extraction_id: str) -> int:
        """Carga el hecho de empresas."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_crm_companies (
                extraction_id, source_id, company_key, created_date_key, has_phone,
                has_email, has_address, company_count, created_at
            )
            SELECT
                src.extraction_id,
                src.source_id,
                dim.company_key,
                date_dim.date_key,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.telefono), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.correo), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.direccion_empresa), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                1,
                src.created_at
            FROM {self._staging_schema}.stg_crm_companies src
            INNER JOIN {self._mart_schema}.dim_crm_company dim
                ON dim.source_id = src.source_id
            LEFT JOIN {self._mart_schema}.dim_crm_date date_dim
                ON date_dim.full_date = src.created_at::DATE
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET company_key = EXCLUDED.company_key,
                created_date_key = EXCLUDED.created_date_key,
                has_phone = EXCLUDED.has_phone,
                has_email = EXCLUDED.has_email,
                has_address = EXCLUDED.has_address,
                company_count = EXCLUDED.company_count,
                created_at = EXCLUDED.created_at
        """
        return self._execute_fact_load(sql, extraction_id, "fact_crm_companies")

    def load_customer_branch_fact(self, extraction_id: str) -> int:
        """Carga el hecho de sucursales cliente."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_crm_customer_branches (
                extraction_id, source_id, created_date_key, branch_code, branch_number,
                branch_name, province, novitec_branch_name, is_active, branch_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                date_dim.date_key,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.codigo), '\\s+', ' ', 'g'), ''), CONCAT('SIN-COD-', src.source_id::TEXT)),
                src.numero,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.nombre), '\\s+', ' ', 'g'), ''), CONCAT('Sucursal ', src.source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(src.provincia), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(src.novitec_sucursal), '\\s+', ' ', 'g'), ''),
                src.activa,
                1
            FROM {self._staging_schema}.stg_crm_customer_branches src
            LEFT JOIN {self._mart_schema}.dim_crm_date date_dim
                ON date_dim.full_date = src.created_at::DATE
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET created_date_key = EXCLUDED.created_date_key,
                branch_code = EXCLUDED.branch_code,
                branch_number = EXCLUDED.branch_number,
                branch_name = EXCLUDED.branch_name,
                province = EXCLUDED.province,
                novitec_branch_name = EXCLUDED.novitec_branch_name,
                is_active = EXCLUDED.is_active,
                branch_count = EXCLUDED.branch_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_crm_customer_branches")

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Calcula hallazgos de calidad y los registra por corrida."""

        sql = f"""
            INSERT INTO {self._mart_schema}.etl_crm_quality_audit (
                extraction_id, entity_name, rule_name, severity, affected_rows
            )
            SELECT
                %s,
                audit.entity_name,
                audit.rule_name,
                audit.severity,
                audit.affected_rows
            FROM (
                SELECT 'customers', 'cliente_sin_identificacion', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_crm_customers
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(identificacion), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'customers', 'cliente_sin_contacto', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_crm_customers
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(numero_contacto), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'companies', 'empresa_sin_ruc', 'critical', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_crm_companies
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(ruc), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'companies', 'empresa_sin_contacto', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_crm_companies
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(telefono), '\\s+', ' ', 'g'), '') IS NULL
                  AND NULLIF(REGEXP_REPLACE(BTRIM(correo), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'customer_branches', 'sucursal_sin_provincia', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_crm_customer_branches
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(provincia), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'customer_branches', 'sucursal_inactiva', 'info', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_crm_customer_branches
                WHERE extraction_id = %s
                  AND activa = FALSE
            ) audit(entity_name, rule_name, severity, affected_rows)
            ON CONFLICT (extraction_id, entity_name, rule_name) DO UPDATE
            SET severity = EXCLUDED.severity,
                affected_rows = EXCLUDED.affected_rows,
                created_at = NOW()
        """
        summary_sql = f"""
            SELECT COUNT(*)::INTEGER, COALESCE(SUM(affected_rows), 0)::INTEGER
            FROM {self._mart_schema}.etl_crm_quality_audit
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
            "Auditoria de calidad CRM actualizada | extraction_id=%s | reglas=%s | hallazgos=%s",
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
            "Hecho CRM cargado en mart | tabla=%s | extraction_id=%s | total=%s",
            table_name,
            extraction_id,
            total,
        )
        return total
