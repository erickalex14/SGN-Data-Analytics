"""DTOs del contexto ejecutivo."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from novitec_dwh.contexts.financial.application.dto import FinancialSummary
from novitec_dwh.contexts.inventory.application.dto_query import InventorySummary
from novitec_dwh.contexts.operational.application.dto_query import OperationalSummary
from novitec_dwh.contexts.technical.application.dto_query import TechnicalSummary


@dataclass(slots=True)
class ExecutiveDashboardFilters:
    """Representa los filtros globales aplicados al dashboard ejecutivo."""

    date_from: date | None
    date_to: date | None
    technician_name: str | None
    branch_name: str | None
    admin_name: str | None
    status_name: str | None
    order_type: str | None


@dataclass(slots=True)
class ExecutiveDashboardKpis:
    """Representa indicadores derivados para lectura gerencial."""

    tasa_aprobacion_nc: Decimal | None
    tasa_notificaciones_leidas: Decimal | None
    tasa_ordenes_entregadas: Decimal | None
    tasa_ordenes_abiertas: Decimal | None
    tasa_ordenes_garantia: Decimal | None
    tasa_informes_equipo_operativo: Decimal | None
    tasa_informes_con_presupuesto: Decimal | None
    tasa_equipos_con_contrasena: Decimal | None
    tasa_repuestos_con_stock: Decimal | None
    tasa_solicitudes_repuesto_aprobadas: Decimal | None
    tasa_solicitudes_repuesto_pendientes: Decimal | None


@dataclass(slots=True)
class ExecutiveDashboard:
    """Agrupa la vista consolidada de resumen financiero, operativo, tecnico e inventario."""

    generated_at: datetime
    filters: ExecutiveDashboardFilters
    operational: OperationalSummary
    financial: FinancialSummary
    technical: TechnicalSummary
    inventory: InventorySummary
    kpis: ExecutiveDashboardKpis
