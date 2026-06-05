"""Script de arranque para la extraccion del dominio CRM."""

import logging

from novitec_dwh.contexts.crm.application.use_cases.extract_crm_domain import (
    ExtractCrmDomainUseCase,
)
from novitec_dwh.contexts.crm.infrastructure.filesystem_crm_extraction_sink import (
    FilesystemCrmExtractionSink,
)
from novitec_dwh.contexts.crm.infrastructure.mysql_crm_extraction_repository import (
    MySQLCrmExtractionRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la extraccion CRM."""

    configure_logging(log_file_name="etl_crm.log")

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

    repository = MySQLCrmExtractionRepository(
        connection_factory=mysql_connection_factory,
    )
    sink = FilesystemCrmExtractionSink(
        base_path=settings.etl_raw_base_path / "crm",
    )
    use_case = ExtractCrmDomainUseCase(repository=repository, sink=sink)

    logger.info(
        "Se iniciara la extraccion del dominio CRM con tamano de lote %s.",
        settings.etl_chunk_size,
    )
    summary = use_case.execute(chunk_size=settings.etl_chunk_size)

    logger.info(
        "Resumen final de la extraccion CRM. Clientes: %s | Empresas: %s | Sucursales cliente: %s | Carpeta raw: %s | Manifiesto: %s.",
        summary.clientes,
        summary.empresas,
        summary.sucursalescliente,
        summary.output_directory,
        summary.manifest_path,
    )


if __name__ == "__main__":
    main()
