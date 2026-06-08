"""Contratos de lectura del dominio CRM."""

from datetime import date
from typing import Protocol

from novitec_dwh.contexts.crm.application.dto_query import (
    CrmCompanyListItem,
    CrmCustomerBranchListItem,
    CrmCustomerListItem,
    CrmSummary,
    PaginatedCrmResult,
)


class CrmQueryRepository(Protocol):
    """Define las consultas de solo lectura sobre el mart CRM."""

    def get_summary(
        self,
        search: str | None = None,
        province: str | None = None,
        is_active: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> CrmSummary:
        """Obtiene los indicadores principales del dominio CRM."""

    def list_customers(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        identification: str | None = None,
        has_email: bool | None = None,
        has_address: bool | None = None,
        sort_by: str = "full_name",
        sort_dir: str = "asc",
    ) -> PaginatedCrmResult[CrmCustomerListItem]:
        """Lista clientes con filtros opcionales."""

    def list_companies(
        self,
        limit: int,
        offset: int,
        search: str | None = None,
        ruc: str | None = None,
        has_email: bool | None = None,
        has_phone: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "company_name",
        sort_dir: str = "asc",
    ) -> PaginatedCrmResult[CrmCompanyListItem]:
        """Lista empresas con filtros opcionales."""

    def list_customer_branches(
        self,
        limit: int,
        offset: int,
        branch_code: str | None = None,
        branch_name: str | None = None,
        province: str | None = None,
        novitec_branch_name: str | None = None,
        is_active: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "branch_name",
        sort_dir: str = "asc",
    ) -> PaginatedCrmResult[CrmCustomerBranchListItem]:
        """Lista sucursales cliente con filtros opcionales."""
