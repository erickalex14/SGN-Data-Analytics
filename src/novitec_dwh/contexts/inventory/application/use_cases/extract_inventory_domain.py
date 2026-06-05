"""Caso de uso para extraer el dominio de inventario completo."""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from novitec_dwh.contexts.inventory.application.contracts import InventoryExtractionSink
from novitec_dwh.contexts.inventory.application.dto import InventoryExtractionSummary
from novitec_dwh.contexts.inventory.domain.repositories import InventoryExtractionRepository

logger = logging.getLogger(__name__)


class ExtractInventoryDomainUseCase:
    """Orquesta la extraccion de las tablas priorizadas del dominio de inventario."""

    def __init__(
        self,
        repository: InventoryExtractionRepository,
        sink: InventoryExtractionSink,
    ) -> None:
        """Recibe el repositorio concreto que conoce el origen de datos."""

        self._repository = repository
        self._sink = sink

    def execute(self, chunk_size: int) -> InventoryExtractionSummary:
        """Ejecuta la extraccion completa y devuelve un resumen de volumen."""

        started_at = datetime.now(UTC)
        extraction_id = started_at.strftime("inventory_%Y%m%d_%H%M%S")
        summary = InventoryExtractionSummary(
            extraction_id=extraction_id,
            started_at=started_at,
        )

        self._sink.start(extraction_id=extraction_id, started_at=started_at)

        if self._sink.run_directory is not None:
            summary.output_directory = str(self._sink.run_directory)

        logger.info("Inicio de extraccion del dominio de inventario. Corrida: %s.", extraction_id)

        self._process_dataset(
            dataset_name="repuestos",
            chunk_iterator=self._repository.extract_spare_parts(chunk_size=chunk_size),
            summary=summary,
            records_field="repuestos",
            chunks_field="repuestos_chunks",
            log_label="catalogo de repuestos",
        )
        self._process_dataset(
            dataset_name="productosinventario",
            chunk_iterator=self._repository.extract_inventory_products(chunk_size=chunk_size),
            summary=summary,
            records_field="productosinventario",
            chunks_field="productosinventario_chunks",
            log_label="catalogo general de inventario",
        )
        self._process_dataset(
            dataset_name="orden_repuestos",
            chunk_iterator=self._repository.extract_order_spare_parts(chunk_size=chunk_size),
            summary=summary,
            records_field="orden_repuestos",
            chunks_field="orden_repuestos_chunks",
            log_label="repuestos instalados por orden",
        )
        self._process_dataset(
            dataset_name="solicitudesrepuesto",
            chunk_iterator=self._repository.extract_spare_part_requests(chunk_size=chunk_size),
            summary=summary,
            records_field="solicitudesrepuesto",
            chunks_field="solicitudesrepuesto_chunks",
            log_label="solicitudes de repuesto",
        )
        self._process_dataset(
            dataset_name="listascompra",
            chunk_iterator=self._repository.extract_purchase_lists(chunk_size=chunk_size),
            summary=summary,
            records_field="listascompra",
            chunks_field="listascompra_chunks",
            log_label="listas de compra",
        )

        summary.finished_at = datetime.now(UTC)
        self._sink.finalize(summary=summary)

        if self._sink.manifest_path is not None:
            summary.manifest_path = str(self._sink.manifest_path)

        logger.info(
            "Extraccion de inventario finalizada. Repuestos: %s | Productos inventario: %s | Orden repuestos: %s | Solicitudes repuesto: %s | Listas compra: %s.",
            summary.repuestos,
            summary.productosinventario,
            summary.orden_repuestos,
            summary.solicitudesrepuesto,
            summary.listascompra,
        )
        return summary

    def _process_dataset(
        self,
        dataset_name: str,
        chunk_iterator: Any,
        summary: InventoryExtractionSummary,
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
