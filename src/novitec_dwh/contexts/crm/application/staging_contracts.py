"""Contratos de aplicacion para la carga de CRM a staging."""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from novitec_dwh.contexts.crm.domain.entities import Cliente, Empresa, SucursalCliente


class CrmRawReader(Protocol):
    """Contrato para leer datasets CRM desde la zona raw."""

    @property
    def extraction_id(self) -> str:
        """Expone el identificador de la corrida raw seleccionada."""

    @property
    def run_directory(self) -> Path:
        """Expone la carpeta de la corrida raw seleccionada."""

    def prepare(self) -> None:
        """Resuelve y valida la corrida raw objetivo."""

    def read_customers(self) -> Iterator[list[Cliente]]:
        """Lee clientes desde raw por lotes."""

    def read_companies(self) -> Iterator[list[Empresa]]:
        """Lee empresas desde raw por lotes."""

    def read_customer_branches(self) -> Iterator[list[SucursalCliente]]:
        """Lee sucursales cliente desde raw por lotes."""


class CrmStagingRepository(Protocol):
    """Contrato para persistir el dominio CRM en staging PostgreSQL."""

    def prepare_schema(self) -> None:
        """Crea o ajusta la estructura CRM requerida en staging."""

    def prepare_extraction(self, extraction_id: str) -> None:
        """Limpia o inicializa el estado necesario para una corrida concreta."""

    def load_customers(self, extraction_id: str, records: list[Cliente]) -> None:
        """Carga clientes en staging."""

    def load_companies(self, extraction_id: str, records: list[Empresa]) -> None:
        """Carga empresas en staging."""

    def load_customer_branches(
        self,
        extraction_id: str,
        records: list[SucursalCliente],
    ) -> None:
        """Carga sucursales cliente en staging."""
