"""Endpoints basicos para validacion operativa de la API."""

from fastapi import APIRouter

from novitec_dwh.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health", summary="Estado general del servicio")
def healthcheck() -> dict[str, str]:
    """Devuelve el estado minimo del servicio para monitoreo."""

    settings = get_settings()

    # Se expone una respuesta minima y estable para sondas de disponibilidad.
    return {
        "status": "ok",
        "application": settings.app_name,
        "environment": settings.app_env,
    }
