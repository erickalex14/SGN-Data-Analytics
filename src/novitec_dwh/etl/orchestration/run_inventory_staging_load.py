"""Script de arranque para cargar el dominio de inventario a staging PostgreSQL."""

import logging

from novitec_dwh.contexts.inventory.application.use_cases.load_inventory_to_staging import (
    LoadInventoryToStagingUseCase,
)
from novitec_dwh.contexts.inventory.infrastructure.filesystem_inventory_raw_reader import (
    FilesystemInventoryRawReader,
)
from novitec_dwh.contexts.inventory.infrastructure.postgresql_inventory_staging_repository import (
    PostgreSQLInventoryStagingRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la carga de inventario a staging."""

    configure_logging(log_file_name="etl_inventory_staging.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    raw_reader = FilesystemInventoryRawReader(
        base_path=settings.etl_raw_base_path / "inventory",
        extraction_id=settings.etl_inventory_extraction_id,
    )
    staging_repository = PostgreSQLInventoryStagingRepository(
        connection_factory=postgres_connection_factory,
        schema_name=settings.postgres_inventory_staging_schema,
    )
    use_case = LoadInventoryToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name=settings.postgres_inventory_staging_schema,
    )

    summary = use_case.execute()

    logger.info(
        "Resumen final de carga de inventario a staging. Corrida: %s | Schema: %s | Repuestos: %s | Productos inventario: %s | Orden repuestos: %s | Solicitudes repuesto: %s | Listas compra: %s.",
        summary.extraction_id,
        summary.schema_name,
        summary.repuestos,
        summary.productosinventario,
        summary.orden_repuestos,
        summary.solicitudesrepuesto,
        summary.listascompra,
    )
