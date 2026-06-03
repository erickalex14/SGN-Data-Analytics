"""Punto de entrada ejecutable para levantar la API con Uvicorn."""

import uvicorn


def main() -> None:
    """Inicia el servidor HTTP principal de la aplicacion."""

    # Se centraliza el arranque para ofrecer un comando de consola estable.
    uvicorn.run(
        "novitec_dwh.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )
