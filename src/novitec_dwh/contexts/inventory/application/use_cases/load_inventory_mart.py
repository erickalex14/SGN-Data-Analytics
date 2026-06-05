"""Caso de uso para construir el mart de inventario desde staging."""

import logging
from datetime import UTC, datetime

from novitec_dwh.contexts.inventory.application.dto_mart import InventoryMartLoadSummary
from novitec_dwh.contexts.inventory.application.mart_contracts import InventoryMartRepository

logger = logging.getLogger(__name__)


class LoadInventoryMartUseCase:
    """Orquesta la construccion del mart de inventario desde staging."""

    def __init__(
        self,
        mart_repository: InventoryMartRepository,
        staging_schema: str,
        mart_schema: str,
        extraction_id: str,
    ) -> None:
        """Recibe el repositorio analitico y el contexto de la corrida."""

        self._mart_repository = mart_repository
        self._staging_schema = staging_schema
        self._mart_schema = mart_schema
        self._extraction_id = extraction_id

    def execute(self) -> InventoryMartLoadSummary:
        """Construye dimensiones y hechos del mart de inventario."""

        summary = InventoryMartLoadSummary(
            extraction_id=self._extraction_id,
            staging_schema=self._staging_schema,
            mart_schema=self._mart_schema,
            started_at=datetime.now(UTC),
        )

        logger.info(
            "Inicio de construccion del mart de inventario. Corrida: %s. Staging: %s. Mart: %s.",
            summary.extraction_id,
            summary.staging_schema,
            summary.mart_schema,
        )

        self._mart_repository.prepare_schema()
        self._mart_repository.prepare_extraction(extraction_id=self._extraction_id)
        self._mart_repository.load_date_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_technician_dimension(extraction_id=self._extraction_id)
        self._mart_repository.load_spare_part_dimension(extraction_id=self._extraction_id)

        summary.repuestos = self._mart_repository.load_spare_part_fact(extraction_id=self._extraction_id)
        logger.info("Hecho de repuestos cargado. Registros: %s.", summary.repuestos)

        summary.consumos_orden = self._mart_repository.load_order_consumption_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de consumo por orden cargado. Registros: %s.",
            summary.consumos_orden,
        )

        summary.solicitudes_repuesto = self._mart_repository.load_spare_part_request_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de solicitudes de repuesto cargado. Registros: %s.",
            summary.solicitudes_repuesto,
        )

        summary.listas_compra = self._mart_repository.load_purchase_list_fact(
            extraction_id=self._extraction_id,
        )
        logger.info(
            "Hecho de listas de compra cargado. Registros: %s.",
            summary.listas_compra,
        )

        (
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        ) = self._mart_repository.refresh_quality_audit(extraction_id=self._extraction_id)
        logger.info(
            "Auditoria de calidad de inventario actualizada. Reglas ejecutadas: %s | Hallazgos detectados: %s.",
            summary.reglas_calidad_ejecutadas,
            summary.hallazgos_calidad,
        )

        summary.finished_at = datetime.now(UTC)
        logger.info(
            "Mart de inventario finalizado. Repuestos: %s | Consumos orden: %s | Solicitudes: %s | Listas compra: %s | Hallazgos calidad: %s.",
            summary.repuestos,
            summary.consumos_orden,
            summary.solicitudes_repuesto,
            summary.listas_compra,
            summary.hallazgos_calidad,
        )
        return summary
