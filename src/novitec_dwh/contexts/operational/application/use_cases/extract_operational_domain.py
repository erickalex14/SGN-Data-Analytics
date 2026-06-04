"""Caso de uso para extraer el dominio operativo completo."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from novitec_dwh.contexts.operational.application.contracts import OperationalExtractionSink
from novitec_dwh.contexts.operational.application.dto import OperationalExtractionSummary
from novitec_dwh.contexts.operational.domain.repositories import OperationalExtractionRepository

logger = logging.getLogger(__name__)


class ExtractOperationalDomainUseCase:
    """Orquesta la extraccion de las tablas operativas priorizadas."""

    def __init__(
        self,
        repository: OperationalExtractionRepository,
        sink: OperationalExtractionSink,
    ) -> None:
        """Recibe el repositorio concreto que conoce el origen de datos."""

        self._repository = repository
        self._sink = sink

    def execute(self, chunk_size: int) -> OperationalExtractionSummary:
        """Ejecuta la extraccion completa y devuelve un resumen de volumen."""

        started_at = datetime.now(UTC)
        extraction_id = started_at.strftime("operational_%Y%m%d_%H%M%S")
        summary = OperationalExtractionSummary(
            extraction_id=extraction_id,
            started_at=started_at,
        )

        self._sink.start(extraction_id=extraction_id, started_at=started_at)

        if self._sink.run_directory is not None:
            summary.output_directory = str(self._sink.run_directory)

        logger.info("Inicio de extraccion del dominio operativo. Corrida: %s.", extraction_id)

        self._process_dataset(
            dataset_name="vista_ordenes",
            chunk_iterator=self._repository.extract_order_view(chunk_size=chunk_size),
            summary=summary,
            records_field="vista_ordenes",
            chunks_field="vista_ordenes_chunks",
            log_label="vista consolidada de ordenes",
        )
        self._process_dataset(
            dataset_name="ordenes",
            chunk_iterator=self._repository.extract_personal_orders(chunk_size=chunk_size),
            summary=summary,
            records_field="ordenes",
            chunks_field="ordenes_chunks",
            log_label="ordenes personales",
        )
        self._process_dataset(
            dataset_name="ordenes_empresas",
            chunk_iterator=self._repository.extract_company_orders(chunk_size=chunk_size),
            summary=summary,
            records_field="ordenes_empresas",
            chunks_field="ordenes_empresas_chunks",
            log_label="ordenes empresariales",
        )
        self._process_dataset(
            dataset_name="preordenes",
            chunk_iterator=self._repository.extract_preorders(chunk_size=chunk_size),
            summary=summary,
            records_field="preordenes",
            chunks_field="preordenes_chunks",
            log_label="preordenes",
        )
        self._process_dataset(
            dataset_name="orden_empresa_tecnicos",
            chunk_iterator=self._repository.extract_company_order_technicians(chunk_size=chunk_size),
            summary=summary,
            records_field="orden_empresa_tecnicos",
            chunks_field="orden_empresa_tecnicos_chunks",
            log_label="asignaciones tecnico-orden empresarial",
        )

        summary.finished_at = datetime.now(UTC)
        self._sink.finalize(summary=summary)

        if self._sink.manifest_path is not None:
            summary.manifest_path = str(self._sink.manifest_path)

        logger.info(
            "Extraccion operativa finalizada. Vista ordenes: %s | Ordenes: %s | Ordenes empresas: %s | Preordenes: %s | Asignaciones tecnicos: %s.",
            summary.vista_ordenes,
            summary.ordenes,
            summary.ordenes_empresas,
            summary.preordenes,
            summary.orden_empresa_tecnicos,
        )
        return summary

    def _process_dataset(
        self,
        dataset_name: str,
        chunk_iterator: Any,
        summary: OperationalExtractionSummary,
        records_field: str,
        chunks_field: str,
        log_label: str,
    ) -> None:
        """Procesa un conjunto de datos en bloques y los persiste en la zona raw."""

        chunk_number = 0
        for chunk in chunk_iterator:
            chunk_number += 1
            setattr(summary, records_field, getattr(summary, records_field) + len(chunk))
            setattr(summary, chunks_field, getattr(summary, chunks_field) + 1)
            output_file = self._sink.write(
                dataset_name=dataset_name,
                chunk_number=chunk_number,
                records=chunk,
            )
            logger.info(
                "Lote %s de %s extraido y persistido correctamente. Registros: %s. Archivo: %s.",
                chunk_number,
                log_label,
                len(chunk),
                Path(output_file).as_posix(),
            )
