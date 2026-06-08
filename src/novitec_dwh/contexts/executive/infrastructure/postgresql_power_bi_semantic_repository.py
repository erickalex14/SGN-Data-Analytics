"""Repositorio PostgreSQL para publicar vistas semanticas de Power BI."""

from importlib.resources import files

from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


class PostgreSQLPowerBISemanticRepository:
    """Publica vistas semanticas consolidadas sobre los marts del DWH."""

    def __init__(
        self,
        connection_factory: PostgreSQLConnectionFactory,
        semantic_schema: str,
        financial_mart_schema: str,
        operational_mart_schema: str,
        technical_mart_schema: str,
        inventory_mart_schema: str,
        crm_mart_schema: str,
        warranty_mart_schema: str,
        organizational_mart_schema: str,
    ) -> None:
        """Recibe fabrica de conexiones y nombres de schemas involucrados."""

        self._connection_factory = connection_factory
        self._semantic_schema = semantic_schema
        self._financial_mart_schema = financial_mart_schema
        self._operational_mart_schema = operational_mart_schema
        self._technical_mart_schema = technical_mart_schema
        self._inventory_mart_schema = inventory_mart_schema
        self._crm_mart_schema = crm_mart_schema
        self._warranty_mart_schema = warranty_mart_schema
        self._organizational_mart_schema = organizational_mart_schema

    def publish_views(self) -> int:
        """Crea o reemplaza las vistas semanticas de Power BI."""

        sql_template = (
            files("novitec_dwh.contexts.executive.infrastructure.sql")
            .joinpath("power_bi_semantic_views.sql")
            .read_text(encoding="utf-8")
        )
        sql_statement = (
            sql_template.replace("{semantic_schema}", self._semantic_schema)
            .replace("{financial_mart_schema}", self._financial_mart_schema)
            .replace("{operational_mart_schema}", self._operational_mart_schema)
            .replace("{technical_mart_schema}", self._technical_mart_schema)
            .replace("{inventory_mart_schema}", self._inventory_mart_schema)
            .replace("{crm_mart_schema}", self._crm_mart_schema)
            .replace("{warranty_mart_schema}", self._warranty_mart_schema)
            .replace("{organizational_mart_schema}", self._organizational_mart_schema)
        )

        with self._connection_factory.connection_scope() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql_statement)
            connection.commit()

        return 15
