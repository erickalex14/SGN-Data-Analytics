"""Servicios del contexto ejecutivo."""

import logging
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from novitec_dwh.contexts.crm.application.services import CrmQueryService
from novitec_dwh.contexts.executive.application.dto import (
    ExecutiveDashboard,
    ExecutiveDashboardFilters,
    ExecutiveDashboardKpis,
)
from novitec_dwh.contexts.financial.application.services import FinancialQueryService
from novitec_dwh.contexts.inventory.application.services import InventoryQueryService
from novitec_dwh.contexts.operational.application.services import OperationalQueryService
from novitec_dwh.contexts.organizational.application.services import (
    OrganizationalQueryService,
)
from novitec_dwh.contexts.technical.application.services import TechnicalQueryService
from novitec_dwh.contexts.warranty.application.services import WarrantyQueryService

logger = logging.getLogger("novitec_dwh.executive.service")


class ExecutiveDashboardService:
    """Orquesta la construccion de un resumen ejecutivo consolidado."""

    def __init__(
        self,
        financial_service: FinancialQueryService,
        operational_service: OperationalQueryService,
        technical_service: TechnicalQueryService,
        inventory_service: InventoryQueryService,
        crm_service: CrmQueryService,
        warranty_service: WarrantyQueryService,
        organizational_service: OrganizationalQueryService,
    ) -> None:
        """Recibe los servicios especializados que alimentan el dashboard."""

        self._financial_service = financial_service
        self._operational_service = operational_service
        self._technical_service = technical_service
        self._inventory_service = inventory_service
        self._crm_service = crm_service
        self._warranty_service = warranty_service
        self._organizational_service = organizational_service

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
        technical_summary = self._technical_service.get_summary(
            technician_name=technician_name,
            equipment_status=status_name,
            date_from=date_from,
            date_to=date_to,
        )
        inventory_summary = self._inventory_service.get_summary(
            technician_name=technician_name,
            request_status=status_name,
            date_from=date_from,
            date_to=date_to,
        )
        crm_summary = self._crm_service.get_summary(
            date_from=date_from,
            date_to=date_to,
        )
        warranty_summary = self._warranty_service.get_summary(
            technician_id=None,
            user_id=None,
            service_center_name=None,
            warranty_status=status_name,
            warranty_type=None,
            order_status=status_name,
            date_from=date_from,
            date_to=date_to,
        )
        organizational_summary = self._organizational_service.get_summary(
            branch_city=branch_name,
            role_name=None,
            access_group_name=None,
            is_active=None,
            can_access_nc=None,
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
            technical=technical_summary,
            inventory=inventory_summary,
            crm=crm_summary,
            warranty=warranty_summary,
            organizational=organizational_summary,
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
                tasa_informes_equipo_operativo=self._calculate_ratio(
                    numerator=technical_summary.informes_equipo_operativo,
                    denominator=technical_summary.total_informes,
                ),
                tasa_informes_con_presupuesto=self._calculate_ratio(
                    numerator=technical_summary.informes_con_presupuesto,
                    denominator=technical_summary.total_informes,
                ),
                tasa_equipos_con_contrasena=self._calculate_ratio(
                    numerator=technical_summary.equipos_con_contrasena,
                    denominator=technical_summary.total_equipos,
                ),
                tasa_repuestos_con_stock=self._calculate_ratio(
                    numerator=inventory_summary.repuestos_con_stock,
                    denominator=inventory_summary.total_repuestos,
                ),
                tasa_solicitudes_repuesto_aprobadas=self._calculate_ratio(
                    numerator=inventory_summary.solicitudes_aprobadas,
                    denominator=inventory_summary.total_solicitudes_repuesto,
                ),
                tasa_solicitudes_repuesto_pendientes=self._calculate_ratio(
                    numerator=inventory_summary.solicitudes_pendientes,
                    denominator=inventory_summary.total_solicitudes_repuesto,
                ),
                tasa_clientes_con_correo=self._calculate_ratio(
                    numerator=crm_summary.clientes_con_correo,
                    denominator=crm_summary.total_clientes,
                ),
                tasa_empresas_con_correo=self._calculate_ratio(
                    numerator=crm_summary.empresas_con_correo,
                    denominator=crm_summary.total_empresas,
                ),
                tasa_sucursalescliente_activas=self._calculate_ratio(
                    numerator=crm_summary.sucursalescliente_activas,
                    denominator=crm_summary.total_sucursalescliente,
                ),
                tasa_cas_activos=self._calculate_ratio(
                    numerator=warranty_summary.cas_activos,
                    denominator=warranty_summary.total_cas,
                ),
                tasa_ordenes_personales_garantia_con_caso=self._calculate_ratio(
                    numerator=warranty_summary.ordenes_personales_con_caso,
                    denominator=warranty_summary.total_ordenes_personales,
                ),
                tasa_ordenes_empresariales_garantia_con_ticket=self._calculate_ratio(
                    numerator=warranty_summary.ordenes_empresariales_con_ticket,
                    denominator=warranty_summary.total_ordenes_empresariales,
                ),
                tasa_usuarios_activos=self._calculate_ratio(
                    numerator=organizational_summary.usuarios_activos,
                    denominator=organizational_summary.total_usuarios,
                ),
                tasa_usuarios_con_acceso_nc=self._calculate_ratio(
                    numerator=organizational_summary.usuarios_con_acceso_nc,
                    denominator=organizational_summary.total_usuarios,
                ),
                tasa_permisos_grupo_permitidos=self._calculate_ratio(
                    numerator=organizational_summary.permisos_grupo_permitidos,
                    denominator=organizational_summary.total_permisos_grupo,
                ),
                tasa_permisos_usuario_permitidos=self._calculate_ratio(
                    numerator=organizational_summary.permisos_usuario_permitidos,
                    denominator=organizational_summary.total_permisos_usuario,
                ),
            ),
        )
        logger.info(
            "Dashboard ejecutivo generado | ordenes=%s | solicitudes_nc=%s | informes=%s | repuestos=%s | clientes=%s | cas=%s | usuarios=%s | ingresos=%s",
            dashboard.operational.total_ordenes,
            dashboard.financial.total_solicitudes_nc,
            dashboard.technical.total_informes,
            dashboard.inventory.total_repuestos,
            dashboard.crm.total_clientes,
            dashboard.warranty.total_cas,
            dashboard.organizational.total_usuarios,
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
