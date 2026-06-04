"""Pruebas del caso de uso de carga operativa a staging."""

from collections.abc import Iterator
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from novitec_dwh.contexts.operational.application.use_cases.load_operational_to_staging import (
    LoadOperationalToStagingUseCase,
)
from novitec_dwh.contexts.operational.domain.entities import (
    OrdenEmpresa,
    OrdenEmpresaTecnico,
    OrdenPersonal,
    PreOrden,
    VistaOrden,
)


class FakeOperationalRawReader:
    """Doblez de lectura raw para validar la orquestacion operativa a staging."""

    def __init__(self) -> None:
        """Inicializa el estado simulado de la corrida."""

        self._prepared = False

    @property
    def extraction_id(self) -> str:
        """Expone el identificador simulado de la corrida."""

        return "operational_20260604_150000"

    @property
    def run_directory(self) -> Path:
        """Expone una ruta raw simulada."""

        return Path("data/raw/operational/operational_20260604_150000")

    def prepare(self) -> None:
        """Marca la corrida como preparada."""

        self._prepared = True

    def read_order_view(self) -> Iterator[list[VistaOrden]]:
        """Entrega un lote simulado de vista de ordenes."""

        assert self._prepared is True
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

    def read_personal_orders(self) -> Iterator[list[OrdenPersonal]]:
        """Entrega un lote simulado de ordenes personales."""

        assert self._prepared is True
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

    def read_company_orders(self) -> Iterator[list[OrdenEmpresa]]:
        """Entrega un lote simulado de ordenes empresariales."""

        assert self._prepared is True
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

    def read_preorders(self) -> Iterator[list[PreOrden]]:
        """Entrega un lote simulado de preordenes."""

        assert self._prepared is True
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

    def read_company_order_technicians(self) -> Iterator[list[OrdenEmpresaTecnico]]:
        """Entrega un lote simulado de asignaciones tecnico-orden."""

        assert self._prepared is True
        yield [OrdenEmpresaTecnico(id=1, orden_empresa_id=2, tecnico_id=1)]


class FakeOperationalStagingRepository:
    """Doblez de persistencia staging para validar el flujo operativo."""

    def __init__(self) -> None:
        """Inicializa contadores internos de carga."""

        self.prepared_schema = False
        self.prepared_extraction: str | None = None
        self.loaded_counts = {
            "vista_ordenes": 0,
            "ordenes": 0,
            "ordenes_empresas": 0,
            "preordenes": 0,
            "orden_empresa_tecnicos": 0,
        }

    def prepare_schema(self) -> None:
        """Marca el schema como preparado."""

        self.prepared_schema = True

    def prepare_extraction(self, extraction_id: str) -> None:
        """Registra la corrida preparada."""

        self.prepared_extraction = extraction_id

    def load_order_view(self, extraction_id: str, records: list[VistaOrden]) -> None:
        """Cuenta registros de vista de ordenes cargados."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["vista_ordenes"] += len(records)

    def load_personal_orders(self, extraction_id: str, records: list[OrdenPersonal]) -> None:
        """Cuenta ordenes personales cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["ordenes"] += len(records)

    def load_company_orders(self, extraction_id: str, records: list[OrdenEmpresa]) -> None:
        """Cuenta ordenes empresariales cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["ordenes_empresas"] += len(records)

    def load_preorders(self, extraction_id: str, records: list[PreOrden]) -> None:
        """Cuenta preordenes cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["preordenes"] += len(records)

    def load_company_order_technicians(
        self,
        extraction_id: str,
        records: list[OrdenEmpresaTecnico],
    ) -> None:
        """Cuenta asignaciones tecnico-orden cargadas."""

        assert extraction_id == self.prepared_extraction
        self.loaded_counts["orden_empresa_tecnicos"] += len(records)


def test_execute_carga_correctamente_el_dominio_operativo_en_staging() -> None:
    """Valida la orquestacion completa de la carga operativa a staging."""

    raw_reader = FakeOperationalRawReader()
    staging_repository = FakeOperationalStagingRepository()
    use_case = LoadOperationalToStagingUseCase(
        raw_reader=raw_reader,
        staging_repository=staging_repository,
        schema_name="stg_operational",
    )

    summary = use_case.execute()

    assert staging_repository.prepared_schema is True
    assert staging_repository.prepared_extraction == "operational_20260604_150000"
    assert staging_repository.loaded_counts["vista_ordenes"] == 1
    assert staging_repository.loaded_counts["ordenes"] == 1
    assert staging_repository.loaded_counts["ordenes_empresas"] == 1
    assert staging_repository.loaded_counts["preordenes"] == 1
    assert staging_repository.loaded_counts["orden_empresa_tecnicos"] == 1
    assert summary.schema_name == "stg_operational"
    assert summary.vista_ordenes == 1
    assert summary.ordenes == 1
    assert summary.ordenes_empresas == 1
    assert summary.preordenes == 1
    assert summary.orden_empresa_tecnicos == 1
