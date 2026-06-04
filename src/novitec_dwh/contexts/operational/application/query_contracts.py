"""Contratos de lectura del dominio operativo."""

from datetime import date
from typing import Protocol

from novitec_dwh.contexts.operational.application.dto_query import (
    OperationalAssignmentListItem,
    OperationalOrderListItem,
    OperationalPreorderListItem,
    OperationalSummary,
    PaginatedOperationalResult,
)


class OperationalQueryRepository(Protocol):
    """Define las consultas de solo lectura sobre el mart operativo."""

    def get_summary(
        self,
        order_type: str | None = None,
        technician_name: str | None = None,
        branch_name: str | None = None,
        status_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> OperationalSummary:
        """Obtiene los indicadores principales del dominio operativo."""

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
        """Lista ordenes operativas con filtros opcionales."""

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
        """Lista preordenes operativas con filtros opcionales."""

    def list_company_order_assignments(
        self,
        limit: int,
        offset: int,
        source_order_id: int | None = None,
        technician_name: str | None = None,
        sort_by: str = "source_order_id",
        sort_dir: str = "desc",
    ) -> PaginatedOperationalResult[OperationalAssignmentListItem]:
        """Lista asignaciones tecnico-orden empresarial con filtros opcionales."""
