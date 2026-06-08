"""Caso de uso para extraer el dominio de garantias completo."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from novitec_dwh.contexts.warranty.application.contracts import WarrantyExtractionSink
from novitec_dwh.contexts.warranty.application.dto import WarrantyExtractionSummary
from novitec_dwh.contexts.warranty.domain.repositories import WarrantyExtractionRepository

logger = logging.getLogger(__name__)


class ExtractWarrantyDomainUseCase:
    """Orquesta la extraccion de las tablas de garantias priorizadas."""

    def __init__(
        self,
        repository: WarrantyExtractionRepository,
        sink: WarrantyExtractionSink,
    ) -> None:
        """Recibe el repositorio concreto que conoce el origen de datos."""

        self._repository = repository
        self._sink = sink

    def execute(self, chunk_size: int) -> WarrantyExtractionSummary:
        """Ejecuta la extraccion completa y devuelve un resumen de volumen."""

        started_at = datetime.now(UTC)
        extraction_id = started_at.strftime("warranty_%Y%m%d_%H%M%S")
        summary = WarrantyExtractionSummary(
            extraction_id=extraction_id,
            started_at=started_at,
        )

        self._sink.start(extraction_id=extraction_id, started_at=started_at)

        if self._sink.run_directory is not None:
            summary.output_directory = str(self._sink.run_directory)

        logger.info("Inicio de extraccion del dominio de garantias. Corrida: %s.", extraction_id)

        self._process_dataset(
            dataset_name="cas",
            chunk_iterator=self._repository.extract_service_centers(chunk_size=chunk_size),
            summary=summary,
            records_field="cas",
            chunks_field="cas_chunks",
            log_label="centros autorizados de servicio",
        )
        self._process_dataset(
            dataset_name="usuariocas",
            chunk_iterator=self._repository.extract_user_assignments(chunk_size=chunk_size),
            summary=summary,
            records_field="usuariocas",
            chunks_field="usuariocas_chunks",
            log_label="asignaciones usuario CAS",
        )
        self._process_dataset(
            dataset_name="ordenes_garantia",
            chunk_iterator=self._repository.extract_personal_warranty_orders(chunk_size=chunk_size),
            summary=summary,
            records_field="ordenes_garantia",
            chunks_field="ordenes_garantia_chunks",
            log_label="ordenes personales con garantia",
        )
        self._process_dataset(
            dataset_name="ordenesempresas_garantia",
            chunk_iterator=self._repository.extract_company_warranty_orders(chunk_size=chunk_size),
            summary=summary,
            records_field="ordenesempresas_garantia",
            chunks_field="ordenesempresas_garantia_chunks",
            log_label="ordenes empresariales con CAS",
        )

        summary.finished_at = datetime.now(UTC)
        self._sink.finalize(summary=summary)

        if self._sink.manifest_path is not None:
            summary.manifest_path = str(self._sink.manifest_path)

        logger.info(
            "Extraccion de garantias finalizada. CAS: %s | Usuario CAS: %s | Ordenes personales garantia: %s | Ordenes empresa CAS: %s.",
            summary.cas,
            summary.usuariocas,
            summary.ordenes_garantia,
            summary.ordenesempresas_garantia,
        )
        return summary

    def _process_dataset(
        self,
        dataset_name: str,
        chunk_iterator: Any,
        summary: WarrantyExtractionSummary,
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
