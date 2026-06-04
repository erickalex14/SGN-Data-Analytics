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
