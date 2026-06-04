"""Middleware HTTP para trazabilidad y logging de acceso."""

import logging
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request

logger = logging.getLogger("novitec_dwh.api.access")


def register_http_middleware(app: FastAPI) -> None:
    """Registra el middleware HTTP comun de la API."""

    @app.middleware("http")
    async def add_request_context_and_access_log(request: Request, call_next):
        """Asigna request_id, mide tiempo y registra el acceso HTTP."""

        request_id = str(uuid4())
        request.state.request_id = request_id
        started_at = perf_counter()

        response = await call_next(request)

        duration_ms = round((perf_counter() - started_at) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "Solicitud HTTP procesada | request_id=%s | metodo=%s | ruta=%s | estado=%s | duracion_ms=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response
