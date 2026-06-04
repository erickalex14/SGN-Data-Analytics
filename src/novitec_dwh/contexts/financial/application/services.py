"""Servicios de aplicacion del dominio financiero."""

import logging
from datetime import date

from novitec_dwh.contexts.financial.application.dto import (
    CreditNoteRequestListItem,
    FinancialSummary,
    NotificationListItem,
    OrderPriceListItem,
    PaginatedResult,
)
from novitec_dwh.contexts.financial.application.query_contracts import (
    FinancialQueryRepository,
)

logger = logging.getLogger("novitec_dwh.financial.service")


class FinancialQueryService:
    """Orquesta las lecturas del dominio financiero para la API."""

    def __init__(self, repository: FinancialQueryRepository) -> None:
        """Recibe el repositorio de consultas del mart financiero."""

        self._repository = repository

    def get_summary(
        self,
        order_id: int | None = None,
        order_number: str | None = None,
        technician_name: str | None = None,
        admin_name: str | None = None,
        status_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> FinancialSummary:
        """Devuelve el resumen financiero principal."""

        logger.info(
            "Consultando resumen financiero | filtros=%s",
            self._build_filter_log(
                order_id=order_id,
                order_number=order_number,
                technician_name=technician_name,
                admin_name=admin_name,
                status_name=status_name,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        result = self._repository.get_summary(
            order_id=order_id,
            order_number=order_number,
            technician_name=technician_name,
            admin_name=admin_name,
            status_name=status_name,
            date_from=date_from,
            date_to=date_to,
        )
        logger.info(
            "Resumen financiero generado | solicitudes_nc=%s | ingresos=%s | notificaciones=%s",
            result.total_solicitudes_nc,
            result.total_registros_ingreso,
            result.total_notificaciones,
        )
        return result

    def list_credit_note_requests(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        request_number: str | None = None,
        order_id: int | None = None,
        order_number: str | None = None,
        status_name: str | None = None,
        technician_name: str | None = None,
        admin_name: str | None = None,
        subject_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "request_date",
        sort_dir: str = "desc",
    ) -> PaginatedResult[CreditNoteRequestListItem]:
        """Devuelve solicitudes NC paginadas y filtrables."""

        logger.info(
            "Consultando solicitudes NC | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                search=search,
                request_number=request_number,
                order_id=order_id,
                order_number=order_number,
                status_name=status_name,
                technician_name=technician_name,
                admin_name=admin_name,
                subject_name=subject_name,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_credit_note_requests(
            limit=limit,
            offset=offset,
            search=search,
            request_number=request_number,
            order_id=order_id,
            order_number=order_number,
            status_name=status_name,
            technician_name=technician_name,
            admin_name=admin_name,
            subject_name=subject_name,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Solicitudes NC consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_order_prices(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        service_name: str | None = None,
        order_number: str | None = None,
        standard_service_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedResult[OrderPriceListItem]:
        """Devuelve ingresos por orden paginados y filtrables."""

        logger.info(
            "Consultando ingresos por orden | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                order_id=order_id,
                service_name=service_name,
                order_number=order_number,
                standard_service_name=standard_service_name,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_order_prices(
            limit=limit,
            offset=offset,
            order_id=order_id,
            service_name=service_name,
            order_number=order_number,
            standard_service_name=standard_service_name,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Ingresos por orden consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_notifications(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        order_number: str | None = None,
        nc_id: int | None = None,
        notification_type: str | None = None,
        is_read: bool | None = None,
        technician_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> PaginatedResult[NotificationListItem]:
        """Devuelve notificaciones paginadas y filtrables."""

        logger.info(
            "Consultando notificaciones financieras | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                order_id=order_id,
                order_number=order_number,
                nc_id=nc_id,
                notification_type=notification_type,
                is_read=is_read,
                technician_name=technician_name,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_notifications(
            limit=limit,
            offset=offset,
            order_id=order_id,
            order_number=order_number,
            nc_id=nc_id,
            notification_type=notification_type,
            is_read=is_read,
            technician_name=technician_name,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Notificaciones financieras consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
