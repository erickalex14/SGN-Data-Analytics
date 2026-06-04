"""Dependencias de FastAPI para ensamblar servicios de aplicacion."""

from novitec_dwh.contexts.executive.application.services import ExecutiveDashboardService
from novitec_dwh.contexts.financial.application.services import FinancialQueryService
from novitec_dwh.contexts.financial.infrastructure.postgresql_financial_query_repository import (
    PostgreSQLFinancialQueryRepository,
)
from novitec_dwh.contexts.operational.application.services import OperationalQueryService
from novitec_dwh.contexts.operational.infrastructure.postgresql_operational_query_repository import (
    PostgreSQLOperationalQueryRepository,
)
from novitec_dwh.core.config import get_settings
from novitec_dwh.shared.infrastructure.postgresql import PostgreSQLConnectionFactory


def get_financial_query_service() -> FinancialQueryService:
    """Construye el servicio de consultas financieras para la API."""

    settings = get_settings()
    connection_factory = PostgreSQLConnectionFactory(settings=settings)
    repository = PostgreSQLFinancialQueryRepository(
        connection_factory=connection_factory,
        mart_schema=settings.postgres_financial_mart_schema,
    )
    return FinancialQueryService(repository=repository)


def get_operational_query_service() -> OperationalQueryService:
    """Construye el servicio de consultas operativas para la API."""

    settings = get_settings()
    connection_factory = PostgreSQLConnectionFactory(settings=settings)
    repository = PostgreSQLOperationalQueryRepository(
        connection_factory=connection_factory,
        mart_schema=settings.postgres_operational_mart_schema,
    )
    return OperationalQueryService(repository=repository)


def get_executive_dashboard_service() -> ExecutiveDashboardService:
    """Construye el servicio consolidado del dashboard ejecutivo."""

    return ExecutiveDashboardService(
        financial_service=get_financial_query_service(),
        operational_service=get_operational_query_service(),
    )
