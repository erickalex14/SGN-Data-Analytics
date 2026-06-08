"""Persistencia de extracciones de garantias sobre el sistema de archivos."""

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
import json
from pathlib import Path
from typing import Any

import polars as pl
from polars.exceptions import ComputeError

from novitec_dwh.contexts.warranty.application.dto import WarrantyExtractionSummary


class FilesystemWarrantyExtractionSink:
    """Persiste la corrida de garantias en una zona raw basada en Parquet."""

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
        dataframe = self._build_dataframe(rows=normalized_rows)
        dataframe.write_parquet(output_file)

        dataset_manifest = self._manifest_data["datasets"].setdefault(
            dataset_name,
            {"records": 0, "chunks": 0, "files": []},
        )
        dataset_manifest["records"] += len(normalized_rows)
        dataset_manifest["chunks"] += 1
        dataset_manifest["files"].append(output_file.as_posix())
        return output_file

    def finalize(self, summary: WarrantyExtractionSummary) -> None:
        """Genera el manifiesto final de la corrida en formato JSON."""

        if self._manifest_path is None:
            raise RuntimeError("La ruta del manifiesto no fue inicializada.")

        self._manifest_data["finished_at"] = (
            summary.finished_at.isoformat() if summary.finished_at else None
        )
        self._manifest_data["summary"] = {
            "cas": summary.cas,
            "cas_chunks": summary.cas_chunks,
            "usuariocas": summary.usuariocas,
            "usuariocas_chunks": summary.usuariocas_chunks,
            "ordenes_garantia": summary.ordenes_garantia,
            "ordenes_garantia_chunks": summary.ordenes_garantia_chunks,
            "ordenesempresas_garantia": summary.ordenesempresas_garantia,
            "ordenesempresas_garantia_chunks": summary.ordenesempresas_garantia_chunks,
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

    def _build_dataframe(self, rows: list[dict[str, Any]]) -> pl.DataFrame:
        """Construye un DataFrame robusto para columnas con tipos mezclados."""

        try:
            return pl.from_dicts(rows, infer_schema_length=None)
        except ComputeError:
            return pl.from_dicts(
                self._coerce_mixed_columns_to_string(rows=rows),
                infer_schema_length=None,
            )

    def _coerce_mixed_columns_to_string(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Convierte a texto las columnas cuyo tipo varia entre filas."""

        column_types: dict[str, set[type]] = {}
        for row in rows:
            for key, value in row.items():
                if value is None:
                    continue
                column_types.setdefault(key, set()).add(type(value))

        mixed_columns = {key for key, types in column_types.items() if len(types) > 1}
        if not mixed_columns:
            return rows

        coerced_rows: list[dict[str, Any]] = []
        for row in rows:
            coerced_row: dict[str, Any] = {}
            for key, value in row.items():
                if key in mixed_columns and value is not None:
                    coerced_row[key] = str(value)
                else:
                    coerced_row[key] = value
            coerced_rows.append(coerced_row)
        return coerced_rows
