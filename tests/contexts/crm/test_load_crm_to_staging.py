"""Pruebas del caso de uso de carga de CRM a staging."""

from collections.abc import Iterator
from datetime import datetime
from pathlib import Path

from novitec_dwh.contexts.crm.application.use_cases.load_crm_to_staging import (
    LoadCrmToStagingUseCase,
)
from novitec_dwh.contexts.crm.domain.entities import Cliente, Empresa, SucursalCliente


class FakeCrmRawReader:
    """Doblez de lectura raw para validar la orquestacion CRM a staging."""

    def __init__(self) -> None:
        """Inicializa el estado simulado de la corrida."""

        self._prepared = False

    @property
    def extraction_id(self) -> str:
        """Expone el identificador simulado de la corrida."""

        return "crm_20260605_140000"

    @property
    def run_directory(self) -> Path:
        """Expone una ruta raw simulada."""

        return Path("data/raw/crm/crm_20260605_140000")

    def prepare(self) -> None:
        """Marca la corrida como preparada."""

        self._prepared = True

    def read_customers(self) -> Iterator[list[Cliente]]:
        """Entrega un lote simulado de clientes."""

        assert self._prepared is True
        yield [
            Cliente(
                id=1,
                nombres="Juan",
                apellidos="Perez",
                identificacion="0102030405",
                numero_contacto="0999999999",
                correo="juan@example.com",
                direccion_clientes="Av. Principal",
            )
        ]

    def read_companies(self) -> Iterator[list[Empresa]]:
        """Entrega un lote simulado de empresas."""

        assert self._prepared is True
        yield [
            Empresa(
                id=1,
                nombre="Empresa Uno",
                ruc="1799999999001",
                telefono="022222222",
                correo="contacto@empresauno.com",
                direccion_empresa="Centro Norte",
                created_at=datetime(2026, 6, 5, 14, 0, 0),
            )
        ]

    def read_customer_branches(self) -> Iterator[list[SucursalCliente]]:
        """Entrega un lote simulado de sucursales cliente."""

        assert self._prepared is True
        yield [
            SucursalCliente(
                id=1,
                codigo="SC-001",
                numero=1,
                nombre="Sucursal Matriz",
                provincia="Pichincha",
                novitec_sucursal="Quito",
                activa=True,
                created_at=datetime(2026, 6, 5, 14, 30, 0),
            )
        ]


class FakeCrmStagingRepository:
    """Doblez de persistencia staging para validar el flujo CRM."""

    def __init__(self) -> None:
        """Inicializa contadores internos de carga."""

        self.prepared_schema = False
        self.prepared_extraction: str | None = None
        self.loaded_counts = {
            "clientes": 0,
            "empresas": 0,
            "sucursalescliente": 0,
        }

    def prepare_schema(self) -> None:
        """Marca el schema como preparado."""

        self.prepared_schema = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Registra la corrida preparada."""

        self.prepared_extraction = extraction_id

    def load_customers(self, extraction_id: str, records: list[Cliente]) -> None:
        """Cuenta clientes cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["clientes"] += len(records)

    def load_companies(self, extraction_id: str, records: list[Empresa]) -> None:
        """Cuenta empresas cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["empresas"] += len(records)

    def load_customer_branches(
        self,
        extraction_id: str,
        records: list[SucursalCliente],
    ) -> None:
        """Cuenta sucursales cliente cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["sucursalescliente"] += len(records)


def test_execute_carga_correctamente_el_dominio_crm_en_staging() -> None:
    """Valida la orquestacion completa de la carga de CRM a staging."""

    raw_reader = FakeCrmRawReader()
    staging_repository = FakeCrmStagingRepository()
    use_case = LoadCrmToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name="stg_crm",
    )

    summary = use_case.execute()

    assert staging_repository.prepared_schema is True
    assert staging_repository.prepared_extraction == "crm_20260605_140000"
    assert staging_repository.loaded_counts["clientes"] == 1
    assert staging_repository.loaded_counts["empresas"] == 1
    assert staging_repository.loaded_counts["sucursalescliente"] == 1
    assert summary.schema_name == "stg_crm"
    assert summary.clientes == 1
    assert summary.empresas == 1
    assert summary.sucursalescliente == 1
