"""Script de arranque para construir el mart de inventario en PostgreSQL."""

import logging

from novitec_dwh.contexts.inventory.application.use_cases.load_inventory_mart import (
    LoadInventoryMartUseCase,
)
from novitec_dwh.contexts.inventory.infrastructure.postgresql_inventory_mart_repository import (
    PostgreSQLInventoryMartRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga del mart de inventario."""

    configure_logging(log_file_name="etl_inventory_mart.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    mart_repository = PostgreSQLInventoryMartRepository(
        connection_factory=postgres_connection_factory,
        staging_schema=settings.postgres_inventory_staging_schema,
        mart_schema=settings.postgres_inventory_mart_schema,
    )
    extraction_id = settings.etl_inventory_extraction_id
    if not extraction_id:
        extraction_id = mart_repository.resolve_latest_extraction_id()
        logger.info(
            "No se definio ETL_INVENTORY_EXTRACTION_ID. Se usara la corrida mas reciente detectada en staging: %s.",
            extraction_id,
        )

    use_case = LoadInventoryMartUseCase(
        mart_repository=mart_repository,
        staging_schema=settings.postgres_inventory_staging_schema,
        mart_schema=settings.postgres_inventory_mart_schema,
        extraction_id=extraction_id,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de mart de inventario. Corrida: %s | Mart: %s | Repuestos: %s | Consumos orden: %s | Solicitudes: %s | Listas compra: %s | Reglas calidad: %s | Hallazgos: %s.",
        summary.extraction_id,
        summary.mart_schema,
        summary.repuestos,
        summary.consumos_orden,
        summary.solicitudes_repuesto,
        summary.listas_compra,
        summary.reglas_calidad_ejecutadas,
        summary.hallazgos_calidad,
    )
