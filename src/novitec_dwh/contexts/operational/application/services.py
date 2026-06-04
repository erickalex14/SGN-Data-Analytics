"""Servicios de aplicacion del dominio operativo."""

import logging
from datetime import date

from novitec_dwh.contexts.operational.application.dto_query import (
    OperationalAssignmentListItem,
    OperationalOrderListItem,
    OperationalPreorderListItem,
    OperationalSummary,
    PaginatedOperationalResult,
)
from novitec_dwh.contexts.operational.application.query_contracts import (
    OperationalQueryRepository,
)

logger = logging.getLogger("novitec_dwh.operational.service")


class OperationalQueryService:
    """Orquesta las lecturas del dominio operativo para la API."""

    def __init__(self, repository: OperationalQueryRepository) -> None:
        """Recibe el repositorio de consultas del mart operativo."""

        self._repository = repository

    def get_summary(
        self,
        order_type: str | None = None,
        technician_name: str | None = None,
        branch_name: str | None = None,
        status_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> OperationalSummary:
        """Devuelve el resumen operativo principal."""

        logger.info(
            "Consultando resumen operativo | filtros=%s",
            self._build_filter_log(
                order_type=order_type,
                technician_name=technician_name,
                branch_name=branch_name,
                status_name=status_name,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        result = self._repository.get_summary(
            order_type=order_type,
            technician_name=technician_name,
            branch_name=branch_name,
            status_name=status_name,
            date_from=date_from,
            date_to=date_to,
        )
        logger.info(
            "Resumen operativo generado | ordenes=%s | preordenes=%s | asignaciones=%s",
            result.total_ordenes,
            result.total_preordenes,
            result.total_asignaciones_tecnicos,
        )
        return result

    def list_orders(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        order_type: str | None = None,
        status_name: str | None = None,
        technician_name: str | None = None,
        branch_name: str | None = None,
        customer_type: str | None = None,
        is_open: bool | None = None,
        is_warranty: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "intake_date",
        sort_dir: str = "desc",
    ) -> PaginatedOperationalResult[OperationalOrderListItem]:
        """Devuelve ordenes operativas paginadas y filtrables."""

        logger.info(
            "Consultando ordenes operativas | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                search=search,
                order_type=order_type,
                status_name=status_name,
                technician_name=technician_name,
                branch_name=branch_name,
                customer_type=customer_type,
                is_open=is_open,
                is_warranty=is_warranty,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_orders(
            limit=limit,
            offset=offset,
            search=search,
            order_type=order_type,
            status_name=status_name,
            technician_name=technician_name,
            branch_name=branch_name,
            customer_type=customer_type,
            is_open=is_open,
            is_warranty=is_warranty,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Ordenes operativas consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_preorders(
        self,
        limit: int,
        offset: int,
        preorder_status: str | None = None,
        branch_name: str | None = None,
        has_invoice: bool | None = None,
        has_photos: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "registration_date",
        sort_dir: str = "desc",
    ) -> PaginatedOperationalResult[OperationalPreorderListItem]:
        """Devuelve preordenes paginadas y filtrables."""

        logger.info(
            "Consultando preordenes operativas | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                preorder_status=preorder_status,
                branch_name=branch_name,
                has_invoice=has_invoice,
                has_photos=has_photos,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_preorders(
            limit=limit,
            offset=offset,
            preorder_status=preorder_status,
            branch_name=branch_name,
            has_invoice=has_invoice,
            has_photos=has_photos,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Preordenes operativas consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_company_order_assignments(
        self,
        limit: int,
        offset: int,
        source_order_id: int | None = None,
        technician_name: str | None = None,
        sort_by: str = "source_order_id",
        sort_dir: str = "desc",
    ) -> PaginatedOperationalResult[OperationalAssignmentListItem]:
        """Devuelve asignaciones tecnico-orden paginadas y filtrables."""

        logger.info(
            "Consultando asignaciones tecnico-orden | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                source_order_id=source_order_id,
                technician_name=technician_name,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_company_order_assignments(
            limit=limit,
            offset=offset,
            source_order_id=source_order_id,
            technician_name=technician_name,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Asignaciones tecnico-orden consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
