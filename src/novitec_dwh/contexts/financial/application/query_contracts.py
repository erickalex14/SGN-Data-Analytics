"""Contratos de lectura del dominio financiero."""

from datetime import date
from typing import Protocol

from novitec_dwh.contexts.financial.application.dto import (
    CreditNoteRequestListItem,
    FinancialSummary,
    NotificationListItem,
    OrderPriceListItem,
    PaginatedResult,
)


class FinancialQueryRepository(Protocol):
    """Define las consultas de solo lectura sobre el mart financiero."""

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
        """Obtiene los indicadores principales del dominio financiero."""

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
        """Lista solicitudes de nota de credito con filtros opcionales."""

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
        """Lista registros de ingresos por orden con filtros opcionales."""

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
        """Lista notificaciones del dominio financiero con filtros opcionales."""
