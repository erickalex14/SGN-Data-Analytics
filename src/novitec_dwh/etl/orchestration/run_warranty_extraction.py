"""Script de arranque para la extraccion del dominio de garantias."""

import logging

from novitec_dwh.contexts.warranty.application.use_cases.extract_warranty_domain import (
    ExtractWarrantyDomainUseCase,
)
from novitec_dwh.contexts.warranty.infrastructure.filesystem_warranty_extraction_sink import (
    FilesystemWarrantyExtractionSink,
)
from novitec_dwh.contexts.warranty.infrastructure.mysql_warranty_extraction_repository import (
    MySQLWarrantyExtractionRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la extraccion de garantias."""

    configure_logging(log_file_name="etl_warranty.log")

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

    repository = MySQLWarrantyExtractionRepository(
        connection_factory=mysql_connection_factory,
    )
    sink = FilesystemWarrantyExtractionSink(
        base_path=settings.etl_raw_base_path / "warranty",
    )
    use_case = ExtractWarrantyDomainUseCase(repository=repository, sink=sink)

    logger.info(
        "Se iniciara la extraccion del dominio de garantias con tamano de lote %s.",
        settings.etl_chunk_size,
    )
    summary = use_case.execute(chunk_size=settings.etl_chunk_size)

    logger.info(
        "Resumen final de la extraccion de garantias. CAS: %s | Usuario CAS: %s | Ordenes personales garantia: %s | Ordenes empresa CAS: %s | Carpeta raw: %s | Manifiesto: %s.",
        summary.cas,
        summary.usuariocas,
        summary.ordenes_garantia,
        summary.ordenesempresas_garantia,
        summary.output_directory,
        summary.manifest_path,
    )


if __name__ == "__main__":
    main()
