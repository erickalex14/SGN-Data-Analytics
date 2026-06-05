"""Caso de uso para cargar el dominio de inventario hacia staging PostgreSQL."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.inventory.application.dto import InventoryStagingLoadSummary
from novitec_dwh.contexts.inventory.application.staging_contracts import (
    InventoryRawReader,
    InventoryStagingRepository,
)

logger = logging.getLogger(__name__)


class LoadInventoryToStagingUseCase:
    """Orquesta la carga de datasets de inventario desde raw hacia staging."""

    def __init__(
        self,
        raw_reader: InventoryRawReader,
        staging_repository: InventoryStagingRepository,
        schema_name: str,
    ) -> None:
        """Recibe los adaptadores necesarios para leer y cargar la corrida."""

        self._raw_reader = raw_reader
        self._staging_repository = staging_repository
        self._schema_name = schema_name

    def execute(self) -> InventoryStagingLoadSummary:
        """Ejecuta la carga completa del dominio de inventario en staging."""

        started_at = datetime.now(UTC)
        self._raw_reader.prepare()
        extraction_id = self._raw_reader.extraction_id

        summary = InventoryStagingLoadSummary(
            extraction_id=extraction_id,
            raw_directory=self._raw_reader.run_directory.as_posix(),
            schema_name=self._schema_name,
            started_at=started_at,
        )

        logger.info(
            "Inicio de carga de inventario a staging. Corrida raw: %s. Carpeta: %s.",
            summary.extraction_id,
            summary.raw_directory,
        )

        self._staging_repository.prepare_schema()
        self._staging_repository.prepare_extraction(extraction_id=extraction_id)

        for chunk_number, chunk in enumerate(self._raw_reader.read_spare_parts(), start=1):
            self._staging_repository.load_spare_parts(extraction_id=extraction_id, records=chunk)
            summary.repuestos += len(chunk)
            summary.repuestos_chunks += 1
            logger.info(
                "Lote %s de repuestos cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_inventory_products(), start=1):
            self._staging_repository.load_inventory_products(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.productosinventario += len(chunk)
            summary.productosinventario_chunks += 1
            logger.info(
                "Lote %s de productos de inventario cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_order_spare_parts(), start=1):
            self._staging_repository.load_order_spare_parts(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.orden_repuestos += len(chunk)
            summary.orden_repuestos_chunks += 1
            logger.info(
                "Lote %s de repuestos por orden cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_spare_part_requests(), start=1):
            self._staging_repository.load_spare_part_requests(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.solicitudesrepuesto += len(chunk)
            summary.solicitudesrepuesto_chunks += 1
            logger.info(
                "Lote %s de solicitudes de repuesto cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        for chunk_number, chunk in enumerate(self._raw_reader.read_purchase_lists(), start=1):
            self._staging_repository.load_purchase_lists(
                extraction_id=extraction_id,
                records=chunk,
            )
            summary.listascompra += len(chunk)
            summary.listascompra_chunks += 1
            logger.info(
                "Lote %s de listas de compra cargado en staging. Registros: %s.",
                chunk_number,
                len(chunk),
            )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Carga de inventario a staging finalizada. Repuestos: %s | Productos inventario: %s | Orden repuestos: %s | Solicitudes repuesto: %s | Listas compra: %s.",
            summary.repuestos,
            summary.productosinventario,
            summary.orden_repuestos,
            summary.solicitudesrepuesto,
            summary.listascompra,
        )
        return summary
