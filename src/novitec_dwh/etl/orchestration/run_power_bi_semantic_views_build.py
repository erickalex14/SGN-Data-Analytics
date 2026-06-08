"""Script de arranque para publicar vistas semanticas de Power BI."""

import logging

from novitec_dwh.contexts.executive.application.use_cases.build_semantic_views import (
    BuildSemanticViewsUseCase,
)
from novitec_dwh.contexts.executive.infrastructure.postgresql_power_bi_semantic_repository import (
    PostgreSQLPowerBISemanticRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y publica las vistas semanticas para Power BI."""

    configure_logging(log_file_name="etl_power_bi_semantic.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    repository = PostgreSQLPowerBISemanticRepository(
        connection_factory=postgres_connection_factory,
        semantic_schema=settings.postgres_semantic_schema,
        financial_mart_schema=settings.postgres_financial_mart_schema,
        operational_mart_schema=settings.postgres_operational_mart_schema,
        technical_mart_schema=settings.postgres_technical_mart_schema,
        inventory_mart_schema=settings.postgres_inventory_mart_schema,
        crm_mart_schema=settings.postgres_crm_mart_schema,
        warranty_mart_schema=settings.postgres_warranty_mart_schema,
        organizational_mart_schema=settings.postgres_organizational_mart_schema,
    )
    use_case = BuildSemanticViewsUseCase(
        repository=repository,
        semantic_schema=settings.postgres_semantic_schema,
    )
    summary = use_case.execute()

    logger.info(
        "Resumen final de vistas semanticas. Schema: %s | Vistas publicadas: %s.",
        summary.semantic_schema,
        summary.published_views,
    )
