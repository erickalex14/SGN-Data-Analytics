"""Endpoints HTTP del dashboard ejecutivo."""

from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends, Query, Security

from novitec_dwh.api.dependencies import get_executive_dashboard_service
from novitec_dwh.api.schemas.executive import ExecutiveDashboardResponse
from novitec_dwh.api.schemas.financial import FinancialSummaryResponse
from novitec_dwh.api.schemas.inventory import InventorySummaryResponse
from novitec_dwh.api.schemas.operational import OperationalSummaryResponse
from novitec_dwh.api.schemas.technical import TechnicalSummaryResponse
from novitec_dwh.api.security import require_api_auth
from novitec_dwh.contexts.executive.application.services import ExecutiveDashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Security(require_api_auth)],
)


@router.get("/executive", response_model=ExecutiveDashboardResponse, summary="Dashboard ejecutivo")
def get_executive_dashboard(
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    technician_name: str | None = Query(default=None),
    branch_name: str | None = Query(default=None),
    admin_name: str | None = Query(default=None),
    status_name: str | None = Query(default=None),
    order_type: str | None = Query(default=None),
    service: ExecutiveDashboardService = Depends(get_executive_dashboard_service),
) -> ExecutiveDashboardResponse:
    """Devuelve un resumen consolidado para consumo gerencial."""

    dashboard = service.get_dashboard(
        date_from=date_from,
        date_to=date_to,
        technician_name=technician_name,
        branch_name=branch_name,
        admin_name=admin_name,
        status_name=status_name,
        order_type=order_type,
    )
    return ExecutiveDashboardResponse(
        generated_at=dashboard.generated_at,
        filters=asdict(dashboard.filters),
        operational=OperationalSummaryResponse(**asdict(dashboard.operational)),
        financial=FinancialSummaryResponse(**asdict(dashboard.financial)),
        technical=TechnicalSummaryResponse(**asdict(dashboard.technical)),
        inventory=InventorySummaryResponse(**asdict(dashboard.inventory)),
        kpis=asdict(dashboard.kpis),
    )
