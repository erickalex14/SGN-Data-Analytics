"""Contratos del dominio CRM."""

from collections.abc import Iterator
from typing import Protocol

from novitec_dwh.contexts.crm.domain.entities import Cliente, Empresa, SucursalCliente


class CrmExtractionRepository(Protocol):
    """Contrato para la extraccion del dominio CRM."""

    def extract_customers(self, chunk_size: int) -> Iterator[list[Cliente]]:
        """Extrae clientes finales por lotes."""

    def extract_companies(self, chunk_size: int) -> Iterator[list[Empresa]]:
        """Extrae empresas por lotes."""

    def extract_customer_branches(self, chunk_size: int) -> Iterator[list[SucursalCliente]]:
        """Extrae sucursales cliente por lotes."""
