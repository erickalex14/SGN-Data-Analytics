"""Script de arranque para construir mart organizacional en PostgreSQL."""

import logging

from novitec_dwh.contexts.organizational.application.use_cases.load_organizational_mart import (
    LoadOrganizationalMartUseCase,
)
from novitec_dwh.contexts.organizational.infrastructure.postgresql_organizational_mart_repository import (
    PostgreSQLOrganizationalMartRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta carga del mart organizacional."""

    configure_logging(log_file_name="etl_organizational_mart.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    mart_repository = PostgreSQLOrganizationalMartRepository(
        connection_factory=postgres_connection_factory,
        staging_schema=settings.postgres_organizational_staging_schema,
        mart_schema=settings.postgres_organizational_mart_schema,
    )
    extraction_id = settings.etl_organizational_extraction_id
    if not extraction_id:
        extraction_id = mart_repository.resolve_latest_extraction_id()
        logger.info(
            "No se definio ETL_ORGANIZATIONAL_EXTRACTION_ID. Se usara la corrida mas reciente detectada en staging: %s.",
            extraction_id,
        )

    use_case = LoadOrganizationalMartUseCase(
        mart_repository=mart_repository,
        staging_schema=settings.postgres_organizational_staging_schema,
        mart_schema=settings.postgres_organizational_mart_schema,
        extraction_id=extraction_id,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de mart organizacional. Corrida: %s | Mart: %s | Usuarios: %s | Usuario sucursal: %s | Permisos grupo: %s | Permisos usuario: %s | Reglas calidad: %s | Hallazgos: %s.",
        summary.extraction_id,
        summary.mart_schema,
        summary.usuarios,
        summary.usuarios_sucursales,
        summary.permisos_grupo,
        summary.permisos_usuario,
        summary.reglas_calidad_ejecutadas,
        summary.hallazgos_calidad,
    )
