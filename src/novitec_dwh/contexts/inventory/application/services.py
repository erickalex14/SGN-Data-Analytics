"""Servicios de aplicacion del dominio de inventario."""

import logging
from datetime import date

from novitec_dwh.contexts.inventory.application.dto_query import (
    InventoryOrderSparePartListItem,
    InventoryPurchaseListListItem,
    InventorySparePartListItem,
    InventorySparePartRequestListItem,
    InventorySummary,
    PaginatedInventoryResult,
)
from novitec_dwh.contexts.inventory.application.query_contracts import InventoryQueryRepository

logger = logging.getLogger("novitec_dwh.inventory.service")


class InventoryQueryService:
    """Orquesta las lecturas del dominio de inventario para la API."""

    def __init__(self, repository: InventoryQueryRepository) -> None:
        """Recibe el repositorio de consultas del mart de inventario."""

        self._repository = repository

    def get_summary(
        self,
        technician_name: str | None = None,
        spare_part_code: str | None = None,
        request_status: str | None = None,
        warehouse_number: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> InventorySummary:
        """Devuelve el resumen principal del dominio de inventario."""

        logger.info(
            "Consultando resumen de inventario | filtros=%s",
            self._build_filter_log(
                technician_name=technician_name,
                spare_part_code=spare_part_code,
                request_status=request_status,
                warehouse_number=warehouse_number,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        result = self._repository.get_summary(
            technician_name=technician_name,
            spare_part_code=spare_part_code,
            request_status=request_status,
            warehouse_number=warehouse_number,
            date_from=date_from,
            date_to=date_to,
        )
        logger.info(
            "Resumen de inventario generado | repuestos=%s | consumos=%s | solicitudes=%s | listas=%s",
            result.total_repuestos,
            result.total_consumos_orden,
            result.total_solicitudes_repuesto,
            result.total_listas_compra,
        )
        return result

    def list_spare_parts(
        self,
        limit: int,
        offset: int,
        spare_part_code: str | None = None,
        part_number: str | None = None,
        spare_part_name: str | None = None,
        warehouse_number: int | None = None,
        has_stock: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "updated_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventorySparePartListItem]:
        """Devuelve repuestos paginados y filtrables."""

        logger.info(
            "Consultando repuestos | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                spare_part_code=spare_part_code,
                part_number=part_number,
                spare_part_name=spare_part_name,
                warehouse_number=warehouse_number,
                has_stock=has_stock,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_spare_parts(
            limit=limit,
            offset=offset,
            spare_part_code=spare_part_code,
            part_number=part_number,
            spare_part_name=spare_part_name,
            warehouse_number=warehouse_number,
            has_stock=has_stock,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Repuestos consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_order_spare_parts(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        spare_part_code: str | None = None,
        spare_part_name: str | None = None,
        installer_user_id: int | None = None,
        has_installer_user: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "movement_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventoryOrderSparePartListItem]:
        """Devuelve consumos por orden paginados y filtrables."""

        logger.info(
            "Consultando consumos de repuestos por orden | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                order_id=order_id,
                spare_part_code=spare_part_code,
                spare_part_name=spare_part_name,
                installer_user_id=installer_user_id,
                has_installer_user=has_installer_user,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_order_spare_parts(
            limit=limit,
            offset=offset,
            order_id=order_id,
            spare_part_code=spare_part_code,
            spare_part_name=spare_part_name,
            installer_user_id=installer_user_id,
            has_installer_user=has_installer_user,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Consumos por orden consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_spare_part_requests(
        self,
        limit: int,
        offset: int,
        request_number: str | None = None,
        order_id: int | None = None,
        technician_name: str | None = None,
        spare_part_code: str | None = None,
        request_status: str | None = None,
        approved_by: str | None = None,
        has_purchase_link: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "request_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventorySparePartRequestListItem]:
        """Devuelve solicitudes de repuesto paginadas y filtrables."""

        logger.info(
            "Consultando solicitudes de repuesto | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                request_number=request_number,
                order_id=order_id,
                technician_name=technician_name,
                spare_part_code=spare_part_code,
                request_status=request_status,
                approved_by=approved_by,
                has_purchase_link=has_purchase_link,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_spare_part_requests(
            limit=limit,
            offset=offset,
            request_number=request_number,
            order_id=order_id,
            technician_name=technician_name,
            spare_part_code=spare_part_code,
            request_status=request_status,
            approved_by=approved_by,
            has_purchase_link=has_purchase_link,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Solicitudes de repuesto consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_purchase_lists(
        self,
        limit: int,
        offset: int,
        list_number: str | None = None,
        creator_user_id: int | None = None,
        list_status: str | None = None,
        has_observation: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "creation_date",
        sort_dir: str = "desc",
    ) -> PaginatedInventoryResult[InventoryPurchaseListListItem]:
        """Devuelve listas de compra paginadas y filtrables."""

        logger.info(
            "Consultando listas de compra | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                list_number=list_number,
                creator_user_id=creator_user_id,
                list_status=list_status,
                has_observation=has_observation,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_purchase_lists(
            limit=limit,
            offset=offset,
            list_number=list_number,
            creator_user_id=creator_user_id,
            list_status=list_status,
            has_observation=has_observation,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Listas de compra consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
