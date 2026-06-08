"""Punto de entrada principal para la API REST."""

from fastapi import FastAPI

from novitec_dwh.api.exception_handlers import register_exception_handlers
from novitec_dwh.api.middleware import register_http_middleware
from novitec_dwh.api.routers.crm import router as crm_router
from novitec_dwh.api.routers.executive import router as executive_router
from novitec_dwh.api.routers.financial import router as financial_router
from novitec_dwh.api.routers.health import router as health_router
from novitec_dwh.api.routers.inventory import router as inventory_router
from novitec_dwh.api.routers.organizational import router as organizational_router
from novitec_dwh.api.routers.operational import router as operational_router
from novitec_dwh.api.routers.technical import router as technical_router
from novitec_dwh.api.routers.warranty import router as warranty_router
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging

# Se inicializa el sistema de logging al cargar la aplicacion para mantener
# un formato consistente tanto en la API como en los procesos ETL.
configure_logging(log_file_name="api.log")

settings = get_settings()

# Se construye la aplicacion FastAPI con metadatos centralizados para evitar
# duplicidad de configuracion entre entornos.
app = FastAPI(
    title=settings.app_name,
    description=(
        "API REST del Data Warehouse de Novitec para consulta ejecutiva, "
        "financiera y operativa del negocio de soporte tecnico."
    ),
    # Se desactiva el debug del framework para conservar respuestas de error
    # uniformes incluso en entornos locales.
    debug=False,
    version="0.1.0",
    contact={
        "name": "Equipo de Datos Novitec",
    },
    openapi_tags=[
        {
            "name": "health",
            "description": "Verificaciones tecnicas de disponibilidad de la API.",
        },
        {
            "name": "financial",
            "description": "Consultas del dominio financiero y de notas de credito.",
        },
        {
            "name": "operational",
            "description": "Consultas del dominio operativo, ordenes y preordenes.",
        },
        {
            "name": "dashboard",
            "description": "Vistas ejecutivas consolidadas para gerencia.",
        },
        {
            "name": "technical",
            "description": "Consultas del dominio tecnico, informes y equipos.",
        },
        {
            "name": "inventory",
            "description": "Consultas del dominio de inventario, repuestos y abastecimiento.",
        },
        {
            "name": "crm",
            "description": "Consultas del dominio CRM, clientes, empresas y sucursales.",
        },
        {
            "name": "warranty",
            "description": "Consultas del dominio de garantias, CAS y ordenes asociadas.",
        },
        {
            "name": "organizational",
            "description": "Consultas del dominio organizacional, usuarios, sucursales y permisos.",
        },
    ],
)

# Se registran middleware y handlers globales para trazabilidad uniforme.
register_http_middleware(app)
register_exception_handlers(app)

# Se registran los routers versionados para mantener compatibilidad futura.
app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(financial_router, prefix=settings.api_v1_prefix)
app.include_router(operational_router, prefix=settings.api_v1_prefix)
app.include_router(executive_router, prefix=settings.api_v1_prefix)
app.include_router(technical_router, prefix=settings.api_v1_prefix)
app.include_router(inventory_router, prefix=settings.api_v1_prefix)
app.include_router(crm_router, prefix=settings.api_v1_prefix)
app.include_router(warranty_router, prefix=settings.api_v1_prefix)
app.include_router(organizational_router, prefix=settings.api_v1_prefix)
