"""Pruebas del caso de uso de carga de garantias a staging."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from novitec_dwh.contexts.warranty.application.use_cases.load_warranty_to_staging import (
    LoadWarrantyToStagingUseCase,
)
from novitec_dwh.contexts.warranty.domain.entities import (
    CentroAutorizadoServicio,
    OrdenGarantiaEmpresa,
    OrdenGarantiaPersonal,
    UsuarioCasAsignacion,
)


class FakeWarrantyRawReader:
    """Doblez de lectura raw para validar la orquestacion de garantias a staging."""

    def __init__(self) -> None:
        """Inicializa el estado simulado de la corrida."""

        self._prepared = False

    @property
    def extraction_id(self) -> str:
        """Expone el identificador simulado de la corrida."""

        return "warranty_20260608_120000"

    @property
    def run_directory(self) -> Path:
        """Expone una ruta raw simulada."""

        return Path("data/raw/warranty/warranty_20260608_120000")

    def prepare(self) -> None:
        """Marca la corrida como preparada."""

        self._prepared = True

    def read_service_centers(self) -> Iterator[list[CentroAutorizadoServicio]]:
        """Entrega un lote simulado de CAS."""

        assert self._prepared is True
        yield [
            CentroAutorizadoServicio(
                id=1,
                nombre="CAS Demo",
                prefijo="CAS",
                marca="HP",
                telefono="022000000",
                correo="cas@demo.com",
                direccion="Av. Central",
                ciudad="Quito",
                contacto="Soporte",
                notas="Centro de prueba",
                activo=True,
                creado_en=datetime(2026, 6, 8, 8, 0, 0),
                actualizado_en=datetime(2026, 6, 8, 9, 0, 0),
            )
        ]

    def read_user_assignments(self) -> Iterator[list[UsuarioCasAsignacion]]:
        """Entrega un lote simulado de asignaciones usuario CAS."""

        assert self._prepared is True
        yield [
            UsuarioCasAsignacion(
                id=1,
                usuario_id=7,
                usuario_login="1726664749",
                usuario_nombre="Tecnico Master",
                cas_id=1,
            )
        ]

    def read_personal_warranty_orders(self) -> Iterator[list[OrdenGarantiaPersonal]]:
        """Entrega un lote simulado de ordenes personales con garantia."""

        assert self._prepared is True
        yield [
            OrdenGarantiaPersonal(
                id=10,
                nro_orden="ORD-001",
                cliente_id=1,
                equipo_id=5,
                tecnico_id=7,
                sucursal_id=2,
                fecha_de_ingreso=datetime(2026, 6, 8, 10, 0, 0),
                estado_orden="Pendiente",
                estado_garantia="Enviado",
                garantia_tipo="externa",
                garantia_cas="CAS Demo",
                cas_id=1,
                cas_fecha_envio=date(2026, 6, 9),
                cas_fecha_retorno=None,
                cas_numero_caso="CAS-100",
                fecha_prometido=date(2026, 6, 15),
                fecha_entrega=None,
                fecha_finalizacion=None,
            )
        ]

    def read_company_warranty_orders(self) -> Iterator[list[OrdenGarantiaEmpresa]]:
        """Entrega un lote simulado de ordenes empresariales con CAS."""

        assert self._prepared is True
        yield [
            OrdenGarantiaEmpresa(
                id=20,
                nro_orden="EMP-001",
                empresa_id=3,
                equipo_id=5,
                tecnico_id=7,
                sucursal_id=2,
                cas_id=1,
                fecha_ingreso=datetime(2026, 6, 8, 11, 0, 0),
                fecha_prometido=date(2026, 6, 16),
                estado="Abierta",
                valor_hora=Decimal("25.00"),
                horas_trabajadas=Decimal("2.50"),
                nro_ticket="TK-001",
            )
        ]


class FakeWarrantyStagingRepository:
    """Doblez de persistencia staging para validar el flujo de garantias."""

    def __init__(self) -> None:
        """Inicializa contadores internos de carga."""

        self.prepared_schema = False
        self.prepared_extraction: str | None = None
        self.loaded_counts = {
            "cas": 0,
            "usuariocas": 0,
            "ordenes_garantia": 0,
            "ordenesempresas_garantia": 0,
        }

    def prepare_schema(self) -> None:
        """Marca el schema como preparado."""

        self.prepared_schema = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Registra la corrida preparada."""

        self.prepared_extraction = extraction_id

    def load_service_centers(
        self,
        extraction_id: str,
        records: list[CentroAutorizadoServicio],
    ) -> None:
        """Cuenta CAS cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["cas"] += len(records)

    def load_user_assignments(
        self,
        extraction_id: str,
        records: list[UsuarioCasAsignacion],
    ) -> None:
        """Cuenta asignaciones usuario CAS cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["usuariocas"] += len(records)

    def load_personal_warranty_orders(
        self,
        extraction_id: str,
        records: list[OrdenGarantiaPersonal],
    ) -> None:
        """Cuenta ordenes personales con garantia cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["ordenes_garantia"] += len(records)

    def load_company_warranty_orders(
        self,
        extraction_id: str,
        records: list[OrdenGarantiaEmpresa],
    ) -> None:
        """Cuenta ordenes empresariales con CAS cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["ordenesempresas_garantia"] += len(records)


def test_execute_carga_correctamente_el_dominio_de_garantias_en_staging() -> None:
    """Valida la orquestacion completa de la carga de garantias a staging."""

    raw_reader = FakeWarrantyRawReader()
    staging_repository = FakeWarrantyStagingRepository()
    use_case = LoadWarrantyToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name="stg_warranty",
    )

    summary = use_case.execute()

    assert staging_repository.prepared_schema is True
    assert staging_repository.prepared_extraction == "warranty_20260608_120000"
    assert staging_repository.loaded_counts["cas"] == 1
    assert staging_repository.loaded_counts["usuariocas"] == 1
    assert staging_repository.loaded_counts["ordenes_garantia"] == 1
    assert staging_repository.loaded_counts["ordenesempresas_garantia"] == 1
    assert summary.schema_name == "stg_warranty"
    assert summary.cas == 1
    assert summary.usuariocas == 1
    assert summary.ordenes_garantia == 1
    assert summary.ordenesempresas_garantia == 1
