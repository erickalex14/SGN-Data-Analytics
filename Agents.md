# Contexto Integral del Proyecto: Data Warehouse y Pipeline ETL (Soporte Técnico)

## 1. Alcance y Objetivo
Actúa como un Arquitecto de Datos y Desarrollador Backend Senior.
El objetivo es diseñar e implementar un pipeline ETL exhaustivo y una API REST para procesar la totalidad de los datos de un sistema de gestión de servicio técnico. 
- **Origen de datos:** MySQL (Base de Datos Transaccional), tienes acceso a la estructura en la raiz de esta carpeta en el archivo estructura_bd.sql.
- **Destino de datos (Data Warehouse):** PostgreSQL (Modelo de Constelación de Hechos).
- **Procesamiento y API:** Python (Polars/Pandas + FastAPI).
- **Consumo final:** Dashboards empresariales multiplataforma en Power BI.

## 2. Reglas Estrictas de Desarrollo
- Todos los comentarios en el código deben estar en español.
- Debe estar todo el codigo comentado profesionalmente, explicando la lógica de cada sección y función.
- Todos los mensajes de log deben estar en español, ser descriptivos y estrictamente profesionales.
- Está terminantemente prohibido el uso de emojis en el código, respuestas, logs o documentación.
- El código debe estar optimizado para manejar grandes volúmenes de datos sin saturar la memoria RAM del servidor.
- La tabla `migrations` debe ser ignorada en los procesos de extracción, ya que es exclusiva del framework interno.

## 3. Diccionario de Datos Completo (Agrupado por Dominio Analítico)

Para el diseño del Data Warehouse, se debe extraer y relacionar la información según los siguientes dominios:

### 3.1. Dominio Operativo y Transaccional (Hechos Principales)
Contiene el flujo central del servicio técnico, desde la recepción hasta la entrega.
- `vista_ordenes`: Vista unificada de órdenes personales y empresariales. Principal fuente de datos para métricas de SLA, volumen y estado general.
- `ordenes`: Detalle transaccional de órdenes de clientes finales (incluye garantías, datos del equipo y fechas precisas).
- `ordenesempresas`: Detalle transaccional de soporte B2B (incluye `horas_trabajadas`, `valor_hora`, `nro_ticket`).
- `preordenes`: Registro de solicitudes previas a la formalización de la orden (incluye fotografías, sucursal, estado de atención).
- `orden_empresa_tecnicos`: Relación de múltiples técnicos asignados a una misma orden empresarial.

### 3.2. Dominio Financiero y Notas de Crédito (Económico)
Rastrea ingresos, tarifas estandarizadas y devoluciones o compensaciones.
- `solicitudesnc`: Solicitudes de Notas de Crédito. Clave para análisis de devoluciones (`nro_solicitud`, `orden_id`, `estado`, `motivo_rechazo`).
- `notificaciones`: Trazabilidad del ciclo de vida de las notas de crédito y aprobaciones (`tipo`: `nc_solicitud`, `nc_aprobada`, `nc_rechazada`).
- `preciosorden`: Ingresos directos facturados por cada orden, detallando el servicio prestado.
- `preciosestandar`: Catálogo maestro de servicios tarifados.

### 3.3. Dominio Técnico e Informes (Calidad y Diagnóstico)
Mide la calidad de la reparación y el estado de los equipos intervenidos.
- `informes`: Dictamen técnico detallado (`antecedentes`, `proceso`, `conclusion`, `recomendaciones`, `estado_equipo`).
- `informefotos`: Evidencia visual adjunta a los informes (metadatos para auditoría).
- `equipos`: Registro maestro de los dispositivos atendidos (marca, modelo, serie, falla reportada).
- `equiposseries`: Trazabilidad de múltiples números de serie por equipo.
- `tiposdispositivo`, `tiposservicio`, `marcas`: Tablas dimensionales para categorización de hardware y servicios.
- `credencialesequipo`: Registro de contraseñas de equipos (Extraer solo para métricas de "equipos con acceso proporcionado", omitiendo el campo `contrasena` por seguridad analítica).

### 3.4. Dominio de Inventario y Cadena de Suministro (Materiales)
Controla el flujo de repuestos, costos y necesidades de abastecimiento.
- `repuestos`: Catálogo analítico de piezas (`costo`, `stock`, `bodega`).
- `productosinventario`: Clasificación general de inventario por códigos y tipos de dispositivo.
- `orden_repuestos`: Piezas efectivamente instaladas en una orden y el técnico responsable.
- `solicitudesrepuesto`: Requerimientos de piezas no disponibles en bodega (`link_compra`, `estado`, `aprobado_por`).
- `listascompra`: Agrupación de repuestos solicitados para compras en bloque.

### 3.5. Dominio CRM (Clientes y B2B)
Información demográfica y de contacto.
- `clientes`: Datos de clientes finales (B2C).
- `empresas`: Datos fiscales y de contacto corporativo (B2B).
- `sucursalescliente`: Sedes físicas de las empresas cliente, vinculadas a su cobertura geográfica.

### 3.6. Dominio de Garantías (Centros Autorizados - CAS)
Rastreo de equipos tercerizados a proveedores oficiales.
- `cas`: Catálogo de Centros Autorizados de Servicio externos.
- `usuariocas`: Relación de qué usuarios internos tienen acceso o gestionan garantías con qué CAS específicos.

### 3.7. Dominio Organizacional y Seguridad (Recursos Humanos)
Estructura interna de la empresa y permisos.
- `sucursales`: Sedes físicas propias donde operan los técnicos.
- `usuarios`: Personal de la empresa (técnicos, administradores).
- `usuariosucursales`: Asignación de personal a sedes específicas.
- Tablas de Auditoría de Accesos: `roles`, `gruposacceso`, `permisosgrupo`, `permisosusuario` (Para medir carga administrativa y niveles de acceso).

## 4. Instrucciones para la Ejecución del Pipeline
1. **Fase de Extracción:** Desarrollar scripts modulares en Python que se conecten a MySQL, paginen las tablas pesadas y extraigan la información completa.
2. **Fase de Transformación:** - Limpiar datos y unificar fechas.
   - Procesar JSON anidados (ej. `presupuesto_json` en `informes`).
   - Construir modelos de Hechos (Ventas, Consumo de Repuestos, SLAs, Devoluciones) y Dimensiones (Tiempo, Clientes, Equipos, Técnicos).
3. **Fase de Carga:** Insertar la data transformada en PostgreSQL.
4. **Primer Paso Requerido:** Genera el script en Python para orquestar la conexión a las bases de datos y la extracción del Dominio Financiero (`solicitudesnc`, `preciosorden`, `notificaciones`), implementando un sistema de logging profesional.