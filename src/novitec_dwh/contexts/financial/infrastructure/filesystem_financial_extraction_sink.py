"""Persistencia de extracciones financieras sobre el sistema de archivos."""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
from typing import Any

import polars as pl

from novitec_dwh.contexts.financial.application.dto import FinancialExtractionSummary


class FilesystemFinancialExtractionSink:
    """Persiste la corrida financiera en una zona raw basada en Parquet."""

    def __init__(self, base_path: Path) -> None:
        """Recibe la carpeta raiz donde se almacenaran las corridas."""

        self._base_path = Path(base_path)
        self._run_directory: Path | None = None
        self._manifest_path: Path | None = None
        self._manifest_data: dict[str, Any] = {}

    @property
    def run_directory(self) -> Path | None:
        """Expone la carpeta base generada para la corrida actual."""

        return self._run_directory

    @property
    def manifest_path(self) -> Path | None:
        """Expone la ruta del manifiesto final de la corrida."""

        return self._manifest_path

    def start(self, extraction_id: str, started_at: datetime) -> None:
        """Inicializa directorios y metadatos base de la corrida."""

        self._run_directory = self._base_path / extraction_id
        self._run_directory.mkdir(parents=True, exist_ok=True)
        self._manifest_path = self._run_directory / "manifest.json"
        self._manifest_data = {
            "extraction_id": extraction_id,
            "started_at": started_at.isoformat(),
            "datasets": {},
        }

    def write(self, dataset_name: str, chunk_number: int, records: list[object]) -> Path:
        """Escribe un lote del dataset indicado en formato Parquet."""

        if self._run_directory is None:
            raise RuntimeError("La corrida de extraccion no fue inicializada.")

        dataset_directory = self._run_directory / dataset_name
        dataset_directory.mkdir(parents=True, exist_ok=True)

        output_file = dataset_directory / f"part-{chunk_number:05d}.parquet"
        normalized_rows = [self._normalize_record(record=record) for record in records]
        dataframe = pl.DataFrame(normalized_rows, strict=False)
        dataframe.write_parquet(output_file)

        dataset_manifest = self._manifest_data["datasets"].setdefault(
            dataset_name,
            {
                "records": 0,
                "chunks": 0,
                "files": [],
            },
        )
        dataset_manifest["records"] += len(normalized_rows)
        dataset_manifest["chunks"] += 1
        dataset_manifest["files"].append(output_file.as_posix())

        return output_file

    def finalize(self, summary: FinancialExtractionSummary) -> None:
        """Genera el manifiesto final de la corrida en formato JSON."""

        if self._manifest_path is None:
            raise RuntimeError("La ruta del manifiesto no fue inicializada.")

        self._manifest_data["finished_at"] = (
            summary.finished_at.isoformat() if summary.finished_at else None
        )
        self._manifest_data["summary"] = {
            "solicitudes_nc": summary.solicitudes_nc,
            "solicitudes_nc_chunks": summary.solicitudes_nc_chunks,
            "precios_orden": summary.precios_orden,
            "precios_orden_chunks": summary.precios_orden_chunks,
            "notificaciones": summary.notificaciones,
            "notificaciones_chunks": summary.notificaciones_chunks,
        }

        self._manifest_path.write_text(
            json.dumps(self._manifest_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _normalize_record(self, record: object) -> dict[str, Any]:
        """Convierte una entidad a un diccionario serializable para Parquet."""

        if not is_dataclass(record):
            raise TypeError("Cada registro a persistir debe ser un dataclass.")

        return self._normalize_value(value=asdict(record))

    def _normalize_value(self, value: Any) -> Any:
        """Normaliza valores complejos conservando la semantica analitica."""

        if isinstance(value, dict):
            return {key: self._normalize_value(item) for key, item in value.items()}

        if isinstance(value, list):
            return [self._normalize_value(item) for item in value]

        if isinstance(value, Decimal):
            return value

        if isinstance(value, (datetime, date)):
            return value

        return value
