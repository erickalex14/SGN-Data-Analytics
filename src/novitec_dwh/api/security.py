"""Dependencias de seguridad para proteger endpoints de la API."""

import logging
from secrets import compare_digest

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from novitec_dwh.core.config import get_settings

bearer_scheme = HTTPBearer(auto_error=False)
logger = logging.getLogger("novitec_dwh.api.security")


def require_api_auth(
    credentials: HTTPAuthorizationCredentials | None = Security(bearer_scheme),
) -> None:
    """Valida un bearer token estatico para la primera capa de proteccion."""

    settings = get_settings()
    if not settings.api_auth_enabled:
        return

    if not settings.api_auth_token:
        logger.error("La autenticacion de API esta habilitada pero no existe token configurado.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="La autenticacion de la API esta habilitada pero no tiene token configurado.",
        )

    if credentials is None or credentials.scheme.lower() != "bearer":
        logger.warning("Acceso rechazado por ausencia de credenciales bearer validas.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autorizado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not compare_digest(credentials.credentials, settings.api_auth_token):
        logger.warning("Acceso rechazado por token invalido.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido.",
            headers={"WWW-Authenticate": "Bearer"},
        )
