"""Contratos de lectura del dominio tecnico."""

from datetime import date
from typing import Protocol

from novitec_dwh.contexts.technical.application.dto_query import (
    PaginatedTechnicalResult,
    TechnicalEquipmentAccessListItem,
    TechnicalEquipmentListItem,
    TechnicalReportListItem,
    TechnicalReportPhotoListItem,
    TechnicalSummary,
)


class TechnicalQueryRepository(Protocol):
    """Define las consultas de solo lectura sobre el mart tecnico."""

    def get_summary(
        self,
        technician_name: str | None = None,
        equipment_status: str | None = None,
        service_name: str | None = None,
        brand_name: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> TechnicalSummary:
        """Obtiene los indicadores principales del dominio tecnico."""

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
        """Lista informes tecnicos con filtros opcionales."""

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
        """Lista fotos de informes con filtros opcionales."""

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
        """Lista equipos tecnicos con filtros opcionales."""

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
        """Lista accesos de equipo con filtros opcionales."""
