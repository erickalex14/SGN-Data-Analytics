"""Configuracion estandar de logging para API y ETL."""

import logging
from pathlib import Path

from novitec_dwh.core.config import get_settings


def configure_logging(log_file_name: str | None = None) -> None:
    """Configura el logger raiz del proyecto con formato uniforme."""

    settings = get_settings()
    log_handlers: list[logging.Handler] = [logging.StreamHandler()]

    # Se crea el directorio de logs una sola vez para soportar ejecuciones
    # locales y automatizadas con el mismo esquema de salida.
    log_directory = Path(settings.log_directory)
    log_directory.mkdir(parents=True, exist_ok=True)

    if log_file_name:
        log_file_path = log_directory / log_file_name
        log_handlers.append(logging.FileHandler(log_file_path, encoding="utf-8"))

    # Se usa una configuracion unica para evitar handlers duplicados al importar
    # modulos desde diferentes puntos de entrada.
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=log_handlers,
        force=True,
    )
