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
from novitec_dwh.contexts.inventory.application.services import InventoryQueryService
from novitec_dwh.contexts.inventory.infrastructure.postgresql_inventory_query_repository import (
    PostgreSQLInventoryQueryRepository,
)
from novitec_dwh.contexts.technical.application.services import TechnicalQueryService
from novitec_dwh.contexts.technical.infrastructure.postgresql_technical_query_repository import (
    PostgreSQLTechnicalQueryRepository,
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
        technical_service=get_technical_query_service(),
        inventory_service=get_inventory_query_service(),
    )


def get_technical_query_service() -> TechnicalQueryService:
    """Construye el servicio de consultas tecnicas para la API."""

    settings = get_settings()
    connection_factory = PostgreSQLConnectionFactory(settings=settings)
    repository = PostgreSQLTechnicalQueryRepository(
        connection_factory=connection_factory,
        mart_schema=settings.postgres_technical_mart_schema,
    )
    return TechnicalQueryService(repository=repository)


def get_inventory_query_service() -> InventoryQueryService:
    """Construye el servicio de consultas de inventario para la API."""

    settings = get_settings()
    connection_factory = PostgreSQLConnectionFactory(settings=settings)
    repository = PostgreSQLInventoryQueryRepository(
        connection_factory=connection_factory,
        mart_schema=settings.postgres_inventory_mart_schema,
    )
    return InventoryQueryService(repository=repository)
