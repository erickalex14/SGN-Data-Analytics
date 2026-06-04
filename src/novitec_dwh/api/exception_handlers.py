"""Manejadores globales de errores para respuestas HTTP uniformes."""

import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from novitec_dwh.api.schemas.common import ApiErrorEnvelopeResponse

logger = logging.getLogger("novitec_dwh.api.errors")


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los manejadores globales de excepciones de la API."""

    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, handle_unexpected_exception)


async def handle_http_exception(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Devuelve un error HTTP uniforme para excepciones controladas."""

    message = str(exc.detail)
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        message = "Recurso no encontrado."

    logger.warning(
        "Solicitud HTTP rechazada | request_id=%s | metodo=%s | ruta=%s | estado=%s | detalle=%s",
        _get_request_id(request),
        request.method,
        request.url.path,
        exc.status_code,
        message,
    )
    return _build_error_response(
        request=request,
        status_code=exc.status_code,
        code=_map_status_code_to_error_code(exc.status_code),
        message=message,
    )


async def handle_validation_exception(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Devuelve un error uniforme para entradas invalidas del cliente."""

    details = [
        {
            "location": list(error["loc"]),
            "message": error["msg"],
            "type": error["type"],
        }
        for error in exc.errors()
    ]
    logger.warning(
        "Solicitud invalida detectada | request_id=%s | metodo=%s | ruta=%s | errores=%s",
        _get_request_id(request),
        request.method,
        request.url.path,
        len(details),
    )
    return _build_error_response(
        request=request,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="La solicitud contiene parametros invalidos.",
        details=details,
    )


async def handle_unexpected_exception(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Devuelve un error uniforme para fallos no controlados."""

    logger.exception(
        "Error interno no controlado | request_id=%s | metodo=%s | ruta=%s | tipo=%s",
        _get_request_id(request),
        request.method,
        request.url.path,
        exc.__class__.__name__,
    )
    return _build_error_response(
        request=request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_server_error",
        message="Ocurrio un error interno en el servidor.",
    )


def _build_error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: list[dict] | None = None,
) -> JSONResponse:
    """Construye una respuesta JSON uniforme para cualquier error API."""

    request_id = _get_request_id(request)
    payload = ApiErrorEnvelopeResponse(
        error={
            "code": code,
            "message": message,
            "request_id": request_id,
            "path": request.url.path,
            "timestamp": datetime.now(timezone.utc),
            "details": details,
        }
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        headers={"X-Request-ID": request_id},
    )


def _get_request_id(request: Request) -> str:
    """Obtiene el request_id generado por middleware o un valor por defecto."""

    return getattr(request.state, "request_id", "sin-request-id")


def _map_status_code_to_error_code(status_code: int) -> str:
    """Mapea estados HTTP comunes a codigos semanticos estables."""

    return {
        status.HTTP_400_BAD_REQUEST: "bad_request",
        status.HTTP_401_UNAUTHORIZED: "unauthorized",
        status.HTTP_403_FORBIDDEN: "forbidden",
        status.HTTP_404_NOT_FOUND: "not_found",
        status.HTTP_409_CONFLICT: "conflict",
    }.get(status_code, "http_error")
