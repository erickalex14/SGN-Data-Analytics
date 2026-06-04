"""Pruebas del caso de uso de extraccion operativa."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal

from novitec_dwh.contexts.operational.application.use_cases.extract_operational_domain import (
    ExtractOperationalDomainUseCase,
)
from novitec_dwh.contexts.operational.domain.entities import (
    OrdenEmpresa,
    OrdenEmpresaTecnico,
    OrdenPersonal,
    PreOrden,
    VistaOrden,
)
from novitec_dwh.contexts.operational.infrastructure.filesystem_operational_extraction_sink import (
    FilesystemOperationalExtractionSink,
)


class FakeOperationalExtractionRepository:
    """Doblez de pruebas para validar el flujo del caso de uso operativo."""

    def extract_order_view(self, chunk_size: int) -> Iterator[list[VistaOrden]]:
        """Devuelve un unico lote simulado de la vista operativa."""

        _ = chunk_size
        yield [
            VistaOrden(
                orden_id=1,
                nro_orden="ORD-001",
                tipo_orden="personal",
                estado_orden="Pendiente",
                estado_repuesto="No requerido",
                estado_garantia=None,
                motivo_ingreso="Servicio Tecnico",
                fecha_de_ingreso=datetime(2026, 6, 4, 10, 0, 0),
                fecha_prometido=date(2026, 6, 6),
                fecha_entrega=None,
                nro_factura="FAC-001",
                nro_factura_2=None,
                nro_sucursal_cliente=None,
                tecnico_id=1,
                sucursal_id=1,
                ingresado_por=1,
                cliente_id=1,
                empresa_id=None,
                equipo_id=1,
                cliente="Cliente Demo",
                nombres="Cliente",
                apellidos="Demo",
                identificacion="123",
                numero_contacto="099",
                correo="demo@test.com",
                direccion="Direccion",
                tipo="Laptop",
                marca="Dell",
                modelo="XPS",
                serie="ABC",
                falla="No enciende",
                observacion="Sin observacion",
                fecha_facturacion="2026-06-04",
                tecnico="Tecnico 1",
                sucursal="Quito",
                fecha_de_ingreso_fmt="04/06/2026 10:00",
                fecha_prometido_fmt="06/06/2026",
                fecha_entrega_fmt=None,
            )
        ]

    def extract_personal_orders(self, chunk_size: int) -> Iterator[list[OrdenPersonal]]:
        """Devuelve un unico lote simulado de ordenes personales."""

        _ = chunk_size
        yield [
            OrdenPersonal(
                id=1,
                nro_orden="ORD-001",
                nro_factura="FAC-001",
                nro_factura_2=None,
                motivo_ingreso="Servicio Tecnico",
                nro_sucursal_cliente=None,
                cliente_id=1,
                equipo_id=1,
                tecnico_id=1,
                sucursal_id=1,
                fecha_de_ingreso=datetime(2026, 6, 4, 10, 0, 0),
                estado_orden="Pendiente",
                estado_repuesto="No requerido",
                estado_garantia=None,
                garantia_tipo=None,
                garantia_cas=None,
                cas_id=None,
                cas_fecha_envio=None,
                cas_fecha_retorno=None,
                cas_numero_caso=None,
                ingresado_por=1,
                fecha_prometido=date(2026, 6, 6),
                modificado_por=None,
                fecha_modificacion=None,
                fecha_entrega=None,
                fecha_finalizacion=None,
                valor_estandar_id=None,
                repuesto_inventario_id=None,
                observacion="Obs",
                tipo_servicio_id=None,
                tipo_servicio_texto=None,
                fecha_facturacion=date(2026, 6, 4),
            )
        ]

    def extract_company_orders(self, chunk_size: int) -> Iterator[list[OrdenEmpresa]]:
        """Devuelve un unico lote simulado de ordenes empresariales."""

        _ = chunk_size
        yield [
            OrdenEmpresa(
                id=2,
                nro_orden="EMP-001",
                empresa_id=1,
                subtipo="Mesa de ayuda",
                nro_sucursal_cliente=None,
                equipo_id=1,
                tipo_servicio="Soporte",
                nro_ticket="TK-001",
                descripcion="Incidencia demo",
                tecnico_id=1,
                sucursal_id=1,
                cas_id=None,
                ingresado_por=1,
                fecha_prometido=date(2026, 6, 7),
                estado="Abierta",
                valor_hora=Decimal("12.00"),
                horas_trabajadas=Decimal("3.50"),
                fecha_ingreso=datetime(2026, 6, 4, 9, 0, 0),
            )
        ]

    def extract_preorders(self, chunk_size: int) -> Iterator[list[PreOrden]]:
        """Devuelve un unico lote simulado de preordenes."""

        _ = chunk_size
        yield [
            PreOrden(
                id=1,
                orden_id=None,
                fecha_registro=datetime(2026, 6, 4, 8, 0, 0),
                nro_preorden="PRE-001",
                sucursal_id=1,
                nombres="Ana",
                apellidos="Perez",
                identificacion="123",
                telefono="099",
                correo="ana@test.com",
                nro_factura=None,
                codigo_producto=None,
                desc_producto=None,
                marca_producto="Dell",
                tipo_producto="Laptop",
                detalle_equipo="Equipo demo",
                foto_1=None,
                foto_2=None,
                foto_3=None,
                foto_4=None,
                estado="pendiente",
                created_at=datetime(2026, 6, 4, 8, 0, 0),
                nro_sucursal_cliente=None,
                ciudad_procedencia="Quito",
                fecha_facturacion=None,
            )
        ]

    def extract_company_order_technicians(
        self,
        chunk_size: int,
    ) -> Iterator[list[OrdenEmpresaTecnico]]:
        """Devuelve un unico lote simulado de asignaciones tecnico-orden."""

        _ = chunk_size
        yield [OrdenEmpresaTecnico(id=1, orden_empresa_id=2, tecnico_id=1)]


def test_execute_resume_correctamente_los_registros(tmp_path) -> None:
    """Valida que el caso de uso acumule el volumen total por entidad."""

    repository = FakeOperationalExtractionRepository()
    sink = FilesystemOperationalExtractionSink(base_path=tmp_path / "raw")
    use_case = ExtractOperationalDomainUseCase(repository=repository, sink=sink)

    summary = use_case.execute(chunk_size=100)

    assert summary.vista_ordenes == 1
    assert summary.vista_ordenes_chunks == 1
    assert summary.ordenes == 1
    assert summary.ordenes_chunks == 1
    assert summary.ordenes_empresas == 1
    assert summary.ordenes_empresas_chunks == 1
    assert summary.preordenes == 1
    assert summary.preordenes_chunks == 1
    assert summary.orden_empresa_tecnicos == 1
    assert summary.orden_empresa_tecnicos_chunks == 1
    assert summary.output_directory is not None
    assert summary.manifest_path is not None
    assert (tmp_path / "raw").exists()
