"""Caso de uso para extraer el dominio CRM completo."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from novitec_dwh.contexts.crm.application.contracts import CrmExtractionSink
from novitec_dwh.contexts.crm.application.dto import CrmExtractionSummary
from novitec_dwh.contexts.crm.domain.repositories import CrmExtractionRepository

logger = logging.getLogger(__name__)


class ExtractCrmDomainUseCase:
    """Orquesta la extraccion de las tablas CRM priorizadas."""

    def __init__(
        self,
        repository: CrmExtractionRepository,
        sink: CrmExtractionSink,
    ) -> None:
        """Recibe el repositorio concreto que conoce el origen de datos."""

        self._repository = repository
        self._sink = sink

    def execute(self, chunk_size: int) -> CrmExtractionSummary:
        """Ejecuta la extraccion completa y devuelve un resumen de volumen."""

        started_at = datetime.now(UTC)
        extraction_id = started_at.strftime("crm_%Y%m%d_%H%M%S")
        summary = CrmExtractionSummary(
            extraction_id=extraction_id,
            started_at=started_at,
        )

        self._sink.start(extraction_id=extraction_id, started_at=started_at)

        if self._sink.run_directory is not None:
            summary.output_directory = str(self._sink.run_directory)

        logger.info("Inicio de extraccion del dominio CRM. Corrida: %s.", extraction_id)

        self._process_dataset(
            dataset_name="clientes",
            chunk_iterator=self._repository.extract_customers(chunk_size=chunk_size),
            summary=summary,
            records_field="clientes",
            chunks_field="clientes_chunks",
            log_label="clientes finales",
        )
        self._process_dataset(
            dataset_name="empresas",
            chunk_iterator=self._repository.extract_companies(chunk_size=chunk_size),
            summary=summary,
            records_field="empresas",
            chunks_field="empresas_chunks",
            log_label="empresas",
        )
        self._process_dataset(
            dataset_name="sucursalescliente",
            chunk_iterator=self._repository.extract_customer_branches(chunk_size=chunk_size),
            summary=summary,
            records_field="sucursalescliente",
            chunks_field="sucursalescliente_chunks",
            log_label="sucursales cliente",
        )

        summary.finished_at = datetime.now(UTC)
        self._sink.finalize(summary=summary)

        if self._sink.manifest_path is not None:
            summary.manifest_path = str(self._sink.manifest_path)

        logger.info(
            "Extraccion CRM finalizada. Clientes: %s | Empresas: %s | Sucursales cliente: %s.",
            summary.clientes,
            summary.empresas,
            summary.sucursalescliente,
        )
        return summary

    def _process_dataset(
        self,
        dataset_name: str,
        chunk_iterator: Any,
        summary: CrmExtractionSummary,
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
