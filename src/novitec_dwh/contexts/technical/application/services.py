"""Servicios de aplicacion del dominio tecnico."""

import logging
from datetime import date

from novitec_dwh.contexts.technical.application.dto_query import (
    PaginatedTechnicalResult,
    TechnicalEquipmentAccessListItem,
    TechnicalEquipmentListItem,
    TechnicalReportListItem,
    TechnicalReportPhotoListItem,
    TechnicalSummary,
)
from novitec_dwh.contexts.technical.application.query_contracts import TechnicalQueryRepository

logger = logging.getLogger("novitec_dwh.technical.service")


class TechnicalQueryService:
    """Orquesta las lecturas del dominio tecnico para la API."""

    def __init__(self, repository: TechnicalQueryRepository) -> None:
        """Recibe el repositorio de consultas del mart tecnico."""

        self._repository = repository

    def get_summary(
        self,
        technician_name: str | None = None,
        equipment_status: str | None = None,
        service_name: str | None = None,
        brand_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> TechnicalSummary:
        """Devuelve el resumen tecnico principal."""

        logger.info(
            "Consultando resumen tecnico | filtros=%s",
            self._build_filter_log(
                technician_name=technician_name,
                equipment_status=equipment_status,
                service_name=service_name,
                brand_name=brand_name,
                date_from=date_from,
                date_to=date_to,
            ),
        )
        result = self._repository.get_summary(
            technician_name=technician_name,
            equipment_status=equipment_status,
            service_name=service_name,
            brand_name=brand_name,
            date_from=date_from,
            date_to=date_to,
        )
        logger.info(
            "Resumen tecnico generado | informes=%s | fotos=%s | equipos=%s | accesos=%s",
            result.total_informes,
            result.total_fotos_informes,
            result.total_equipos,
            result.total_accesos_equipos,
        )
        return result

    def list_reports(
        self,
        limit: int,
        offset: int,
        order_id: int | None = None,
        technician_name: str | None = None,
        equipment_status: str | None = None,
        has_budget_json: bool | None = None,
        is_equipment_operational: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "report_date",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalReportListItem]:
        """Devuelve informes tecnicos paginados y filtrables."""

        logger.info(
            "Consultando informes tecnicos | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                order_id=order_id,
                technician_name=technician_name,
                equipment_status=equipment_status,
                has_budget_json=has_budget_json,
                is_equipment_operational=is_equipment_operational,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_reports(
            limit=limit,
            offset=offset,
            order_id=order_id,
            technician_name=technician_name,
            equipment_status=equipment_status,
            has_budget_json=has_budget_json,
            is_equipment_operational=is_equipment_operational,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Informes tecnicos consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_report_photos(
        self,
        limit: int,
        offset: int,
        report_source_id: int | None = None,
        technician_name: str | None = None,
        has_binary_evidence: bool | None = None,
        mime_type: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "report_date",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalReportPhotoListItem]:
        """Devuelve fotos de informes paginadas y filtrables."""

        logger.info(
            "Consultando fotos de informes | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                report_source_id=report_source_id,
                technician_name=technician_name,
                has_binary_evidence=has_binary_evidence,
                mime_type=mime_type,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_report_photos(
            limit=limit,
            offset=offset,
            report_source_id=report_source_id,
            technician_name=technician_name,
            has_binary_evidence=has_binary_evidence,
            mime_type=mime_type,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Fotos de informes consultadas | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_equipment(
        self,
        limit: int,
        offset: int,
        service_name: str | None = None,
        brand_name: str | None = None,
        device_type_name: str | None = None,
        inventory_product_code: str | None = None,
        has_password_provided: bool | None = None,
        has_failure_description: bool | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        sort_by: str = "billing_date",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalEquipmentListItem]:
        """Devuelve equipos tecnicos paginados y filtrables."""

        logger.info(
            "Consultando equipos tecnicos | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                service_name=service_name,
                brand_name=brand_name,
                device_type_name=device_type_name,
                inventory_product_code=inventory_product_code,
                has_password_provided=has_password_provided,
                has_failure_description=has_failure_description,
                date_from=date_from,
                date_to=date_to,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_equipment(
            limit=limit,
            offset=offset,
            service_name=service_name,
            brand_name=brand_name,
            device_type_name=device_type_name,
            inventory_product_code=inventory_product_code,
            has_password_provided=has_password_provided,
            has_failure_description=has_failure_description,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Equipos tecnicos consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def list_equipment_access(
        self,
        limit: int,
        offset: int,
        equipment_source_id: int | None = None,
        has_user_name: bool | None = None,
        is_pattern: bool | None = None,
        sort_by: str = "equipment_source_id",
        sort_dir: str = "desc",
    ) -> PaginatedTechnicalResult[TechnicalEquipmentAccessListItem]:
        """Devuelve accesos de equipos paginados y filtrables."""

        logger.info(
            "Consultando accesos de equipos | filtros=%s",
            self._build_filter_log(
                limit=limit,
                offset=offset,
                equipment_source_id=equipment_source_id,
                has_user_name=has_user_name,
                is_pattern=is_pattern,
                sort_by=sort_by,
                sort_dir=sort_dir,
            ),
        )
        result = self._repository.list_equipment_access(
            limit=limit,
            offset=offset,
            equipment_source_id=equipment_source_id,
            has_user_name=has_user_name,
            is_pattern=is_pattern,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        logger.info(
            "Accesos de equipos consultados | total=%s | devueltos=%s | limit=%s | offset=%s",
            result.total,
            len(result.items),
            result.limit,
            result.offset,
        )
        return result

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
