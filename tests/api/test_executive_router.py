"""Pruebas del endpoint ejecutivo consolidado."""

from datetime import date, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from novitec_dwh.api.dependencies import get_executive_dashboard_service
from novitec_dwh.api.main import app
from novitec_dwh.core.config import get_settings
from novitec_dwh.contexts.crm.application.dto_query import CrmSummary
from novitec_dwh.contexts.executive.application.dto import (
    ExecutiveDashboard,
    ExecutiveDashboardFilters,
    ExecutiveDashboardKpis,
)
from novitec_dwh.contexts.financial.application.dto import FinancialSummary
from novitec_dwh.contexts.inventory.application.dto_query import InventorySummary
from novitec_dwh.contexts.operational.application.dto_query import OperationalSummary
from novitec_dwh.contexts.organizational.application.dto_query import OrganizationalSummary
from novitec_dwh.contexts.technical.application.dto_query import TechnicalSummary
from novitec_dwh.contexts.warranty.application.dto_query import WarrantySummary


class FakeExecutiveDashboardService:
    """Doblez de servicio para probar el endpoint ejecutivo sin PostgreSQL."""

    def __init__(self) -> None:
        """Inicializa un contenedor para capturar filtros del dashboard."""

        self.last_filters: dict | None = None

    def get_dashboard(self, **kwargs) -> ExecutiveDashboard:
        """Devuelve un dashboard ejecutivo fijo para pruebas."""

        self.last_filters = kwargs
        return ExecutiveDashboard(
            generated_at=datetime(2026, 6, 4, 16, 30, 0),
            filters=ExecutiveDashboardFilters(
                date_from=kwargs.get("date_from"),
                date_to=kwargs.get("date_to"),
                technician_name=kwargs.get("technician_name"),
                branch_name=kwargs.get("branch_name"),
                admin_name=kwargs.get("admin_name"),
                status_name=kwargs.get("status_name"),
                order_type=kwargs.get("order_type"),
            ),
            operational=OperationalSummary(
                extraction_id="operational_20260604_202615",
                total_ordenes=1500,
                ordenes_abiertas=700,
                ordenes_entregadas=650,
                ordenes_con_garantia=120,
                total_preordenes=60,
                total_asignaciones_tecnicos=12,
                promedio_dias_ciclo=Decimal("4.50"),
            ),
            financial=FinancialSummary(
                extraction_id="financial_20260603_204252",
                total_solicitudes_nc=226,
                solicitudes_aprobadas=182,
                solicitudes_rechazadas=4,
                solicitudes_pendientes=40,
                total_registros_ingreso=39,
                monto_total_ingresos=Decimal("546.00"),
                total_notificaciones=831,
                total_notificaciones_leidas=500,
            ),
            technical=TechnicalSummary(
                extraction_id="technical_20260605_101500",
                total_informes=320,
                informes_equipo_operativo=180,
                informes_con_presupuesto=140,
                total_fotos_informes=900,
                total_equipos=280,
                equipos_con_contrasena=210,
                total_accesos_equipos=260,
            ),
            inventory=InventorySummary(
                extraction_id="inventory_20260605_173536",
                total_repuestos=2086,
                repuestos_con_stock=1560,
                stock_total_unidades=4820,
                costo_total_inventario=Decimal("153240.50"),
                total_consumos_orden=16,
                cantidad_total_consumida=28,
                total_solicitudes_repuesto=12,
                solicitudes_aprobadas=5,
                solicitudes_rechazadas=1,
                solicitudes_pendientes=6,
                total_listas_compra=4,
            ),
            crm=CrmSummary(
                extraction_id="crm_20260605_140000",
                total_clientes=120,
                clientes_con_correo=85,
                clientes_con_direccion=97,
                clientes_con_contacto=118,
                total_empresas=24,
                empresas_con_correo=20,
                empresas_con_telefono=22,
                total_sucursalescliente=51,
                sucursalescliente_activas=46,
            ),
            warranty=WarrantySummary(
                extraction_id="warranty_20260608_150000",
                total_cas=12,
                cas_activos=10,
                total_ordenes_personales=85,
                ordenes_personales_con_caso=58,
                ordenes_personales_cerradas=49,
                total_ordenes_empresariales=19,
                ordenes_empresariales_con_ticket=14,
                ordenes_empresariales_con_horas=11,
                total_asignaciones_usuario_cas=9,
            ),
            organizational=OrganizationalSummary(
                extraction_id="organizational_20260608_220000",
                total_usuarios=24,
                usuarios_activos=20,
                usuarios_con_correo=18,
                usuarios_con_telefono=16,
                usuarios_con_acceso_nc=7,
                usuarios_con_grupo_acceso=19,
                total_asignaciones_sucursal=30,
                total_permisos_grupo=80,
                permisos_grupo_permitidos=65,
                total_permisos_usuario=12,
                permisos_usuario_permitidos=9,
            ),
            kpis=ExecutiveDashboardKpis(
                tasa_aprobacion_nc=Decimal("80.53"),
                tasa_notificaciones_leidas=Decimal("60.17"),
                tasa_ordenes_entregadas=Decimal("43.33"),
                tasa_ordenes_abiertas=Decimal("46.67"),
                tasa_ordenes_garantia=Decimal("8.00"),
                tasa_informes_equipo_operativo=Decimal("56.25"),
                tasa_informes_con_presupuesto=Decimal("43.75"),
                tasa_equipos_con_contrasena=Decimal("75.00"),
                tasa_repuestos_con_stock=Decimal("74.78"),
                tasa_solicitudes_repuesto_aprobadas=Decimal("41.67"),
                tasa_solicitudes_repuesto_pendientes=Decimal("50.00"),
                tasa_clientes_con_correo=Decimal("70.83"),
                tasa_empresas_con_correo=Decimal("83.33"),
                tasa_sucursalescliente_activas=Decimal("90.20"),
                tasa_cas_activos=Decimal("83.33"),
                tasa_ordenes_personales_garantia_con_caso=Decimal("68.24"),
                tasa_ordenes_empresariales_garantia_con_ticket=Decimal("73.68"),
                tasa_usuarios_activos=Decimal("83.33"),
                tasa_usuarios_con_acceso_nc=Decimal("29.17"),
                tasa_permisos_grupo_permitidos=Decimal("81.25"),
                tasa_permisos_usuario_permitidos=Decimal("75.00"),
            ),
        )


def test_get_executive_dashboard() -> None:
    """Valida la respuesta base del dashboard ejecutivo."""

    app.dependency_overrides[get_executive_dashboard_service] = lambda: FakeExecutiveDashboardService()
    client = TestClient(app)

    response = client.get("/api/v1/dashboard/executive")

    assert response.status_code == 200
    assert response.json()["operational"]["total_ordenes"] == 1500
    assert response.json()["financial"]["total_solicitudes_nc"] == 226
    assert response.json()["technical"]["total_informes"] == 320
    assert response.json()["inventory"]["total_repuestos"] == 2086
    assert response.json()["crm"]["total_clientes"] == 120
    assert response.json()["warranty"]["total_cas"] == 12
    assert response.json()["organizational"]["total_usuarios"] == 24
    assert response.json()["kpis"]["tasa_aprobacion_nc"] == "80.53"
    assert response.json()["kpis"]["tasa_informes_equipo_operativo"] == "56.25"
    assert response.json()["kpis"]["tasa_repuestos_con_stock"] == "74.78"
    assert response.json()["kpis"]["tasa_clientes_con_correo"] == "70.83"
    assert response.json()["kpis"]["tasa_cas_activos"] == "83.33"
    assert response.json()["kpis"]["tasa_usuarios_activos"] == "83.33"

    app.dependency_overrides.clear()


def test_get_executive_dashboard_with_filters() -> None:
    """Valida que los filtros globales lleguen al servicio ejecutivo."""

    fake_service = FakeExecutiveDashboardService()
    app.dependency_overrides[get_executive_dashboard_service] = lambda: fake_service
    client = TestClient(app)

    response = client.get(
        "/api/v1/dashboard/executive",
        params={
            "date_from": "2026-06-01",
            "date_to": "2026-06-30",
            "technician_name": "Tecnico 1",
            "branch_name": "Quito",
            "admin_name": "Supervisor",
            "status_name": "Aprobada",
            "order_type": "personal",
        },
    )

    assert response.status_code == 200
    assert response.json()["filters"]["branch_name"] == "Quito"
    assert fake_service.last_filters == {
        "date_from": date(2026, 6, 1),
        "date_to": date(2026, 6, 30),
        "technician_name": "Tecnico 1",
        "branch_name": "Quito",
        "admin_name": "Supervisor",
        "status_name": "Aprobada",
        "order_type": "personal",
    }

    app.dependency_overrides.clear()


def test_executive_endpoint_requires_token_when_auth_is_enabled() -> None:
    """Valida que el dashboard ejecutivo exija token cuando la auth esta activa."""

    settings = get_settings()
    original_enabled = settings.api_auth_enabled
    original_token = settings.api_auth_token
    settings.api_auth_enabled = True
    settings.api_auth_token = "token-prueba"

    try:
        app.dependency_overrides[get_executive_dashboard_service] = lambda: FakeExecutiveDashboardService()
        client = TestClient(app)

        response = client.get("/api/v1/dashboard/executive")

        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthorized"
    finally:
        settings.api_auth_enabled = original_enabled
        settings.api_auth_token = original_token
        app.dependency_overrides.clear()
