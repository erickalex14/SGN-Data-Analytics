"""Pruebas del caso de uso de extraccion CRM."""

from collections.abc import Iterator
from datetime import datetime

from novitec_dwh.contexts.crm.application.use_cases.extract_crm_domain import (
    ExtractCrmDomainUseCase,
)
from novitec_dwh.contexts.crm.domain.entities import Cliente, Empresa, SucursalCliente
from novitec_dwh.contexts.crm.infrastructure.filesystem_crm_extraction_sink import (
    FilesystemCrmExtractionSink,
)


class FakeCrmExtractionRepository:
    """Doblez de pruebas para validar el flujo del caso de uso CRM."""

    def extract_customers(self, chunk_size: int) -> Iterator[list[Cliente]]:
        """Devuelve un unico lote simulado de clientes."""

        _ = chunk_size
        yield [
            Cliente(
                id=1,
                nombres="Juan",
                apellidos="Perez",
                identificacion="0102030405",
                numero_contacto="0999999999",
                correo="juan@example.com",
                direccion_clientes="Quito",
            )
        ]

    def extract_companies(self, chunk_size: int) -> Iterator[list[Empresa]]:
        """Devuelve un unico lote simulado de empresas."""

        _ = chunk_size
        yield [
            Empresa(
                id=1,
                nombre="Empresa Demo",
                ruc="1799999999001",
                telefono="022000000",
                correo="contacto@demo.com",
                direccion_empresa="Av. Principal",
                created_at=datetime(2026, 6, 5, 9, 0, 0),
            )
        ]

    def extract_customer_branches(self, chunk_size: int) -> Iterator[list[SucursalCliente]]:
        """Devuelve un unico lote simulado de sucursales cliente."""

        _ = chunk_size
        yield [
            SucursalCliente(
                id=1,
                codigo="N001",
                numero=1,
                nombre="Sucursal Norte",
                provincia="Pichincha",
                novitec_sucursal="UIO",
                activa=True,
                created_at=datetime(2026, 6, 5, 10, 0, 0),
            )
        ]


def test_execute_resume_correctamente_los_registros(tmp_path) -> None:
    """Valida que el caso de uso CRM acumule el volumen total por entidad."""

    repository = FakeCrmExtractionRepository()
    sink = FilesystemCrmExtractionSink(base_path=tmp_path / "raw")
    use_case = ExtractCrmDomainUseCase(repository=repository, sink=sink)

    summary = use_case.execute(chunk_size=100)

    assert summary.clientes == 1
    assert summary.clientes_chunks == 1
    assert summary.empresas == 1
    assert summary.empresas_chunks == 1
    assert summary.sucursalescliente == 1
    assert summary.sucursalescliente_chunks == 1
    assert summary.output_directory is not None
    assert summary.manifest_path is not None
    assert (tmp_path / "raw").exists()
