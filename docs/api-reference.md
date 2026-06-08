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

- bloque `crm`
- bloque `financial`
- bloque `operational`
- bloque `technical`
- bloque `inventory`
- bloque `warranty`
- bloque `organizational`
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
- `tasa_clientes_con_correo`
- `tasa_empresas_con_correo`
- `tasa_sucursalescliente_activas`
- `tasa_cas_activos`
- `tasa_ordenes_personales_garantia_con_caso`
- `tasa_ordenes_empresariales_garantia_con_ticket`
- `tasa_usuarios_activos`
- `tasa_usuarios_con_acceso_nc`
- `tasa_permisos_grupo_permitidos`
- `tasa_permisos_usuario_permitidos`

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

## Endpoints CRM

### `GET /api/v1/crm/summary`

Filtros:

- `search`
- `province`
- `is_active`
- `date_from`
- `date_to`

### `GET /api/v1/crm/customers`

Filtros:

- `limit`
- `offset`
- `search`
- `identification`
- `has_email`
- `has_address`
- `sort_by`
- `sort_dir`

### `GET /api/v1/crm/companies`

Filtros:

- `limit`
- `offset`
- `search`
- `ruc`
- `has_email`
- `has_phone`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/crm/customer-branches`

Filtros:

- `limit`
- `offset`
- `branch_code`
- `branch_name`
- `province`
- `novitec_branch_name`
- `is_active`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

## Endpoints de garantias

### `GET /api/v1/warranty/summary`

Filtros:

- `service_center_name`
- `technician_id`
- `user_id`
- `warranty_status`
- `warranty_type`
- `order_status`
- `date_from`
- `date_to`

### `GET /api/v1/warranty/service-centers`

Filtros:

- `limit`
- `offset`
- `service_center_name`
- `prefix_code`
- `brand_name`
- `city_name`
- `is_active`
- `sort_by`
- `sort_dir`

### `GET /api/v1/warranty/personal-orders`

Filtros:

- `limit`
- `offset`
- `order_number`
- `service_center_name`
- `technician_id`
- `warranty_status`
- `warranty_type`
- `order_status`
- `has_case_number`
- `is_closed`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/warranty/company-orders`

Filtros:

- `limit`
- `offset`
- `order_number`
- `service_center_name`
- `technician_id`
- `company_id`
- `order_status`
- `has_ticket_number`
- `has_worked_hours`
- `date_from`
- `date_to`
- `sort_by`
- `sort_dir`

### `GET /api/v1/warranty/user-assignments`

Filtros:

- `limit`
- `offset`
- `user_id`
- `user_login`
- `user_name`
- `service_center_name`
- `sort_by`
- `sort_dir`

## Endpoints organizacionales

### `GET /api/v1/organizational/summary`

Filtros:

- `branch_city`
- `role_name`
- `access_group_name`
- `is_active`
- `can_access_nc`

### `GET /api/v1/organizational/users`

Filtros:

- `limit`
- `offset`
- `search`
- `role_name`
- `branch_city`
- `access_group_name`
- `is_active`
- `can_access_nc`
- `has_email`
- `has_phone`
- `sort_by`
- `sort_dir`

### `GET /api/v1/organizational/user-branches`

Filtros:

- `limit`
- `offset`
- `user_id`
- `user_login`
- `branch_id`
- `branch_city`
- `sort_by`
- `sort_dir`

### `GET /api/v1/organizational/group-permissions`

Filtros:

- `limit`
- `offset`
- `group_name`
- `module_name`
- `action_name`
- `is_allowed`
- `is_superadmin`
- `sort_by`
- `sort_dir`

### `GET /api/v1/organizational/user-permissions`

Filtros:

- `limit`
- `offset`
- `user_id`
- `user_login`
- `module_name`
- `action_name`
- `is_allowed`
- `sort_by`
- `sort_dir`
