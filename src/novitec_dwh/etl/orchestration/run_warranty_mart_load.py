"""Script de arranque para construir el mart de garantias en PostgreSQL."""

import logging

from novitec_dwh.contexts.warranty.application.use_cases.load_warranty_mart import (
    LoadWarrantyMartUseCase,
)
from novitec_dwh.contexts.warranty.infrastructure.postgresql_warranty_mart_repository import (
    PostgreSQLWarrantyMartRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga del mart de garantias."""

    configure_logging(log_file_name="etl_warranty_mart.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    mart_repository = PostgreSQLWarrantyMartRepository(
        connection_factory=postgres_connection_factory,
        staging_schema=settings.postgres_warranty_staging_schema,
        mart_schema=settings.postgres_warranty_mart_schema,
    )
    extraction_id = settings.etl_warranty_extraction_id
    if not extraction_id:
        extraction_id = mart_repository.resolve_latest_extraction_id()
        logger.info(
            "No se definio ETL_WARRANTY_EXTRACTION_ID. Se usara la corrida mas reciente detectada en staging: %s.",
            extraction_id,
        )

    use_case = LoadWarrantyMartUseCase(
        mart_repository=mart_repository,
        staging_schema=settings.postgres_warranty_staging_schema,
        mart_schema=settings.postgres_warranty_mart_schema,
        extraction_id=extraction_id,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de mart de garantias. Corrida: %s | Mart: %s | Ordenes personales: %s | Ordenes empresariales: %s | Asignaciones usuario CAS: %s | Reglas calidad: %s | Hallazgos: %s.",
        summary.extraction_id,
        summary.mart_schema,
        summary.ordenes_personales,
        summary.ordenes_empresariales,
        summary.asignaciones_usuario_cas,
        summary.reglas_calidad_ejecutadas,
        summary.hallazgos_calidad,
    )
