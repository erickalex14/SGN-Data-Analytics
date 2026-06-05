# Referencia API Novitec DWH

## Seguridad

Cuando `API_AUTH_ENABLED=true`, todos los endpoints excepto `health` requieren:

```http
Authorization: Bearer <token>
```

## Formato de error

```json
{
  "error": {
    "code": "validation_error",
    "message": "La solicitud contiene parametros invalidos.",
    "request_id": "uuid",
    "path": "/api/v1/financial/credit-note-requests",
    "timestamp": "2026-06-04T16:00:00",
    "details": []
  }
}
```

## Formato de paginacion

```json
{
  "meta": {
    "total": 226,
    "limit": 50,
    "offset": 0,
    "count": 50,
    "page": 1,
    "total_pages": 5,
    "has_next": true,
    "has_previous": false
  },
  "items": []
}
```

## Endpoint ejecutivo

### `GET /api/v1/dashboard/executive`

Entrega un resumen consolidado de gerencia con:

- bloque `financial`
- bloque `operational`
- bloque `technical`
- bloque `inventory`
- bloque `kpis`
- bloque `filters`

Filtros:

- `date_from`
- `date_to`
- `technician_name`
- `branch_name`
- `admin_name`
- `status_name`
- `order_type`

Ejemplo:

```http
GET /api/v1/dashboard/executive?date_from=2026-06-01&date_to=2026-06-30&branch_name=Quito
```

KPIs incluidos actualmente:

- `tasa_aprobacion_nc`
- `tasa_notificaciones_leidas`
- `tasa_ordenes_entregadas`
- `tasa_ordenes_abiertas`
- `tasa_ordenes_garantia`
- `tasa_informes_equipo_operativo`
- `tasa_informes_con_presupuesto`
- `tasa_equipos_con_contrasena`
- `tasa_repuestos_con_stock`
- `tasa_solicitudes_repuesto_aprobadas`
- `tasa_solicitudes_repuesto_pendientes`

## Endpoints financieros

### `GET /api/v1/financial/summary`

Filtros:

- `order_id`
- `order_number`
- `technician_name`
- `admin_name`
- `status_name`
- `date_from`
- `date_to`

### `GET /api/v1/financial/credit-note-requests`

Filtros:

- `limit`
- `offset`
- `search`
- `request_number`
- `order_id`
- `order_number`
- `status_name`
- `technician_name`
- `admin_name`
- `subject_name`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/financial/order-prices`

Filtros:

- `limit`
- `offset`
- `order_id`
- `service_name`
- `order_number`
- `standard_service_name`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/financial/notifications`

Filtros:

- `limit`
- `offset`
- `order_id`
- `order_number`
- `nc_id`
- `notification_type`
- `is_read`
- `technician_name`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

## Endpoints operativos

### `GET /api/v1/operational/summary`

Filtros:

- `order_type`
- `technician_name`
- `branch_name`
- `status_name`
- `date_from`
- `date_to`

### `GET /api/v1/operational/orders`

Filtros:

- `limit`
- `offset`
- `search`
- `order_type`
- `status_name`
- `technician_name`
- `branch_name`
- `customer_type`
- `is_open`
- `is_warranty`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/operational/preorders`

Filtros:

- `limit`
- `offset`
- `preorder_status`
- `branch_name`
- `has_invoice`
- `has_photos`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/operational/company-order-assignments`

Filtros:

- `limit`
- `offset`
- `source_order_id`
- `technician_name`
- `sort_by`
- `sort_dir`

## Endpoints tecnicos

### `GET /api/v1/technical/summary`

Filtros:

- `technician_name`
- `equipment_status`
- `service_name`
- `brand_name`
- `date_from`
- `date_to`

### `GET /api/v1/technical/reports`

Filtros:

- `limit`
- `offset`
- `order_id`
- `technician_name`
- `equipment_status`
- `has_budget_json`
- `is_equipment_operational`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/technical/report-photos`

Filtros:

- `limit`
- `offset`
- `report_source_id`
- `technician_name`
- `has_binary_evidence`
- `mime_type`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/technical/equipment`

Filtros:

- `limit`
- `offset`
- `service_name`
- `brand_name`
- `device_type_name`
- `inventory_product_code`
- `has_password_provided`
- `has_failure_description`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/technical/equipment-access`

Filtros:

- `limit`
- `offset`
- `equipment_source_id`
- `has_user_name`
- `is_pattern`
- `sort_by`
- `sort_dir`

## Endpoints de inventario

### `GET /api/v1/inventory/summary`

Filtros:

- `technician_name`
- `spare_part_code`
- `request_status`
- `warehouse_number`
- `date_from`
- `date_to`

### `GET /api/v1/inventory/spare-parts`

Filtros:

- `limit`
- `offset`
- `spare_part_code`
- `part_number`
- `spare_part_name`
- `warehouse_number`
- `has_stock`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/inventory/order-spare-parts`

Filtros:

- `limit`
- `offset`
- `order_id`
- `spare_part_code`
- `spare_part_name`
- `installer_user_id`
- `has_installer_user`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/inventory/spare-part-requests`

Filtros:

- `limit`
- `offset`
- `request_number`
- `order_id`
- `technician_name`
- `spare_part_code`
- `request_status`
- `approved_by`
- `has_purchase_link`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/inventory/purchase-lists`

Filtros:

- `limit`
- `offset`
- `list_number`
- `creator_user_id`
- `list_status`
- `has_observation`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`
