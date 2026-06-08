CREATE SCHEMA IF NOT EXISTS {semantic_schema};

CREATE OR REPLACE VIEW {semantic_schema}.vw_executive_dashboard AS
WITH
financial_latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {financial_mart_schema}.fact_financial_credit_note_requests
),
financial_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_solicitudes_nc,
        COALESCE(SUM(CASE WHEN is_approved THEN 1 ELSE 0 END), 0)::INTEGER AS solicitudes_aprobadas,
        COALESCE(SUM(CASE WHEN is_rejected THEN 1 ELSE 0 END), 0)::INTEGER AS solicitudes_rechazadas,
        COALESCE(SUM(CASE WHEN is_pending THEN 1 ELSE 0 END), 0)::INTEGER AS solicitudes_pendientes
    FROM {financial_mart_schema}.fact_financial_credit_note_requests
    WHERE extraction_id = (SELECT extraction_id FROM financial_latest)
),
financial_income AS (
    SELECT
        COUNT(*)::INTEGER AS total_registros_ingreso,
        COALESCE(SUM(amount), 0) AS monto_total_ingresos
    FROM {financial_mart_schema}.fact_financial_order_prices
    WHERE extraction_id = (SELECT extraction_id FROM financial_latest)
),
financial_notifications AS (
    SELECT
        COUNT(*)::INTEGER AS total_notificaciones,
        COALESCE(SUM(CASE WHEN is_read THEN 1 ELSE 0 END), 0)::INTEGER AS total_notificaciones_leidas
    FROM {financial_mart_schema}.fact_financial_credit_note_notifications
    WHERE extraction_id = (SELECT extraction_id FROM financial_latest)
),
operational_latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {operational_mart_schema}.fact_operational_orders
),
operational_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_ordenes,
        COALESCE(SUM(CASE WHEN is_open THEN 1 ELSE 0 END), 0)::INTEGER AS ordenes_abiertas,
        COALESCE(SUM(CASE WHEN is_delivered THEN 1 ELSE 0 END), 0)::INTEGER AS ordenes_entregadas,
        COALESCE(SUM(CASE WHEN is_warranty THEN 1 ELSE 0 END), 0)::INTEGER AS ordenes_con_garantia,
        COALESCE(AVG(cycle_days), 0) AS promedio_dias_ciclo
    FROM {operational_mart_schema}.fact_operational_orders
    WHERE extraction_id = (SELECT extraction_id FROM operational_latest)
),
technical_latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {technical_mart_schema}.fact_technical_reports
),
technical_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_informes,
        COALESCE(SUM(CASE WHEN is_equipment_operational THEN 1 ELSE 0 END), 0)::INTEGER AS informes_equipo_operativo,
        COALESCE(SUM(CASE WHEN has_budget_json THEN 1 ELSE 0 END), 0)::INTEGER AS informes_con_presupuesto
    FROM {technical_mart_schema}.fact_technical_reports
    WHERE extraction_id = (SELECT extraction_id FROM technical_latest)
),
inventory_latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {inventory_mart_schema}.fact_inventory_spare_parts
),
inventory_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_repuestos,
        COALESCE(SUM(CASE WHEN has_stock THEN 1 ELSE 0 END), 0)::INTEGER AS repuestos_con_stock,
        COALESCE(SUM(current_stock), 0)::INTEGER AS stock_total_unidades,
        COALESCE(SUM(current_stock * current_cost), 0) AS costo_total_inventario
    FROM {inventory_mart_schema}.fact_inventory_spare_parts
    WHERE extraction_id = (SELECT extraction_id FROM inventory_latest)
),
inventory_request_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_solicitudes_repuesto,
        COALESCE(SUM(CASE WHEN is_approved THEN 1 ELSE 0 END), 0)::INTEGER AS solicitudes_repuesto_aprobadas,
        COALESCE(SUM(CASE WHEN is_pending THEN 1 ELSE 0 END), 0)::INTEGER AS solicitudes_repuesto_pendientes
    FROM {inventory_mart_schema}.fact_inventory_spare_part_requests
    WHERE extraction_id = (SELECT extraction_id FROM inventory_latest)
),
crm_latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {crm_mart_schema}.fact_crm_customers
),
crm_customer_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_clientes,
        COALESCE(SUM(CASE WHEN has_email THEN 1 ELSE 0 END), 0)::INTEGER AS clientes_con_correo
    FROM {crm_mart_schema}.fact_crm_customers
    WHERE extraction_id = (SELECT extraction_id FROM crm_latest)
),
crm_company_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_empresas,
        COALESCE(SUM(CASE WHEN has_email THEN 1 ELSE 0 END), 0)::INTEGER AS empresas_con_correo
    FROM {crm_mart_schema}.fact_crm_companies
    WHERE extraction_id = (SELECT extraction_id FROM crm_latest)
),
warranty_latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {warranty_mart_schema}.fact_warranty_personal_orders
),
warranty_personal_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_ordenes_personales_garantia,
        COALESCE(SUM(CASE WHEN has_case_number THEN 1 ELSE 0 END), 0)::INTEGER AS ordenes_personales_con_caso
    FROM {warranty_mart_schema}.fact_warranty_personal_orders
    WHERE extraction_id = (SELECT extraction_id FROM warranty_latest)
),
warranty_company_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_ordenes_empresariales_garantia,
        COALESCE(SUM(CASE WHEN has_ticket_number THEN 1 ELSE 0 END), 0)::INTEGER AS ordenes_empresariales_con_ticket
    FROM {warranty_mart_schema}.fact_warranty_company_orders
    WHERE extraction_id = (SELECT extraction_id FROM warranty_latest)
),
organizational_latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {organizational_mart_schema}.fact_organizational_users
),
organizational_summary AS (
    SELECT
        COUNT(*)::INTEGER AS total_usuarios,
        COALESCE(SUM(CASE WHEN is_active THEN 1 ELSE 0 END), 0)::INTEGER AS usuarios_activos,
        COALESCE(SUM(CASE WHEN can_access_nc THEN 1 ELSE 0 END), 0)::INTEGER AS usuarios_con_acceso_nc
    FROM {organizational_mart_schema}.fact_organizational_users
    WHERE extraction_id = (SELECT extraction_id FROM organizational_latest)
)
SELECT
    CURRENT_TIMESTAMP AS generated_at,
    (SELECT extraction_id FROM financial_latest) AS financial_extraction_id,
    (SELECT extraction_id FROM operational_latest) AS operational_extraction_id,
    (SELECT extraction_id FROM technical_latest) AS technical_extraction_id,
    (SELECT extraction_id FROM inventory_latest) AS inventory_extraction_id,
    (SELECT extraction_id FROM crm_latest) AS crm_extraction_id,
    (SELECT extraction_id FROM warranty_latest) AS warranty_extraction_id,
    (SELECT extraction_id FROM organizational_latest) AS organizational_extraction_id,
    financial_summary.total_solicitudes_nc,
    financial_summary.solicitudes_aprobadas,
    financial_summary.solicitudes_rechazadas,
    financial_summary.solicitudes_pendientes,
    financial_income.total_registros_ingreso,
    financial_income.monto_total_ingresos,
    financial_notifications.total_notificaciones,
    financial_notifications.total_notificaciones_leidas,
    operational_summary.total_ordenes,
    operational_summary.ordenes_abiertas,
    operational_summary.ordenes_entregadas,
    operational_summary.ordenes_con_garantia,
    operational_summary.promedio_dias_ciclo,
    technical_summary.total_informes,
    technical_summary.informes_equipo_operativo,
    technical_summary.informes_con_presupuesto,
    inventory_summary.total_repuestos,
    inventory_summary.repuestos_con_stock,
    inventory_summary.stock_total_unidades,
    inventory_summary.costo_total_inventario,
    inventory_request_summary.total_solicitudes_repuesto,
    inventory_request_summary.solicitudes_repuesto_aprobadas,
    inventory_request_summary.solicitudes_repuesto_pendientes,
    crm_customer_summary.total_clientes,
    crm_customer_summary.clientes_con_correo,
    crm_company_summary.total_empresas,
    crm_company_summary.empresas_con_correo,
    warranty_personal_summary.total_ordenes_personales_garantia,
    warranty_personal_summary.ordenes_personales_con_caso,
    warranty_company_summary.total_ordenes_empresariales_garantia,
    warranty_company_summary.ordenes_empresariales_con_ticket,
    organizational_summary.total_usuarios,
    organizational_summary.usuarios_activos,
    organizational_summary.usuarios_con_acceso_nc
FROM financial_summary
CROSS JOIN financial_income
CROSS JOIN financial_notifications
CROSS JOIN operational_summary
CROSS JOIN technical_summary
CROSS JOIN inventory_summary
CROSS JOIN inventory_request_summary
CROSS JOIN crm_customer_summary
CROSS JOIN crm_company_summary
CROSS JOIN warranty_personal_summary
CROSS JOIN warranty_company_summary
CROSS JOIN organizational_summary;

CREATE OR REPLACE VIEW {semantic_schema}.vw_financial_credit_notes AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {financial_mart_schema}.fact_financial_credit_note_requests
)
SELECT
    fact.extraction_id,
    fact.request_number,
    fact.order_id,
    fact.order_number,
    request_date.full_date AS request_date,
    fact.status_name,
    fact.subject_name,
    fact.admin_name,
    fact.rejection_reason,
    tech.tecnico_nombre AS technician_name,
    fact.created_at,
    fact.is_approved,
    fact.is_rejected,
    fact.is_pending
FROM {financial_mart_schema}.fact_financial_credit_note_requests fact
INNER JOIN {financial_mart_schema}.dim_financial_date request_date
    ON request_date.date_key = fact.request_date_key
INNER JOIN {financial_mart_schema}.dim_financial_technician tech
    ON tech.technician_key = fact.technician_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_financial_order_prices AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {financial_mart_schema}.fact_financial_order_prices
)
SELECT
    fact.extraction_id,
    fact.order_id,
    fact.order_number,
    created_date.full_date AS created_date,
    fact.service_name,
    fact.standard_service_name,
    fact.amount,
    fact.standard_amount
FROM {financial_mart_schema}.fact_financial_order_prices fact
LEFT JOIN {financial_mart_schema}.dim_financial_date created_date
    ON created_date.date_key = fact.created_date_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_operational_orders AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {operational_mart_schema}.fact_operational_orders
)
SELECT
    fact.extraction_id,
    fact.source_order_id,
    fact.order_type,
    fact.order_number,
    intake_date.full_date AS intake_date,
    promised_date.full_date AS promised_date,
    delivery_date.full_date AS delivery_date,
    fact.order_status,
    fact.intake_reason,
    fact.customer_type,
    fact.customer_name,
    tech.tecnico_nombre AS technician_name,
    branch.sucursal_nombre AS branch_name,
    fact.cycle_days,
    fact.delay_days,
    fact.worked_hours,
    fact.hourly_rate,
    fact.is_open,
    fact.is_delivered,
    fact.is_warranty
FROM {operational_mart_schema}.fact_operational_orders fact
LEFT JOIN {operational_mart_schema}.dim_operational_date intake_date
    ON intake_date.date_key = fact.intake_date_key
LEFT JOIN {operational_mart_schema}.dim_operational_date promised_date
    ON promised_date.date_key = fact.promised_date_key
LEFT JOIN {operational_mart_schema}.dim_operational_date delivery_date
    ON delivery_date.date_key = fact.delivery_date_key
LEFT JOIN {operational_mart_schema}.dim_operational_technician tech
    ON tech.technician_key = fact.technician_key
LEFT JOIN {operational_mart_schema}.dim_operational_branch branch
    ON branch.branch_key = fact.branch_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_operational_preorders AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {operational_mart_schema}.fact_operational_preorders
)
SELECT
    fact.extraction_id,
    fact.source_id,
    fact.linked_order_id,
    fact.preorder_number,
    registration_date.full_date AS registration_date,
    fact.preorder_status,
    fact.customer_name,
    branch.sucursal_nombre AS branch_name,
    fact.city_name,
    fact.has_invoice,
    fact.has_photos
FROM {operational_mart_schema}.fact_operational_preorders fact
LEFT JOIN {operational_mart_schema}.dim_operational_date registration_date
    ON registration_date.date_key = fact.registration_date_key
LEFT JOIN {operational_mart_schema}.dim_operational_branch branch
    ON branch.branch_key = fact.branch_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_technical_reports AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {technical_mart_schema}.fact_technical_reports
)
SELECT
    fact.extraction_id,
    fact.source_id,
    fact.order_id,
    report_date.full_date AS report_date,
    fact.created_at,
    tech.tecnico_nombre AS technician_name,
    fact.equipment_status,
    fact.has_background,
    fact.has_process,
    fact.has_conclusion,
    fact.has_recommendations,
    fact.has_budget_json,
    fact.is_equipment_operational,
    fact.background_length,
    fact.process_length,
    fact.conclusion_length,
    fact.recommendation_length
FROM {technical_mart_schema}.fact_technical_reports fact
LEFT JOIN {technical_mart_schema}.dim_technical_date report_date
    ON report_date.date_key = fact.report_date_key
LEFT JOIN {technical_mart_schema}.dim_technical_technician tech
    ON tech.technician_key = fact.technician_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_technical_equipment AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {technical_mart_schema}.fact_technical_equipment
)
SELECT
    fact.extraction_id,
    fact.source_id,
    billing_date.full_date AS billing_date,
    service.service_name,
    brand.brand_name,
    fact.device_type_name,
    fact.device_model,
    fact.serial_number,
    fact.inventory_product_code,
    fact.has_password_provided,
    fact.has_failure_description,
    fact.has_observation,
    fact.has_billing_date
FROM {technical_mart_schema}.fact_technical_equipment fact
LEFT JOIN {technical_mart_schema}.dim_technical_date billing_date
    ON billing_date.date_key = fact.billing_date_key
LEFT JOIN {technical_mart_schema}.dim_technical_service_type service
    ON service.service_type_key = fact.service_type_key
LEFT JOIN {technical_mart_schema}.dim_technical_brand brand
    ON brand.brand_key = fact.brand_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_inventory_stock AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {inventory_mart_schema}.fact_inventory_spare_parts
)
SELECT
    fact.extraction_id,
    fact.source_id,
    dim.spare_part_code,
    dim.part_number,
    dim.spare_part_name,
    created_date.full_date AS created_date,
    updated_date.full_date AS updated_date,
    fact.current_stock,
    fact.current_cost,
    fact.warehouse_number,
    fact.has_stock,
    fact.has_part_number
FROM {inventory_mart_schema}.fact_inventory_spare_parts fact
INNER JOIN {inventory_mart_schema}.dim_inventory_spare_part dim
    ON dim.spare_part_key = fact.spare_part_key
LEFT JOIN {inventory_mart_schema}.dim_inventory_date created_date
    ON created_date.date_key = fact.created_date_key
LEFT JOIN {inventory_mart_schema}.dim_inventory_date updated_date
    ON updated_date.date_key = fact.updated_date_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_inventory_requests AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {inventory_mart_schema}.fact_inventory_spare_part_requests
)
SELECT
    fact.extraction_id,
    fact.source_id,
    fact.request_number,
    fact.order_id,
    tech.tecnico_nombre AS technician_name,
    dim.spare_part_code,
    dim.spare_part_name,
    request_date.full_date AS request_date,
    management_date.full_date AS management_date,
    fact.approved_by,
    fact.request_status,
    fact.quantity,
    fact.is_approved,
    fact.is_rejected,
    fact.is_pending,
    fact.has_purchase_link
FROM {inventory_mart_schema}.fact_inventory_spare_part_requests fact
INNER JOIN {inventory_mart_schema}.dim_inventory_technician tech
    ON tech.technician_key = fact.technician_key
LEFT JOIN {inventory_mart_schema}.dim_inventory_spare_part dim
    ON dim.spare_part_key = fact.spare_part_key
INNER JOIN {inventory_mart_schema}.dim_inventory_date request_date
    ON request_date.date_key = fact.request_date_key
LEFT JOIN {inventory_mart_schema}.dim_inventory_date management_date
    ON management_date.date_key = fact.management_date_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_crm_customers AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {crm_mart_schema}.fact_crm_customers
)
SELECT
    fact.extraction_id,
    fact.source_id,
    dim.full_name,
    dim.first_name,
    dim.last_name,
    dim.identification,
    dim.phone_number,
    dim.email,
    dim.address,
    fact.has_email,
    fact.has_address,
    fact.has_phone
FROM {crm_mart_schema}.fact_crm_customers fact
INNER JOIN {crm_mart_schema}.dim_crm_customer dim
    ON dim.customer_key = fact.customer_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_crm_companies AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {crm_mart_schema}.fact_crm_companies
)
SELECT
    fact.extraction_id,
    fact.source_id,
    dim.company_name,
    dim.ruc,
    dim.phone_number,
    dim.email,
    dim.address,
    created_date.full_date AS created_date,
    fact.has_phone,
    fact.has_email,
    fact.has_address
FROM {crm_mart_schema}.fact_crm_companies fact
INNER JOIN {crm_mart_schema}.dim_crm_company dim
    ON dim.company_key = fact.company_key
LEFT JOIN {crm_mart_schema}.dim_crm_date created_date
    ON created_date.date_key = fact.created_date_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_crm_customer_branches AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {crm_mart_schema}.fact_crm_customer_branches
)
SELECT
    fact.extraction_id,
    fact.source_id,
    created_date.full_date AS created_date,
    fact.branch_code,
    fact.branch_number,
    fact.branch_name,
    fact.province,
    fact.novitec_branch_name,
    fact.is_active
FROM {crm_mart_schema}.fact_crm_customer_branches fact
LEFT JOIN {crm_mart_schema}.dim_crm_date created_date
    ON created_date.date_key = fact.created_date_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_warranty_personal_orders AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {warranty_mart_schema}.fact_warranty_personal_orders
)
SELECT
    fact.extraction_id,
    fact.source_id,
    fact.order_number,
    fact.order_status,
    fact.warranty_status,
    fact.warranty_type,
    fact.service_center_name,
    opened_date.full_date AS opened_date,
    promised_date.full_date AS promised_date,
    shipped_date.full_date AS shipped_date,
    returned_date.full_date AS returned_date,
    delivered_date.full_date AS delivered_date,
    finalized_date.full_date AS finalized_date,
    usr.source_id AS technician_id,
    fact.branch_id,
    fact.client_id,
    fact.equipment_id,
    fact.case_number,
    fact.cycle_days,
    fact.sla_days,
    fact.has_case_number,
    fact.has_return_date,
    fact.is_closed
FROM {warranty_mart_schema}.fact_warranty_personal_orders fact
LEFT JOIN {warranty_mart_schema}.dim_warranty_user usr
    ON usr.user_key = fact.technician_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date opened_date
    ON opened_date.date_key = fact.opened_date_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date promised_date
    ON promised_date.date_key = fact.promised_date_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date shipped_date
    ON shipped_date.date_key = fact.shipped_date_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date returned_date
    ON returned_date.date_key = fact.returned_date_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date delivered_date
    ON delivered_date.date_key = fact.delivered_date_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date finalized_date
    ON finalized_date.date_key = fact.finalized_date_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_warranty_company_orders AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {warranty_mart_schema}.fact_warranty_company_orders
)
SELECT
    fact.extraction_id,
    fact.source_id,
    fact.order_number,
    fact.order_status,
    opened_date.full_date AS opened_date,
    promised_date.full_date AS promised_date,
    cas.service_center_name,
    usr.source_id AS technician_id,
    fact.branch_id,
    fact.company_id,
    fact.equipment_id,
    fact.ticket_number,
    fact.hourly_rate,
    fact.worked_hours,
    fact.estimated_revenue,
    fact.cycle_days,
    fact.sla_days,
    fact.has_ticket_number,
    fact.has_worked_hours
FROM {warranty_mart_schema}.fact_warranty_company_orders fact
LEFT JOIN {warranty_mart_schema}.dim_warranty_service_center cas
    ON cas.service_center_key = fact.service_center_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_user usr
    ON usr.user_key = fact.technician_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date opened_date
    ON opened_date.date_key = fact.opened_date_key
LEFT JOIN {warranty_mart_schema}.dim_warranty_date promised_date
    ON promised_date.date_key = fact.promised_date_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);

CREATE OR REPLACE VIEW {semantic_schema}.vw_organizational_users AS
WITH latest AS (
    SELECT MAX(extraction_id) AS extraction_id
    FROM {organizational_mart_schema}.fact_organizational_users
)
SELECT
    fact.extraction_id,
    fact.source_id,
    usr.user_login,
    usr.user_name,
    rol.role_name,
    suc.branch_number,
    suc.city_name AS branch_city,
    suc.sequential_code,
    grp.group_name AS access_group_name,
    grp.is_superadmin,
    fact.has_phone,
    fact.has_email,
    fact.can_access_nc,
    fact.is_active,
    fact.has_access_group
FROM {organizational_mart_schema}.fact_organizational_users fact
INNER JOIN {organizational_mart_schema}.dim_organizational_user usr
    ON usr.user_key = fact.user_key
LEFT JOIN {organizational_mart_schema}.dim_organizational_role rol
    ON rol.role_key = fact.role_key
LEFT JOIN {organizational_mart_schema}.dim_organizational_branch suc
    ON suc.branch_key = fact.branch_key
LEFT JOIN {organizational_mart_schema}.dim_organizational_access_group grp
    ON grp.access_group_key = fact.access_group_key
WHERE fact.extraction_id = (SELECT extraction_id FROM latest);
