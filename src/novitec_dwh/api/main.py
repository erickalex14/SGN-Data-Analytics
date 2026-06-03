"""Punto de entrada principal para la API REST."""

from fastapi import FastAPI

from novitec_dwh.api.routers.health import router as health_router
from novitec_dwh.core.config import get_settings
from novitec_dwh.core.logging import configure_logging

# Se inicializa el sistema de logging al cargar la aplicacion para mantener
# un formato consistente tanto en la API como en los procesos ETL.
configure_logging()

settings = get_settings()

# Se construye la aplicacion FastAPI con metadatos centralizados para evitar
# duplicidad de configuracion entre entornos.
app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

# Se registran los routers versionados para mantener compatibilidad futura.
app.include_router(health_router, prefix=settings.api_v1_prefix)
