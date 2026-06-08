"""Esquemas Pydantic del dashboard ejecutivo para FastAPI."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from novitec_dwh.api.schemas.crm import CrmSummaryResponse
from novitec_dwh.api.schemas.financial import FinancialSummaryResponse
from novitec_dwh.api.schemas.inventory import InventorySummaryResponse
from novitec_dwh.api.schemas.operational import OperationalSummaryResponse
from novitec_dwh.api.schemas.organizational import OrganizationalSummaryResponse
from novitec_dwh.api.schemas.technical import TechnicalSummaryResponse
from novitec_dwh.api.schemas.warranty import WarrantySummaryResponse


class ExecutiveDashboardFiltersResponse(BaseModel):
    """Expone los filtros globales usados para el dashboard ejecutivo."""

    date_from: date | None
    date_to: date | None
    technician_name: str | None
    branch_name: str | None
    admin_name: str | None
    status_name: str | None
    order_type: str | None


class ExecutiveDashboardKpisResponse(BaseModel):
    """Expone indicadores ejecutivos derivados para lectura rápida."""

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
    tasa_clientes_con_correo: Decimal | None
    tasa_empresas_con_correo: Decimal | None
    tasa_sucursalescliente_activas: Decimal | None
    tasa_cas_activos: Decimal | None
    tasa_ordenes_personales_garantia_con_caso: Decimal | None
    tasa_ordenes_empresariales_garantia_con_ticket: Decimal | None
    tasa_usuarios_activos: Decimal | None
    tasa_usuarios_con_acceso_nc: Decimal | None
    tasa_permisos_grupo_permitidos: Decimal | None
    tasa_permisos_usuario_permitidos: Decimal | None


class ExecutiveDashboardResponse(BaseModel):
    """Representa la vista consolidada consumible por gerencia."""

    generated_at: datetime
    filters: ExecutiveDashboardFiltersResponse
    operational: OperationalSummaryResponse
    financial: FinancialSummaryResponse
    technical: TechnicalSummaryResponse
    inventory: InventorySummaryResponse
    crm: CrmSummaryResponse
    warranty: WarrantySummaryResponse
    organizational: OrganizationalSummaryResponse
    kpis: ExecutiveDashboardKpisResponse
