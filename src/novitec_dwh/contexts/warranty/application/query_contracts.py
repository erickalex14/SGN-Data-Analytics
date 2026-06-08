"""Contratos de lectura del dominio de garantias."""

from datetime import date
from typing import Protocol

from novitec_dwh.contexts.warranty.application.dto_query import (
    PaginatedWarrantyResult,
    WarrantyCompanyOrderListItem,
    WarrantyPersonalOrderListItem,
    WarrantyServiceCenterListItem,
    WarrantySummary,
    WarrantyUserAssignmentListItem,
)


class WarrantyQueryRepository(Protocol):
    """Define las consultas de solo lectura sobre el mart de garantias."""

    def get_summary(
        self,
        service_center_name: str | None = None,
        technician_id: int | None = None,
        user_id: int | None = None,
        warranty_status: str | None = None,
        warranty_type: str | None = None,
        order_status: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> WarrantySummary:
        """Obtiene los indicadores principales del dominio de garantias."""

    def list_service_centers(
        self,
        limit: int,
        offset: int,
        service_center_name: str | None = None,
        prefix_code: str | None = None,
        brand_name: str | None = None,
        city_name: str | None = None,
        is_active: bool | None = None,
        sort_by: str = "service_center_name",
        sort_dir: str = "asc",
    ) -> PaginatedWarrantyResult[WarrantyServiceCenterListItem]:
        """Lista CAS con filtros opcionales."""

    def list_personal_orders(
        self,
        limit: int,
        offset: int,
        order_number: str | None = None,
        service_center_name: str | None = None,
        technician_id: int | None = None,
        warranty_status: str | None = None,
        warranty_type: str | None = None,
        order_status: str | None = None,
        has_case_number: bool | None = None,
        is_closed: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "opened_date",
        sort_dir: str = "desc",
    ) -> PaginatedWarrantyResult[WarrantyPersonalOrderListItem]:
        """Lista ordenes personales con garantia."""

    def list_company_orders(
        self,
        limit: int,
        offset: int,
        order_number: str | None = None,
        service_center_name: str | None = None,
        technician_id: int | None = None,
        company_id: int | None = None,
        order_status: str | None = None,
        has_ticket_number: bool | None = None,
        has_worked_hours: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "opened_date",
        sort_dir: str = "desc",
    ) -> PaginatedWarrantyResult[WarrantyCompanyOrderListItem]:
        """Lista ordenes empresariales asociadas a CAS."""

    def list_user_assignments(
        self,
        limit: int,
        offset: int,
        user_id: int | None = None,
        user_login: str | None = None,
        user_name: str | None = None,
        service_center_name: str | None = None,
        sort_by: str = "user_name",
        sort_dir: str = "asc",
    ) -> PaginatedWarrantyResult[WarrantyUserAssignmentListItem]:
        """Lista asignaciones entre usuarios y CAS."""

