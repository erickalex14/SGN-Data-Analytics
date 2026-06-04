"""Caso de uso para cargar el dominio operativo hacia staging PostgreSQL."""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime

from novitec_dwh.contexts.operational.application.staging_contracts import (
    OperationalRawReader,
    OperationalStagingRepository,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class OperationalStagingLoadSummary:
    """Resume el resultado de la carga del dominio operativo a staging."""

    extraction_id: str
    raw_directory: str
    schema_name: str
    started_at: datetime
    finished_at: datetime | None = None
    vista_ordenes: int = 0
    vista_ordenes_chunks: int = 0
    ordenes: int = 0
    ordenes_chunks: int = 0
    ordenes_empresas: int = 0
    ordenes_empresas_chunks: int = 0
    preordenes: int = 0
    preordenes_chunks: int = 0
    orden_empresa_tecnicos: int = 0
    orden_empresa_tecnicos_chunks: int = 0


class LoadOperationalToStagingUseCase:
    """Orquesta la carga de datasets operativos desde raw hacia staging."""

    def __init__(
        self,
        raw_reader: OperationalRawReader,
        staging_repository: OperationalStagingRepository,
        schema_name: str,
    ) -> None:
        """Recibe los adaptadores necesarios para leer y cargar la corrida."""

        self._raw_reader = raw_reader
        self._staging_repository = staging_repository
        self._schema_name = schema_name

    def execute(self) -> OperationalStagingLoadSummary:
        """Ejecuta la carga completa del dominio operativo en staging."""

        started_at = datetime.now(UTC)
        self._raw_reader.prepare()
        extraction_id = self._raw_reader.extraction_id

        summary = OperationalStagingLoadSummary(
            extraction_id=extraction_id,
            raw_directory=self._raw_reader.run_directory.as_posix(),
            schema_name=self._schema_name,
            started_at=started_at,
        )

        logger.info(
            "Inicio de carga operativa a staging. Corrida raw: %s. Carpeta: %s.",
            summary.extraction_id,
            summary.raw_directory,
        )

        self._staging_repository.prepare_schema()
        self._staging_repository.prepare_extraction(extraction_id=extraction_id)

        for chunk_number, chunk in enumerate(self._raw_reader.read_order_view(), start=1):
            self._staging_repository.load_order_view(extraction_id=extraction_id, records=chunk)
            summary.vista_ordenes += len(chunk)
            summary.vista_ordenes_chunks += 1
            logger.info(
                "Lote %s de vista de ordenes cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_personal_orders(), start=1):
            self._staging_repository.load_personal_orders(extraction_id=extraction_id, records=chunk)
            summary.ordenes += len(chunk)
            summary.ordenes_chunks += 1
            logger.info(
                "Lote %s de ordenes personales cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_company_orders(), start=1):
            self._staging_repository.load_company_orders(extraction_id=extraction_id, records=chunk)
            summary.ordenes_empresas += len(chunk)
            summary.ordenes_empresas_chunks += 1
            logger.info(
                "Lote %s de ordenes empresariales cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_preorders(), start=1):
            self._staging_repository.load_preorders(extraction_id=extraction_id, records=chunk)
            summary.preordenes += len(chunk)
            summary.preordenes_chunks += 1
            logger.info(
                "Lote %s de preordenes cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(
            self._raw_reader.read_company_order_technicians(),
            start=1,
        ):
            self._staging_repository.load_company_order_technicians(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.orden_empresa_tecnicos += len(chunk)
            summary.orden_empresa_tecnicos_chunks += 1
            logger.info(
                "Lote %s de asignaciones tecnico-orden cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Carga operativa a staging finalizada. Vista ordenes: %s | Ordenes: %s | Ordenes empresas: %s | Preordenes: %s | Asignaciones tecnicos: %s.",
            summary.vista_ordenes,
            summary.ordenes,
            summary.ordenes_empresas,
            summary.preordenes,
            summary.orden_empresa_tecnicos,
        )
        return summary
