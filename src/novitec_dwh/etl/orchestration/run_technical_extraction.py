"""Script de arranque para la extraccion del dominio tecnico."""

import logging

from novitec_dwh.contexts.technical.application.use_cases.extract_technical_domain import (
    ExtractTechnicalDomainUseCase,
)
from novitec_dwh.contexts.technical.infrastructure.filesystem_technical_extraction_sink import (
    FilesystemTechnicalExtractionSink,
)
from novitec_dwh.contexts.technical.infrastructure.mysql_technical_extraction_repository import (
    MySQLTechnicalExtractionRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging
from novitec_dwh.shared.infrastructure.mysql import MySQLConnectionFactory
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def main() -> None:
    """Ensambla dependencias y ejecuta la extraccion tecnica."""

    configure_logging(log_file_name="etl_technical.log")

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

    repository = MySQLTechnicalExtractionRepository(
        connection_factory=mysql_connection_factory,
    )
    sink = FilesystemTechnicalExtractionSink(
        base_path=settings.etl_raw_base_path / "technical",
    )
    use_case = ExtractTechnicalDomainUseCase(repository=repository, sink=sink)

    logger.info(
        "Se iniciara la extraccion del dominio tecnico con tamano de lote %s.",
        settings.etl_chunk_size,
    )
    summary = use_case.execute(chunk_size=settings.etl_chunk_size)

    logger.info(
        "Resumen final de la extraccion tecnica. Informes: %s | Fotos: %s | Equipos: %s | Series: %s | Tipos dispositivo: %s | Tipos servicio: %s | Marcas: %s | Credenciales: %s | Carpeta raw: %s | Manifiesto: %s.",
        summary.informes,
        summary.informefotos,
        summary.equipos,
        summary.equiposseries,
        summary.tiposdispositivo,
        summary.tiposservicio,
        summary.marcas,
        summary.credencialesequipo,
        summary.output_directory,
        summary.manifest_path,
    )


if __name__ == "__main__":
    main()
