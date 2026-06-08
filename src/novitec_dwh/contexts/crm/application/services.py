"""Servicios de aplicacion del dominio CRM."""

import logging
from datetime import date

from novitec_dwh.contexts.crm.application.dto_query import (
    CrmCompanyListItem,
    CrmCustomerBranchListItem,
    CrmCustomerListItem,
    CrmSummary,
    PaginatedCrmResult,
)
from novitec_dwh.contexts.crm.application.query_contracts import CrmQueryRepository

logger = logging.getLogger("novitec_dwh.crm.service")


class CrmQueryService:
    """Orquesta las lecturas del dominio CRM para la API."""

    def __init__(self, repository: CrmQueryRepository) -> None:
        """Recibe el repositorio de consultas del mart CRM."""

        self._repository = repository

    def get_summary(
        self,
        search: str | None = None,
        province: str | None = None,
        is_active: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> CrmSummary:
        """Devuelve el resumen principal del dominio CRM."""

        logger.info(
            "Consultando resumen CRM | filtros=%s",
            self._build_filter_log(
                search=search,
                province=province,
                is_active=is_active,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        result = self._repository.get_summary(
            search=search,
            province=province,
            is_active=is_active,
            date_from=date_from,
            date_to=date_to,
        )
        logger.info(
            "Resumen CRM generado | clientes=%s | empresas=%s | sucursales=%s",
            result.total_clientes,
            result.total_empresas,
            result.total_sucursalescliente,
        )
        return result

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
        """Devuelve clientes paginados y filtrables."""

        logger.info(
            "Consultando clientes CRM | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                search=search,
                identification=identification,
                has_email=has_email,
                has_address=has_address,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_customers(
            limit=limit,
            offset=offset,
            search=search,
            identification=identification,
            has_email=has_email,
            has_address=has_address,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Clientes CRM consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve empresas paginadas y filtrables."""

        logger.info(
            "Consultando empresas CRM | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                search=search,
                ruc=ruc,
                has_email=has_email,
                has_phone=has_phone,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_companies(
            limit=limit,
            offset=offset,
            search=search,
            ruc=ruc,
            has_email=has_email,
            has_phone=has_phone,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Empresas CRM consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve sucursales cliente paginadas y filtrables."""

        logger.info(
            "Consultando sucursales cliente CRM | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                branch_code=branch_code,
                branch_name=branch_name,
                province=province,
                novitec_branch_name=novitec_branch_name,
                is_active=is_active,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_customer_branches(
            limit=limit,
            offset=offset,
            branch_code=branch_code,
            branch_name=branch_name,
            province=province,
            novitec_branch_name=novitec_branch_name,
            is_active=is_active,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Sucursales cliente CRM consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
