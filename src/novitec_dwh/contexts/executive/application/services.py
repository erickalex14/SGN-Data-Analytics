"""Servicios del contexto ejecutivo."""

import logging
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from novitec_dwh.contexts.executive.application.dto import (
    ExecutiveDashboard,
    ExecutiveDashboardFilters,
    ExecutiveDashboardKpis,
)
from novitec_dwh.contexts.financial.application.services import FinancialQueryService
from novitec_dwh.contexts.operational.application.services import OperationalQueryService

logger = logging.getLogger("novitec_dwh.executive.service")


class ExecutiveDashboardService:
    """Orquesta la construccion de un resumen ejecutivo consolidado."""

    def __init__(
        self,
        financial_service: FinancialQueryService,
        operational_service: OperationalQueryService,
    ) -> None:
        """Recibe los servicios especializados que alimentan el dashboard."""

        self._financial_service = financial_service
        self._operational_service = operational_service

    def get_dashboard(
        self,
        date_from: date | None = None,
        date_to: date | None = None,
        technician_name: str | None = None,
        branch_name: str | None = None,
        admin_name: str | None = None,
        status_name: str | None = None,
        order_type: str | None = None,
    ) -> ExecutiveDashboard:
        """Construye el resumen ejecutivo consolidado para la gerencia."""

        logger.info(
            "Consultando dashboard ejecutivo | filtros=%s",
            self._build_filter_log(
                date_from=date_from,
                date_to=date_to,
                technician_name=technician_name,
                branch_name=branch_name,
                admin_name=admin_name,
                status_name=status_name,
                order_type=order_type,
            ),
        )

        # Se reutilizan los contratos ya validados de cada dominio para evitar
        # duplicar reglas de lectura o armar consultas fuera de su contexto.
        financial_summary = self._financial_service.get_summary(
            technician_name=technician_name,
            admin_name=admin_name,
            status_name=status_name,
            date_from=date_from,
            date_to=date_to,
        )
        operational_summary = self._operational_service.get_summary(
            order_type=order_type,
            technician_name=technician_name,
            branch_name=branch_name,
            status_name=status_name,
            date_from=date_from,
            date_to=date_to,
        )

        dashboard = ExecutiveDashboard(
            generated_at=datetime.now(),
            filters=ExecutiveDashboardFilters(
                date_from=date_from,
                date_to=date_to,
                technician_name=technician_name,
                branch_name=branch_name,
                admin_name=admin_name,
                status_name=status_name,
                order_type=order_type,
            ),
            operational=operational_summary,
            financial=financial_summary,
            kpis=ExecutiveDashboardKpis(
                tasa_aprobacion_nc=self._calculate_ratio(
                    numerator=financial_summary.solicitudes_aprobadas,
                    denominator=financial_summary.total_solicitudes_nc,
                ),
                tasa_notificaciones_leidas=self._calculate_ratio(
                    numerator=financial_summary.total_notificaciones_leidas,
                    denominator=financial_summary.total_notificaciones,
                ),
                tasa_ordenes_entregadas=self._calculate_ratio(
                    numerator=operational_summary.ordenes_entregadas,
                    denominator=operational_summary.total_ordenes,
                ),
                tasa_ordenes_abiertas=self._calculate_ratio(
                    numerator=operational_summary.ordenes_abiertas,
                    denominator=operational_summary.total_ordenes,
                ),
                tasa_ordenes_garantia=self._calculate_ratio(
                    numerator=operational_summary.ordenes_con_garantia,
                    denominator=operational_summary.total_ordenes,
                ),
            ),
        )
        logger.info(
            "Dashboard ejecutivo generado | ordenes=%s | solicitudes_nc=%s | ingresos=%s",
            dashboard.operational.total_ordenes,
            dashboard.financial.total_solicitudes_nc,
            dashboard.financial.monto_total_ingresos,
        )
        return dashboard

    def _calculate_ratio(self, numerator: int, denominator: int) -> Decimal | None:
        """Calcula un indicador porcentual con dos decimales."""

        if denominator <= 0:
            return None
        ratio = (Decimal(numerator) / Decimal(denominator)) * Decimal("100")
        return ratio.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _build_filter_log(self, **filters) -> dict[str, object]:
        """Depura filtros vacios para registrar solo datos relevantes."""

        return {key: value for key, value in filters.items() if value is not None and value != ""}
