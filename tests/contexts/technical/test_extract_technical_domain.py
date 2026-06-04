"""Pruebas del caso de uso de extraccion tecnica."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal

from novitec_dwh.contexts.technical.application.use_cases.extract_technical_domain import (
    ExtractTechnicalDomainUseCase,
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
from novitec_dwh.contexts.technical.infrastructure.filesystem_technical_extraction_sink import (
    FilesystemTechnicalExtractionSink,
)


class FakeTechnicalExtractionRepository:
    """Doblez de pruebas para validar el flujo del caso de uso tecnico."""

    def extract_reports(self, chunk_size: int) -> Iterator[list[InformeTecnico]]:
        """Devuelve un unico lote simulado de informes tecnicos."""

        _ = chunk_size
        yield [
            InformeTecnico(
                id=1,
                orden_id=10,
                tecnico_id=5,
                antecedentes="Equipo sin encender",
                proceso="Revision interna",
                conclusion="Falla de energia",
                recomendaciones="Cambiar adaptador",
                estado_equipo="Operativo",
                fecha_informe=date(2026, 6, 4),
                fecha_creacion=datetime(2026, 6, 4, 10, 0, 0),
                presupuesto_json='{"mano_obra": 25}',
            )
        ]

    def extract_report_photo_metadata(
        self,
        chunk_size: int,
    ) -> Iterator[list[InformeFotoMetadata]]:
        """Devuelve un unico lote simulado de metadatos de fotos."""

        _ = chunk_size
        yield [
            InformeFotoMetadata(
                id=1,
                informe_id=1,
                caption="Placa madre",
                nombre_archivo="placa.jpg",
                tipo_mime="image/jpeg",
                orden_foto=1,
                tiene_foto=True,
            )
        ]

    def extract_equipment(self, chunk_size: int) -> Iterator[list[EquipoTecnico]]:
        """Devuelve un unico lote simulado de equipos."""

        _ = chunk_size
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

    def extract_equipment_series(self, chunk_size: int) -> Iterator[list[EquipoSerie]]:
        """Devuelve un unico lote simulado de series de equipos."""

        _ = chunk_size
        yield [
            EquipoSerie(
                id=1,
                equipo_id=1,
                serie="ABC123",
                orden=1,
                created_at=datetime(2026, 6, 4, 8, 0, 0),
            )
        ]

    def extract_device_types(self, chunk_size: int) -> Iterator[list[TipoDispositivo]]:
        """Devuelve un unico lote simulado de tipos de dispositivo."""

        _ = chunk_size
        yield [TipoDispositivo(id=1, codigo="LAP", nombre="Laptop")]

    def extract_service_types(self, chunk_size: int) -> Iterator[list[TipoServicio]]:
        """Devuelve un unico lote simulado de tipos de servicio."""

        _ = chunk_size
        yield [
            TipoServicio(
                id=2,
                nombre="Revision",
                descripcion="Revision general",
                precio=Decimal("25.00"),
                activo=True,
                created_at=datetime(2026, 6, 4, 7, 0, 0),
            )
        ]

    def extract_brands(self, chunk_size: int) -> Iterator[list[Marca]]:
        """Devuelve un unico lote simulado de marcas."""

        _ = chunk_size
        yield [Marca(id=1, nombre="Dell")]

    def extract_equipment_credentials_metadata(
        self,
        chunk_size: int,
    ) -> Iterator[list[CredencialEquipoMetadata]]:
        """Devuelve un unico lote simulado de credenciales sin secreto."""

        _ = chunk_size
        yield [
            CredencialEquipoMetadata(
                id=1,
                equipo_id=1,
                usuario="admin",
                es_patron=False,
            )
        ]


def test_execute_resume_correctamente_los_registros(tmp_path) -> None:
    """Valida que el caso de uso tecnico acumule el volumen total por entidad."""

    repository = FakeTechnicalExtractionRepository()
    sink = FilesystemTechnicalExtractionSink(base_path=tmp_path / "raw")
    use_case = ExtractTechnicalDomainUseCase(repository=repository, sink=sink)

    summary = use_case.execute(chunk_size=100)

    assert summary.informes == 1
    assert summary.informes_chunks == 1
    assert summary.informefotos == 1
    assert summary.informefotos_chunks == 1
    assert summary.equipos == 1
    assert summary.equipos_chunks == 1
    assert summary.equiposseries == 1
    assert summary.equiposseries_chunks == 1
    assert summary.tiposdispositivo == 1
    assert summary.tiposdispositivo_chunks == 1
    assert summary.tiposservicio == 1
    assert summary.tiposservicio_chunks == 1
    assert summary.marcas == 1
    assert summary.marcas_chunks == 1
    assert summary.credencialesequipo == 1
    assert summary.credencialesequipo_chunks == 1
    assert summary.output_directory is not None
    assert summary.manifest_path is not None
    assert (tmp_path / "raw").exists()
