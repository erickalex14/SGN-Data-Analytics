"""Esquemas Pydantic del dashboard ejecutivo para FastAPI."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel

from novitec_dwh.api.schemas.financial import FinancialSummaryResponse
from novitec_dwh.api.schemas.operational import OperationalSummaryResponse


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


class ExecutiveDashboardResponse(BaseModel):
    """Representa la vista consolidada consumible por gerencia."""

    generated_at: datetime
    filters: ExecutiveDashboardFiltersResponse
    operational: OperationalSummaryResponse
    financial: FinancialSummaryResponse
    kpis: ExecutiveDashboardKpisResponse
