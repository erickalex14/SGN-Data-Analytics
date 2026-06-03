"""Lector de datasets financieros desde la zona raw basada en Parquet."""

from collections.abc import Iterator
import json
from pathlib import Path
from typing import TypeVar

import polars as pl

from novitec_dwh.contexts.financial.domain.entities import (
    NotificacionNotaCredito,
    PrecioOrden,
    SolicitudNotaCredito,
)

EntityType = TypeVar("EntityType")


class FilesystemFinancialRawReader:
    """Lee una corrida financiera ya extraida desde el sistema de archivos."""

    def __init__(self, base_path: Path, extraction_id: str | None = None) -> None:
        """Recibe la carpeta base raw y una corrida opcional a resolver."""

        self._base_path = Path(base_path)
        self._requested_extraction_id = extraction_id
        self._extraction_id: str | None = None
        self._run_directory: Path | None = None
        self._manifest: dict | None = None

    @property
    def extraction_id(self) -> str:
        """Expone el identificador de la corrida raw seleccionada."""

        if self._extraction_id is None:
            raise RuntimeError("La corrida raw todavia no fue preparada.")

        return self._extraction_id

    @property
    def run_directory(self) -> Path:
        """Expone la carpeta de la corrida raw seleccionada."""

        if self._run_directory is None:
            raise RuntimeError("La corrida raw todavia no fue preparada.")

        return self._run_directory

    def prepare(self) -> None:
        """Resuelve la corrida raw objetivo y valida su manifiesto."""

        if self._requested_extraction_id:
            run_directory = self._base_path / self._requested_extraction_id
        else:
            run_directory = self._resolve_latest_run_directory()

        manifest_path = run_directory / "manifest.json"
        if not manifest_path.exists():
            raise FileNotFoundError(
                f"No se encontro el manifiesto de la corrida financiera: {manifest_path.as_posix()}",
            )

        self._run_directory = run_directory
        self._manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self._extraction_id = str(self._manifest["extraction_id"])

    def read_credit_note_requests(self) -> Iterator[list[SolicitudNotaCredito]]:
        """Lee solicitudes de nota de credito desde archivos Parquet."""

        yield from self._read_dataset(
            dataset_name="solicitudes_nc",
            entity_class=SolicitudNotaCredito,
        )

    def read_order_prices(self) -> Iterator[list[PrecioOrden]]:
        """Lee precios por orden desde archivos Parquet."""

        yield from self._read_dataset(
            dataset_name="precios_orden",
            entity_class=PrecioOrden,
        )

    def read_credit_note_notifications(self) -> Iterator[list[NotificacionNotaCredito]]:
        """Lee notificaciones de nota de credito desde archivos Parquet."""

        yield from self._read_dataset(
            dataset_name="notificaciones",
            entity_class=NotificacionNotaCredito,
        )

    def _read_dataset(self, dataset_name: str, entity_class: type[EntityType]) -> Iterator[list[EntityType]]:
        """Carga cada archivo Parquet del dataset como un lote independiente."""

        if self._run_directory is None:
            raise RuntimeError("La corrida raw todavia no fue preparada.")

        dataset_directory = self._run_directory / dataset_name
        if not dataset_directory.exists():
            return

        for parquet_file in sorted(dataset_directory.glob("*.parquet")):
            rows = pl.read_parquet(parquet_file).to_dicts()
            yield [entity_class(**row) for row in rows]

    def _resolve_latest_run_directory(self) -> Path:
        """Localiza la corrida financiera mas reciente dentro de la zona raw."""

        if not self._base_path.exists():
            raise FileNotFoundError(
                f"La ruta base raw no existe: {self._base_path.as_posix()}",
            )

        candidates = sorted(
            [path for path in self._base_path.iterdir() if path.is_dir()],
            key=lambda path: path.name,
            reverse=True,
        )
        if not candidates:
            raise FileNotFoundError(
                f"No se encontraron corridas financieras en raw: {self._base_path.as_posix()}",
            )

        return candidates[0]
