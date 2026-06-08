"""Caso de uso para cargar el dominio de garantias hacia staging PostgreSQL."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.warranty.application.dto import WarrantyStagingLoadSummary
from novitec_dwh.contexts.warranty.application.staging_contracts import (
    WarrantyRawReader,
    WarrantyStagingRepository,
)

logger = logging.getLogger(__name__)


class LoadWarrantyToStagingUseCase:
    """Orquesta la carga de datasets de garantias desde raw hacia staging."""

    def __init__(
        self,
        raw_reader: WarrantyRawReader,
        staging_repository: WarrantyStagingRepository,
        schema_name: str,
    ) -> None:
        """Recibe los adaptadores necesarios para leer y cargar la corrida."""

        self._raw_reader = raw_reader
        self._staging_repository = staging_repository
        self._schema_name = schema_name

    def execute(self) -> WarrantyStagingLoadSummary:
        """Ejecuta la carga completa del dominio de garantias en staging."""

        started_at = datetime.now(UTC)
        self._raw_reader.prepare()
        extraction_id = self._raw_reader.extraction_id

        summary = WarrantyStagingLoadSummary(
            extraction_id=extraction_id,
            raw_directory=self._raw_reader.run_directory.as_posix(),
            schema_name=self._schema_name,
            started_at=started_at,
        )

        logger.info(
            "Inicio de carga de garantias a staging. Corrida raw: %s. Carpeta: %s.",
            summary.extraction_id,
            summary.raw_directory,
        )

        self._staging_repository.prepare_schema()
        self._staging_repository.prepare_extraction(extraction_id=extraction_id)

        for chunk_number, chunk in enumerate(self._raw_reader.read_service_centers(), start=1):
            self._staging_repository.load_service_centers(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.cas += len(chunk)
            summary.cas_chunks += 1
            logger.info(
                "Lote %s de CAS cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_user_assignments(), start=1):
            self._staging_repository.load_user_assignments(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.usuariocas += len(chunk)
            summary.usuariocas_chunks += 1
            logger.info(
                "Lote %s de usuario CAS cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(
            self._raw_reader.read_personal_warranty_orders(),
            start=1,
        ):
            self._staging_repository.load_personal_warranty_orders(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.ordenes_garantia += len(chunk)
            summary.ordenes_garantia_chunks += 1
            logger.info(
                "Lote %s de ordenes personales con garantia cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(
            self._raw_reader.read_company_warranty_orders(),
            start=1,
        ):
            self._staging_repository.load_company_warranty_orders(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.ordenesempresas_garantia += len(chunk)
            summary.ordenesempresas_garantia_chunks += 1
            logger.info(
                "Lote %s de ordenes empresariales con CAS cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Carga de garantias a staging finalizada. CAS: %s | Usuario CAS: %s | Ordenes personales garantia: %s | Ordenes empresa CAS: %s.",
            summary.cas,
            summary.usuariocas,
            summary.ordenes_garantia,
            summary.ordenesempresas_garantia,
        )
        return summary
