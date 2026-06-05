"""Pruebas del caso de uso de carga tecnica a staging."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from novitec_dwh.contexts.technical.application.use_cases.load_technical_to_staging import (
    LoadTechnicalToStagingUseCase,
)
from novitec_dwh.contexts.technical.domain.entities import (
    CredencialEquipoMetadata,
    EquipoSerie,
    EquipoTecnico,
    InformeFotoMetadata,
    InformeTecnico,
    Marca,
    TipoDispositivo,
    TipoServicio,
)


class FakeTechnicalRawReader:
    """Doblez de lectura raw para validar la orquestacion tecnica a staging."""

    def __init__(self) -> None:
        """Inicializa el estado simulado de la corrida."""

        self._prepared = False

    @property
    def extraction_id(self) -> str:
        """Expone el identificador simulado de la corrida."""

        return "technical_20260605_090000"

    @property
    def run_directory(self) -> Path:
        """Expone una ruta raw simulada."""

        return Path("data/raw/technical/technical_20260605_090000")

    def prepare(self) -> None:
        """Marca la corrida como preparada."""

        self._prepared = True

    def read_reports(self) -> Iterator[list[InformeTecnico]]:
        """Entrega un lote simulado de informes tecnicos."""

        assert self._prepared is True
        yield [
            InformeTecnico(
                id=1,
                orden_id=100,
                tecnico_id=5,
                antecedentes="Antecedente",
                proceso="Proceso",
                conclusion="Conclusion",
                recomendaciones="Recomendacion",
                estado_equipo="Operativo",
                fecha_informe=date(2026, 6, 5),
                fecha_creacion=datetime(2026, 6, 5, 9, 0, 0),
                presupuesto_json='{"prueba": true}',
            )
        ]

    def read_report_photo_metadata(self) -> Iterator[list[InformeFotoMetadata]]:
        """Entrega un lote simulado de fotos de informes."""

        assert self._prepared is True
        yield [
            InformeFotoMetadata(
                id=1,
                informe_id=1,
                caption="Foto",
                nombre_archivo="foto.jpg",
                tipo_mime="image/jpeg",
                orden_foto=1,
                tiene_foto=True,
            )
        ]

    def read_equipment(self) -> Iterator[list[EquipoTecnico]]:
        """Entrega un lote simulado de equipos."""

        assert self._prepared is True
        yield [
            EquipoTecnico(
                id=1,
                tipo="Laptop",
                tipo_servicio_id=2,
                tipo_servicio_texto="Revision",
                marca="Dell",
                modelo="Latitude",
                serie="ABC123",
                contrasena_equipo="1234",
                falla="No enciende",
                observacion="Sin observacion",
                fecha_facturacion=date(2026, 6, 1),
                producto_inventario_codigo="INV-001",
            )
        ]

    def read_equipment_series(self) -> Iterator[list[EquipoSerie]]:
        """Entrega un lote simulado de series de equipos."""

        assert self._prepared is True
        yield [
            EquipoSerie(
                id=1,
                equipo_id=1,
                serie="ABC123",
                orden=1,
                created_at=datetime(2026, 6, 5, 8, 0, 0),
            )
        ]

    def read_device_types(self) -> Iterator[list[TipoDispositivo]]:
        """Entrega un lote simulado de tipos de dispositivo."""

        assert self._prepared is True
        yield [TipoDispositivo(id=1, codigo="LAP", nombre="Laptop")]

    def read_service_types(self) -> Iterator[list[TipoServicio]]:
        """Entrega un lote simulado de tipos de servicio."""

        assert self._prepared is True
        yield [
            TipoServicio(
                id=2,
                nombre="Revision",
                descripcion="Revision general",
                precio=Decimal("25.00"),
                activo=True,
                created_at=datetime(2026, 6, 5, 7, 0, 0),
            )
        ]

    def read_brands(self) -> Iterator[list[Marca]]:
        """Entrega un lote simulado de marcas."""

        assert self._prepared is True
        yield [Marca(id=1, nombre="Dell")]

    def read_equipment_credentials_metadata(
        self,
    ) -> Iterator[list[CredencialEquipoMetadata]]:
        """Entrega un lote simulado de credenciales sin secreto."""

        assert self._prepared is True
        yield [CredencialEquipoMetadata(id=1, equipo_id=1, usuario="admin", es_patron=False)]


class FakeTechnicalStagingRepository:
    """Doblez de persistencia staging para validar el flujo tecnico."""

    def __init__(self) -> None:
        """Inicializa contadores internos de carga."""

        self.prepared_schema = False
        self.prepared_extraction: str | None = None
        self.loaded_counts = {
            "informes": 0,
            "informefotos": 0,
            "equipos": 0,
            "equiposseries": 0,
            "tiposdispositivo": 0,
            "tiposservicio": 0,
            "marcas": 0,
            "credencialesequipo": 0,
        }

    def prepare_schema(self) -> None:
        """Marca el schema como preparado."""

        self.prepared_schema = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Registra la corrida preparada."""

        self.prepared_extraction = extraction_id

    def load_reports(self, extraction_id: str, records: list[InformeTecnico]) -> None:
        """Cuenta informes tecnicos cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["informes"] += len(records)

    def load_report_photo_metadata(
        self,
        extraction_id: str,
        records: list[InformeFotoMetadata],
    ) -> None:
        """Cuenta fotos de informes cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["informefotos"] += len(records)

    def load_equipment(self, extraction_id: str, records: list[EquipoTecnico]) -> None:
        """Cuenta equipos cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["equipos"] += len(records)

    def load_equipment_series(self, extraction_id: str, records: list[EquipoSerie]) -> None:
        """Cuenta series de equipos cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["equiposseries"] += len(records)

    def load_device_types(self, extraction_id: str, records: list[TipoDispositivo]) -> None:
        """Cuenta tipos de dispositivo cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["tiposdispositivo"] += len(records)

    def load_service_types(self, extraction_id: str, records: list[TipoServicio]) -> None:
        """Cuenta tipos de servicio cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["tiposservicio"] += len(records)

    def load_brands(self, extraction_id: str, records: list[Marca]) -> None:
        """Cuenta marcas cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["marcas"] += len(records)

    def load_equipment_credentials_metadata(
        self,
        extraction_id: str,
        records: list[CredencialEquipoMetadata],
    ) -> None:
        """Cuenta credenciales de equipo cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["credencialesequipo"] += len(records)


def test_execute_carga_correctamente_el_dominio_tecnico_en_staging() -> None:
    """Valida la orquestacion completa de la carga tecnica a staging."""

    raw_reader = FakeTechnicalRawReader()
    staging_repository = FakeTechnicalStagingRepository()
    use_case = LoadTechnicalToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name="stg_technical",
    )

    summary = use_case.execute()

    assert staging_repository.prepared_schema is True
    assert staging_repository.prepared_extraction == "technical_20260605_090000"
    assert staging_repository.loaded_counts["informes"] == 1
    assert staging_repository.loaded_counts["informefotos"] == 1
    assert staging_repository.loaded_counts["equipos"] == 1
    assert staging_repository.loaded_counts["equiposseries"] == 1
    assert staging_repository.loaded_counts["tiposdispositivo"] == 1
    assert staging_repository.loaded_counts["tiposservicio"] == 1
    assert staging_repository.loaded_counts["marcas"] == 1
    assert staging_repository.loaded_counts["credencialesequipo"] == 1
    assert summary.schema_name == "stg_technical"
    assert summary.informes == 1
    assert summary.informefotos == 1
    assert summary.equipos == 1
    assert summary.equiposseries == 1
    assert summary.tiposdispositivo == 1
    assert summary.tiposservicio == 1
    assert summary.marcas == 1
    assert summary.credencialesequipo == 1
