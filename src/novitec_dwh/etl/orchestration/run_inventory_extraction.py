"""Script de arranque para la extraccion del dominio de inventario."""

import logging

from novitec_dwh.contexts.inventory.application.use_cases.extract_inventory_domain import (
    ExtractInventoryDomainUseCase,
)
from novitec_dwh.contexts.inventory.infrastructure.filesystem_inventory_extraction_sink import (
    FilesystemInventoryExtractionSink,
)
from novitec_dwh.contexts.inventory.infrastructure.mysql_inventory_extraction_repository import (
    MySQLInventoryExtractionRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la extraccion de inventario."""

    configure_logging(log_file_name="etl_inventory.log")

    settings = get_settings()
    logger = logging.getLogger(__name__)

    mysql_connection_factory = MySQLConnectionFactory(settings=settings)
    postgres_connection_factory = PostgreSQLConnectionFactory(settings=settings)

    logger.info("Se iniciara la validacion de conectividad a MySQL origen.")
    mysql_connection_factory.test_connection()
    logger.info("La conectividad con MySQL origen fue validada correctamente.")

    logger.info("Se iniciara la validacion de conectividad a PostgreSQL destino.")
    postgres_connection_factory.test_connection()
    logger.info("La conectividad con PostgreSQL destino fue validada correctamente.")

    repository = MySQLInventoryExtractionRepository(
        connection_factory=mysql_connection_factory,
    )
    sink = FilesystemInventoryExtractionSink(
        base_path=settings.etl_raw_base_path / "inventory",
    )
    use_case = ExtractInventoryDomainUseCase(repository=repository, sink=sink)

    logger.info(
        "Se iniciara la extraccion del dominio de inventario con tamano de lote %s.",
        settings.etl_chunk_size,
    )
    summary = use_case.execute(chunk_size=settings.etl_chunk_size)

    logger.info(
        "Resumen final de la extraccion de inventario. Repuestos: %s | Productos inventario: %s | Orden repuestos: %s | Solicitudes repuesto: %s | Listas compra: %s | Carpeta raw: %s | Manifiesto: %s.",
        summary.repuestos,
        summary.productosinventario,
        summary.orden_repuestos,
        summary.solicitudesrepuesto,
        summary.listascompra,
        summary.output_directory,
        summary.manifest_path,
    )


if __name__ == "__main__":
    main()
