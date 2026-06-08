"""Servicios de aplicacion del dominio de garantias."""

import logging
from datetime import date

from novitec_dwh.contexts.warranty.application.dto_query import (
    PaginatedWarrantyResult,
    WarrantyCompanyOrderListItem,
    WarrantyPersonalOrderListItem,
    WarrantyServiceCenterListItem,
    WarrantySummary,
    WarrantyUserAssignmentListItem,
)
from novitec_dwh.contexts.warranty.application.query_contracts import WarrantyQueryRepository

logger = logging.getLogger("novitec_dwh.warranty.service")


class WarrantyQueryService:
    """Orquesta las lecturas del dominio de garantias para la API."""

    def __init__(self, repository: WarrantyQueryRepository) -> None:
        """Recibe el repositorio de consultas del mart de garantias."""

        self._repository = repository

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
        """Devuelve el resumen principal del dominio de garantias."""

        logger.info(
            "Consultando resumen de garantias | filtros=%s",
            self._build_filter_log(
                service_center_name=service_center_name,
                technician_id=technician_id,
                user_id=user_id,
                warranty_status=warranty_status,
                warranty_type=warranty_type,
                order_status=order_status,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        result = self._repository.get_summary(
            service_center_name=service_center_name,
            technician_id=technician_id,
            user_id=user_id,
            warranty_status=warranty_status,
            warranty_type=warranty_type,
            order_status=order_status,
            date_from=date_from,
            date_to=date_to,
        )
        logger.info(
            "Resumen de garantias generado | cas=%s | ordenes_personales=%s | ordenes_empresariales=%s | asignaciones=%s",
            result.total_cas,
            result.total_ordenes_personales,
            result.total_ordenes_empresariales,
            result.total_asignaciones_usuario_cas,
        )
        return result

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
        """Devuelve CAS paginados y filtrables."""

        logger.info(
            "Consultando CAS | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                service_center_name=service_center_name,
                prefix_code=prefix_code,
                brand_name=brand_name,
                city_name=city_name,
                is_active=is_active,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_service_centers(
            limit=limit,
            offset=offset,
            service_center_name=service_center_name,
            prefix_code=prefix_code,
            brand_name=brand_name,
            city_name=city_name,
            is_active=is_active,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "CAS consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve ordenes personales de garantia paginadas y filtrables."""

        logger.info(
            "Consultando ordenes personales de garantia | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                order_number=order_number,
                service_center_name=service_center_name,
                technician_id=technician_id,
                warranty_status=warranty_status,
                warranty_type=warranty_type,
                order_status=order_status,
                has_case_number=has_case_number,
                is_closed=is_closed,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_personal_orders(
            limit=limit,
            offset=offset,
            order_number=order_number,
            service_center_name=service_center_name,
            technician_id=technician_id,
            warranty_status=warranty_status,
            warranty_type=warranty_type,
            order_status=order_status,
            has_case_number=has_case_number,
            is_closed=is_closed,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Ordenes personales de garantia consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve ordenes empresariales asociadas a CAS."""

        logger.info(
            "Consultando ordenes empresariales con CAS | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                order_number=order_number,
                service_center_name=service_center_name,
                technician_id=technician_id,
                company_id=company_id,
                order_status=order_status,
                has_ticket_number=has_ticket_number,
                has_worked_hours=has_worked_hours,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_company_orders(
            limit=limit,
            offset=offset,
            order_number=order_number,
            service_center_name=service_center_name,
            technician_id=technician_id,
            company_id=company_id,
            order_status=order_status,
            has_ticket_number=has_ticket_number,
            has_worked_hours=has_worked_hours,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Ordenes empresariales con CAS consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

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
        """Devuelve asignaciones usuario CAS paginadas y filtrables."""

        logger.info(
            "Consultando asignaciones usuario CAS | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                user_id=user_id,
                user_login=user_login,
                user_name=user_name,
                service_center_name=service_center_name,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_user_assignments(
            limit=limit,
            offset=offset,
            user_id=user_id,
            user_login=user_login,
            user_name=user_name,
            service_center_name=service_center_name,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Asignaciones usuario CAS consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
