"""Caso de uso para cargar el dominio CRM hacia staging PostgreSQL."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.crm.application.dto import CrmStagingLoadSummary
from novitec_dwh.contexts.crm.application.staging_contracts import (
    CrmRawReader,
    CrmStagingRepository,
)

logger = logging.getLogger(__name__)


class LoadCrmToStagingUseCase:
    """Orquesta la carga de datasets CRM desde raw hacia staging."""

    def __init__(
        self,
        raw_reader: CrmRawReader,
        staging_repository: CrmStagingRepository,
        schema_name: str,
    ) -> None:
        """Recibe los adaptadores necesarios para leer y cargar la corrida."""

        self._raw_reader = raw_reader
        self._staging_repository = staging_repository
        self._schema_name = schema_name

    def execute(self) -> CrmStagingLoadSummary:
        """Ejecuta la carga completa del dominio CRM en staging."""

        started_at = datetime.now(UTC)
        self._raw_reader.prepare()
        extraction_id = self._raw_reader.extraction_id

        summary = CrmStagingLoadSummary(
            extraction_id=extraction_id,
            raw_directory=self._raw_reader.run_directory.as_posix(),
            schema_name=self._schema_name,
            started_at=started_at,
        )

        logger.info(
            "Inicio de carga de CRM a staging. Corrida raw: %s. Carpeta: %s.",
            summary.extraction_id,
            summary.raw_directory,
        )

        self._staging_repository.prepare_schema()
        self._staging_repository.prepare_extraction(extraction_id=extraction_id)

        for chunk_number, chunk in enumerate(self._raw_reader.read_customers(), start=1):
            self._staging_repository.load_customers(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.clientes += len(chunk)
            summary.clientes_chunks += 1
            logger.info(
                "Lote %s de clientes cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_companies(), start=1):
            self._staging_repository.load_companies(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.empresas += len(chunk)
            summary.empresas_chunks += 1
            logger.info(
                "Lote %s de empresas cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(
            self._raw_reader.read_customer_branches(),
            start=1,
        ):
            self._staging_repository.load_customer_branches(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.sucursalescliente += len(chunk)
            summary.sucursalescliente_chunks += 1
            logger.info(
                "Lote %s de sucursales cliente cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Carga de CRM a staging finalizada. Clientes: %s | Empresas: %s | Sucursales cliente: %s.",
            summary.clientes,
            summary.empresas,
            summary.sucursalescliente,
        )
        return summary
