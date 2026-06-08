# Plan de Accion - Portal Ejecutivo Web

## 1. Objetivo

Construir un portal web ejecutivo, interno y multiplataforma para gerencia, que consuma la API `FastAPI` actual y permita:

- consultar indicadores por dominio
- navegar tablas analiticas con filtros avanzados
- visualizar graficos de nivel gerencial
- exportar reportes en `Excel`, `CSV` y `PDF`
- reemplazar gradualmente el consumo manual en Power BI para uso diario

## 2. Decision de arquitectura

Se usara un **frontend separado** del backend actual.

Arquitectura objetivo:

```text
Frontend React
    |
    v
FastAPI Portal / API Analitica
    |
    v
PostgreSQL DWH + schemas semanticos
```

Decision principal:

- `Power BI` queda como canal opcional de analisis
- el portal web sera el canal principal de consumo gerencial
- el frontend **no** se conectara directo a PostgreSQL

## 3. Stack recomendado

### 3.1. Frontend

- `React`
- `TypeScript`
- `Vite`
- `Tailwind CSS`
- `shadcn/ui`
- `Aceternity UI`
- `TanStack Query`
- `TanStack Table`
- `Apache ECharts`
- `React Router`
- `Zod`

### 3.2. Backend de soporte al portal

Sobre el backend actual:

- `FastAPI`
- `Pydantic`
- `openpyxl` para `Excel`
- generacion de `CSV`
- `WeasyPrint` para `PDF`

## 4. Rol de Aceternity UI

`Aceternity UI` si entra, pero con criterio.

Uso recomendado:

- encabezados ejecutivos
- tarjetas KPI premium
- bloques de filtros destacados
- contenedores de dashboards
- pantallas vacias o estados de carga elegantes

Uso no recomendado:

- tablas densas
- formularios pesados
- vistas con demasiada animacion
- componentes criticos donde la sobriedad sea mas importante que el impacto visual

Regla:

- `shadcn/ui` sera la base funcional enterprise
- `Aceternity UI` sera la capa visual premium

## 5. Estructura propuesta del frontend

```text
frontend/
`-- novitec-portal/
    |-- public/
    |-- src/
    |   |-- app/
    |   |   |-- providers/
    |   |   |-- router/
    |   |   `-- layouts/
    |   |-- features/
    |   |   |-- executive/
    |   |   |-- operational/
    |   |   |-- financial/
    |   |   |-- technical/
    |   |   |-- inventory/
    |   |   |-- crm/
    |   |   |-- warranty/
    |   |   `-- organizational/
    |   |-- shared/
    |   |   |-- ui/
    |   |   |-- charts/
    |   |   |-- tables/
    |   |   |-- filters/
    |   |   |-- export/
    |   |   `-- utils/
    |   |-- services/
    |   |-- hooks/
    |   |-- types/
    |   `-- main.tsx
    |-- package.json
    |-- tsconfig.json
    `-- vite.config.ts
```

## 6. Paginas del portal

### 6.1. MVP inicial

- `Login`
- `Resumen Ejecutivo`
- `Operaciones`
- `Financiero`
- `Tecnico`
- `Inventario`
- `CRM`
- `Garantias`
- `Organizacional`
- `Centro de Exportes`

### 6.2. Segunda etapa

- `Auditoria de descargas`
- `Comparativos por periodos`
- `Reportes programados`
- `Modo impresion`

## 7. Estrategia de datos

### 7.1. Lo que ya sirve

La API actual ya expone:

- endpoints por dominio
- endpoint ejecutivo consolidado
- filtros
- paginacion
- auth
- manejo uniforme de errores

### 7.2. Lo que conviene agregar para el portal

Crear endpoints mas orientados a consumo visual:

- `/api/v1/portal/dashboard/executive`
- `/api/v1/portal/financial/overview`
- `/api/v1/portal/operational/overview`
- `/api/v1/portal/technical/overview`
- `/api/v1/portal/inventory/overview`
- `/api/v1/portal/crm/overview`
- `/api/v1/portal/warranty/overview`
- `/api/v1/portal/organizational/overview`
- `/api/v1/portal/exports/...`

Objetivo:

- menos roundtrips desde el frontend
- respuestas mas estables para visualizacion
- menos logica de agregacion en React

## 8. Seguridad recomendada

Para el portal no conviene dejar token fijo manual en navegador.

Objetivo:

- login simple interno
- sesion por cookie segura
- expiracion de sesion
- logout
- trazabilidad de accesos y descargas

## 9. Exportes enterprise

### 9.1. Excel

Debe soportar:

- hojas multiples
- encabezados corporativos
- filtros aplicados en encabezado
- formatos de moneda, fecha y porcentaje

### 9.2. PDF

Debe soportar:

- portada simple
- resumen de filtros
- bloques KPI
- tablas resumidas
- graficos renderizados o capturados

### 9.3. CSV

Debe soportar:

- exportacion rapida de tablas
- codificacion UTF-8

## 10. Lineamientos visuales

Objetivo visual:

- sobrio
- ejecutivo
- denso pero limpio
- premium sin parecer landing page

Reglas:

- fondo claro o neutro
- color de acento corporativo controlado
- cards discretas
- tipografia compacta
- graficos legibles en escritorio y laptop
- filtros globales visibles
- sin ornamentacion excesiva

## 11. Fases de implementacion

### Fase 0 - Definicion

- cerrar stack final
- definir branding minimo
- definir estrategia de autenticacion
- definir endpoints portal necesarios

### Fase 1 - Base tecnica

- crear proyecto `frontend/novitec-portal`
- configurar `React + TypeScript + Vite`
- integrar `Tailwind`, `shadcn/ui` y `Aceternity UI`
- configurar `React Router`
- configurar `TanStack Query`
- configurar layout principal

### Fase 2 - Shell del portal

- login
- sidebar
- header
- selector global de fechas
- estados de carga
- manejo global de errores

### Fase 3 - Resumen Ejecutivo

- KPIs globales
- graficos principales
- filtros globales
- exporte ejecutivo

### Fase 4 - Dominios

- operaciones
- financiero
- tecnico
- inventario
- crm
- garantias
- organizacional

### Fase 5 - Exportes

- exportes a Excel
- exportes a CSV
- reportes PDF
- impresion limpia

### Fase 6 - Endurecimiento

- permisos
- auditoria
- rendimiento
- cache
- pruebas visuales

## 12. Riesgos y decisiones a vigilar

- no abusar de `Aceternity UI` en pantallas densas
- no dejar toda la agregacion al frontend
- no multiplicar endpoints casi iguales sin una capa `portal`
- no usar `DirectQuery` a la base desde navegador
- no mezclar dashboard ejecutivo con vistas operativas demasiado detalladas

## 13. Recomendacion final

La ruta mas sana es esta:

1. crear el frontend separado
2. usar `shadcn/ui` como base
3. usar `Aceternity UI` como capa visual premium controlada
4. mantener `FastAPI` como backend de negocio y exportes
5. construir primero `Resumen Ejecutivo`
6. luego abrir paginas por dominio

## 14. Siguiente paso inmediato

El siguiente paso recomendado ya no es Power BI.

El siguiente paso es:

1. scaffold del frontend `React + Vite + TypeScript`
2. instalacion de `Tailwind`, `shadcn/ui` y `Aceternity UI`
3. layout base del portal
4. primera pagina `Resumen Ejecutivo` consumiendo la API actual
