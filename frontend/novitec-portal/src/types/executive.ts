// Modela la respuesta actual del endpoint ejecutivo consolidado.
export type ExecutiveDashboardResponse = {
  filters: Record<string, string | null>;
  financial: {
    total_credit_note_requests: number;
    approved_credit_note_requests: number;
    rejected_credit_note_requests: number;
    pending_credit_note_requests: number;
    total_income_amount: number;
    total_notifications: number;
  };
  operational: {
    total_orders: number;
    open_orders: number;
    delivered_orders: number;
    total_preorders: number;
    average_cycle_days: number;
  };
  technical: {
    total_reports: number;
    reports_with_budget: number;
    operational_reports: number;
    total_equipment_records: number;
  };
  inventory: {
    total_spare_parts: number;
    spare_parts_with_stock: number;
    total_order_spare_parts: number;
    total_spare_part_requests: number;
  };
  crm: {
    total_customers: number;
    total_companies: number;
    total_customer_branches: number;
  };
  warranty: {
    total_service_centers: number;
    total_warranty_personal_orders: number;
    total_warranty_company_orders: number;
  };
  organizational: {
    total_users: number;
    active_users: number;
    total_group_permissions: number;
    total_user_permissions: number;
  };
  kpis: Record<string, number>;
};
