"""Contratos de aplicacion para la carga operativa a staging."""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from novitec_dwh.contexts.operational.domain.entities import (
    OrdenEmpresa,
    OrdenEmpresaTecnico,
    OrdenPersonal,
    PreOrden,
    VistaOrden,
)


class OperationalRawReader(Protocol):
    """Contrato para leer datasets operativos desde la zona raw."""

    @property
    def extraction_id(self) -> str:
        """Expone el identificador de la corrida raw seleccionada."""

    @property
    def run_directory(self) -> Path:
        """Expone la carpeta de la corrida raw seleccionada."""

    def prepare(self) -> None:
        """Resuelve y valida la corrida raw objetivo."""

    def read_order_view(self) -> Iterator[list[VistaOrden]]:
        """Lee la vista de ordenes desde raw por lotes."""

    def read_personal_orders(self) -> Iterator[list[OrdenPersonal]]:
        """Lee ordenes personales desde raw por lotes."""

    def read_company_orders(self) -> Iterator[list[OrdenEmpresa]]:
        """Lee ordenes empresariales desde raw por lotes."""

    def read_preorders(self) -> Iterator[list[PreOrden]]:
        """Lee preordenes desde raw por lotes."""

    def read_company_order_technicians(self) -> Iterator[list[OrdenEmpresaTecnico]]:
        """Lee asignaciones tecnico-orden empresarial desde raw por lotes."""


class OperationalStagingRepository(Protocol):
    """Contrato para persistir el dominio operativo en staging PostgreSQL."""

    def prepare_schema(self) -> None:
        """Crea o ajusta la estructura tecnica requerida en staging."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia o inicializa el estado necesario para una corrida concreta."""

    def load_order_view(self, extraction_id: str, records: list[VistaOrden]) -> None:
        """Carga la vista de ordenes en staging."""

    def load_personal_orders(self, extraction_id: str, records: list[OrdenPersonal]) -> None:
        """Carga ordenes personales en staging."""

    def load_company_orders(self, extraction_id: str, records: list[OrdenEmpresa]) -> None:
        """Carga ordenes empresariales en staging."""

    def load_preorders(self, extraction_id: str, records: list[PreOrden]) -> None:
        """Carga preordenes en staging."""

    def load_company_order_technicians(
        self,
        extraction_id: str,
        records: list[OrdenEmpresaTecnico],
    ) -> None:
        """Carga asignaciones tecnico-orden empresarial en staging."""
