"""Repositorio PostgreSQL para construir mart organizacional."""

from importlib.resources import files
import logging

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory

logger = logging.getLogger(__name__)


class PostgreSQLOrganizationalMartRepository:
    """Construye dimensiones, hechos y auditoria del mart organizacional."""

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
        """Crea schema analitico y tablas si no existen."""

        ddl_template = (
            files("novitec_dwh.contexts.organizational.infrastructure.sql")
            .joinpath("organizational_mart.sql")
            .read_text(encoding="utf-8")
        )
        ddl_statement = ddl_template.replace("{mart_schema}", self._mart_schema)

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(ddl_statement)
            connection.commit()

    def prepare_extraction(self, extraction_id: str) -> None:
        """Elimina datos previos de misma corrida para soportar reprocesos."""

        tables = [
            "etl_organizational_quality_audit",
            "fact_organizational_user_permissions",
            "fact_organizational_group_permissions",
            "fact_organizational_user_branches",
            "fact_organizational_users",
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
        """Obtiene corrida organizacional mas reciente disponible en staging."""

        sql = f"SELECT MAX(extraction_id) FROM {self._staging_schema}.stg_organizational_users"

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                row = cursor.fetchone()

        extraction_id = row[0] if row else None
        if not extraction_id:
            raise ValueError(
                "No se encontro ninguna corrida organizacional en staging para construir el mart."
            )

        return str(extraction_id)

    def load_date_dimension(self, extraction_id: str) -> None:
        """Carga fechas necesarias para corrida del mart."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_organizational_date (
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
                FROM {self._staging_schema}.stg_organizational_access_groups
                WHERE extraction_id = %s

                UNION

                SELECT created_at::DATE AS source_date
                FROM {self._staging_schema}.stg_organizational_user_permissions
                WHERE extraction_id = %s
            ) dates
            ON CONFLICT (date_key) DO NOTHING
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id))
            connection.commit()

    def load_branch_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza dimension de sucursales propias."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_organizational_branch (
                source_id, branch_number, city_name, sequential_code, base_number,
                first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                nro_sucursal,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(ciudad), '\\s+', ' ', 'g'), ''), 'No informado'),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(secuencial), '\\s+', ' ', 'g'), ''), 'No informado'),
                NULLIF(REGEXP_REPLACE(BTRIM(nro_base), '\\s+', ' ', 'g'), ''),
                %s,
                %s
            FROM {self._staging_schema}.stg_organizational_branches
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET branch_number = EXCLUDED.branch_number,
                city_name = EXCLUDED.city_name,
                sequential_code = EXCLUDED.sequential_code,
                base_number = EXCLUDED.base_number,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_role_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza dimension de roles."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_organizational_role (
                source_id, role_name, first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(rol), '\\s+', ' ', 'g'), ''), CONCAT('ROL-', source_id::TEXT)),
                %s,
                %s
            FROM {self._staging_schema}.stg_organizational_roles
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET role_name = EXCLUDED.role_name,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_access_group_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza dimension de grupos de acceso."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_organizational_access_group (
                source_id, group_name, description, is_superadmin, created_date_key,
                first_extraction_id, last_extraction_id
            )
            SELECT
                src.source_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.nombre), '\\s+', ' ', 'g'), ''), CONCAT('GRUPO-', src.source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(src.descripcion), '\\s+', ' ', 'g'), ''),
                src.es_superadmin,
                dim_date.date_key,
                %s,
                %s
            FROM {self._staging_schema}.stg_organizational_access_groups src
            LEFT JOIN {self._mart_schema}.dim_organizational_date dim_date
                ON dim_date.full_date = src.created_at::DATE
            WHERE src.extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET group_name = EXCLUDED.group_name,
                description = EXCLUDED.description,
                is_superadmin = EXCLUDED.is_superadmin,
                created_date_key = EXCLUDED.created_date_key,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_user_dimension(self, extraction_id: str) -> None:
        """Carga y actualiza dimension de usuarios."""

        sql = f"""
            INSERT INTO {self._mart_schema}.dim_organizational_user (
                source_id, user_login, user_name, phone_number, email,
                first_extraction_id, last_extraction_id
            )
            SELECT
                source_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(usuario), '\\s+', ' ', 'g'), ''), CONCAT('USR-', source_id::TEXT)),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(nombre_tecnico), '\\s+', ' ', 'g'), ''), CONCAT('Usuario ', source_id::TEXT)),
                NULLIF(REGEXP_REPLACE(BTRIM(telefono), '\\s+', ' ', 'g'), ''),
                NULLIF(REGEXP_REPLACE(BTRIM(correo_tec), '\\s+', ' ', 'g'), ''),
                %s,
                %s
            FROM {self._staging_schema}.stg_organizational_users
            WHERE extraction_id = %s
            ON CONFLICT (source_id) DO UPDATE
            SET user_login = EXCLUDED.user_login,
                user_name = EXCLUDED.user_name,
                phone_number = EXCLUDED.phone_number,
                email = EXCLUDED.email,
                last_extraction_id = EXCLUDED.last_extraction_id,
                updated_at = NOW()
        """

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, (extraction_id, extraction_id, extraction_id))
            connection.commit()

    def load_user_fact(self, extraction_id: str) -> int:
        """Carga hecho principal de usuarios."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_organizational_users (
                extraction_id, source_id, user_key, role_key, branch_key, access_group_key,
                has_phone, has_email, can_access_nc, is_active, has_access_group, user_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                usr.user_key,
                rol.role_key,
                suc.branch_key,
                grp.access_group_key,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.telefono), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                CASE WHEN NULLIF(REGEXP_REPLACE(BTRIM(src.correo_tec), '\\s+', ' ', 'g'), '') IS NOT NULL THEN TRUE ELSE FALSE END,
                src.acceso_nc,
                src.activo,
                CASE WHEN src.grupo_id IS NOT NULL THEN TRUE ELSE FALSE END,
                1
            FROM {self._staging_schema}.stg_organizational_users src
            INNER JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.source_id = src.source_id
            LEFT JOIN {self._mart_schema}.dim_organizational_role rol
                ON rol.source_id = src.rol_id
            LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                ON suc.source_id = src.sucursal_id
            LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                ON grp.source_id = src.grupo_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET user_key = EXCLUDED.user_key,
                role_key = EXCLUDED.role_key,
                branch_key = EXCLUDED.branch_key,
                access_group_key = EXCLUDED.access_group_key,
                has_phone = EXCLUDED.has_phone,
                has_email = EXCLUDED.has_email,
                can_access_nc = EXCLUDED.can_access_nc,
                is_active = EXCLUDED.is_active,
                has_access_group = EXCLUDED.has_access_group,
                user_count = EXCLUDED.user_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_organizational_users")

    def load_user_branch_fact(self, extraction_id: str) -> int:
        """Carga hecho de asignaciones usuario sucursal."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_organizational_user_branches (
                extraction_id, source_id, user_key, branch_key, user_id, branch_id, assignment_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                usr.user_key,
                suc.branch_key,
                src.usuario_id,
                src.sucursal_id,
                1
            FROM {self._staging_schema}.stg_organizational_user_branches src
            LEFT JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.source_id = src.usuario_id
            LEFT JOIN {self._mart_schema}.dim_organizational_branch suc
                ON suc.source_id = src.sucursal_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET user_key = EXCLUDED.user_key,
                branch_key = EXCLUDED.branch_key,
                user_id = EXCLUDED.user_id,
                branch_id = EXCLUDED.branch_id,
                assignment_count = EXCLUDED.assignment_count
        """
        return self._execute_fact_load(sql, extraction_id, "fact_organizational_user_branches")

    def load_group_permission_fact(self, extraction_id: str) -> int:
        """Carga hecho de permisos de grupo."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_organizational_group_permissions (
                extraction_id, source_id, access_group_key, group_id, module_name,
                action_name, is_allowed, permission_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                grp.access_group_key,
                src.grupo_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.modulo), '\\s+', ' ', 'g'), ''), 'modulo_no_informado'),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.accion), '\\s+', ' ', 'g'), ''), 'accion_no_informada'),
                src.permitido,
                1
            FROM {self._staging_schema}.stg_organizational_group_permissions src
            LEFT JOIN {self._mart_schema}.dim_organizational_access_group grp
                ON grp.source_id = src.grupo_id
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET access_group_key = EXCLUDED.access_group_key,
                group_id = EXCLUDED.group_id,
                module_name = EXCLUDED.module_name,
                action_name = EXCLUDED.action_name,
                is_allowed = EXCLUDED.is_allowed,
                permission_count = EXCLUDED.permission_count
        """
        return self._execute_fact_load(
            sql,
            extraction_id,
            "fact_organizational_group_permissions",
        )

    def load_user_permission_fact(self, extraction_id: str) -> int:
        """Carga hecho de permisos de usuario."""

        sql = f"""
            INSERT INTO {self._mart_schema}.fact_organizational_user_permissions (
                extraction_id, source_id, user_key, created_date_key, user_id, module_name,
                action_name, is_allowed, permission_count
            )
            SELECT
                src.extraction_id,
                src.source_id,
                usr.user_key,
                dim_date.date_key,
                src.usuario_id,
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.modulo), '\\s+', ' ', 'g'), ''), 'modulo_no_informado'),
                COALESCE(NULLIF(REGEXP_REPLACE(BTRIM(src.accion), '\\s+', ' ', 'g'), ''), 'accion_no_informada'),
                src.permitido,
                1
            FROM {self._staging_schema}.stg_organizational_user_permissions src
            LEFT JOIN {self._mart_schema}.dim_organizational_user usr
                ON usr.source_id = src.usuario_id
            LEFT JOIN {self._mart_schema}.dim_organizational_date dim_date
                ON dim_date.full_date = src.created_at::DATE
            WHERE src.extraction_id = %s
            ON CONFLICT (extraction_id, source_id) DO UPDATE
            SET user_key = EXCLUDED.user_key,
                created_date_key = EXCLUDED.created_date_key,
                user_id = EXCLUDED.user_id,
                module_name = EXCLUDED.module_name,
                action_name = EXCLUDED.action_name,
                is_allowed = EXCLUDED.is_allowed,
                permission_count = EXCLUDED.permission_count
        """
        return self._execute_fact_load(
            sql,
            extraction_id,
            "fact_organizational_user_permissions",
        )

    def refresh_quality_audit(self, extraction_id: str) -> tuple[int, int]:
        """Calcula hallazgos de calidad y los registra por corrida."""

        sql = f"""
            INSERT INTO {self._mart_schema}.etl_organizational_quality_audit (
                extraction_id, entity_name, rule_name, severity, affected_rows
            )
            SELECT
                %s,
                audit.entity_name,
                audit.rule_name,
                audit.severity,
                audit.affected_rows
            FROM (
                SELECT 'users', 'usuario_sin_contacto', 'warning', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_organizational_users
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(telefono), '\\s+', ' ', 'g'), '') IS NULL
                  AND NULLIF(REGEXP_REPLACE(BTRIM(correo_tec), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'users', 'usuario_inactivo_con_acceso_nc', 'critical', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_organizational_users
                WHERE extraction_id = %s
                  AND activo = FALSE
                  AND acceso_nc = TRUE

                UNION ALL
                SELECT 'users', 'usuario_sin_grupo_acceso', 'info', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_organizational_users
                WHERE extraction_id = %s
                  AND grupo_id IS NULL

                UNION ALL
                SELECT 'access_groups', 'grupo_sin_descripcion', 'info', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_organizational_access_groups
                WHERE extraction_id = %s
                  AND NULLIF(REGEXP_REPLACE(BTRIM(descripcion), '\\s+', ' ', 'g'), '') IS NULL

                UNION ALL
                SELECT 'user_permissions', 'permiso_usuario_no_permitido', 'info', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_organizational_user_permissions
                WHERE extraction_id = %s
                  AND permitido = FALSE

                UNION ALL
                SELECT 'group_permissions', 'permiso_grupo_no_permitido', 'info', COUNT(*)::INTEGER
                FROM {self._staging_schema}.stg_organizational_group_permissions
                WHERE extraction_id = %s
                  AND permitido = FALSE
            ) audit(entity_name, rule_name, severity, affected_rows)
            ON CONFLICT (extraction_id, entity_name, rule_name) DO UPDATE
            SET severity = EXCLUDED.severity,
                affected_rows = EXCLUDED.affected_rows,
                created_at = NOW()
        """
        summary_sql = f"""
            SELECT COUNT(*)::INTEGER, COALESCE(SUM(affected_rows), 0)::INTEGER
            FROM {self._mart_schema}.etl_organizational_quality_audit
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
            "Auditoria de calidad organizacional actualizada | extraction_id=%s | reglas=%s | hallazgos=%s",
            extraction_id,
            row[0],
            row[1],
        )
        return int(row[0]), int(row[1])

    def _execute_fact_load(self, sql: str, extraction_id: str, table_name: str) -> int:
        """Ejecuta carga de hecho y devuelve total final de corrida."""

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
            "Hecho organizacional cargado en mart | tabla=%s | extraction_id=%s | total=%s",
            table_name,
            extraction_id,
            total,
        )
        return total
