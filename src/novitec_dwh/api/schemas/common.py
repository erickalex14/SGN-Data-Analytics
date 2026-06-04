"""Esquemas compartidos para respuestas tecnicas de la API."""

from datetime import datetime

from pydantic import BaseModel


class ApiErrorResponse(BaseModel):
    """Representa una respuesta de error uniforme de la API."""

    code: str
    message: str
    request_id: str
    path: str
    timestamp: datetime
    details: list[dict] | None = None


class ApiErrorEnvelopeResponse(BaseModel):
    """Envuelve el error uniforme para respuestas HTTP fallidas."""

    error: ApiErrorResponse
