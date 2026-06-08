import { useExecutiveDashboardQuery } from "@/features/executive/queries/use-executive-dashboard-query";
import { DashboardHeader } from "@/shared/ui/dashboard/dashboard-header";
import { KpiGrid } from "@/shared/ui/dashboard/kpi-grid";
import { PlaceholderBlock } from "@/shared/ui/feedback/placeholder-block";

// Renderiza el resumen ejecutivo inicial del portal.
export function ExecutiveDashboardPage() {
  const executiveDashboardQuery = useExecutiveDashboardQuery();

  return (
    <section className="space-y-6">
      <DashboardHeader
        eyebrow="Resumen consolidado"
        title="Vista ejecutiva"
        description="KPIs transversales de operaciones, finanzas, tecnico, inventario y gestion interna."
      />
      <KpiGrid
        isLoading={executiveDashboardQuery.isLoading}
        items={[
          {
            label: "Ordenes totales",
            value: executiveDashboardQuery.data?.operational.total_orders,
          },
          {
            label: "Solicitudes NC",
            value: executiveDashboardQuery.data?.financial.total_credit_note_requests,
          },
          {
            label: "Informes tecnicos",
            value: executiveDashboardQuery.data?.technical.total_reports,
          },
          {
            label: "Solicitudes de repuesto",
            value: executiveDashboardQuery.data?.inventory.total_spare_part_requests,
          },
        ]}
      />
      <div className="grid gap-6 xl:grid-cols-[1.4fr_1fr]">
        <PlaceholderBlock
          title="Graficos ejecutivos"
          description="Aqui viviran los graficos ECharts de tendencia, distribucion y comparativos."
        />
        <PlaceholderBlock
          title="Filtros globales"
          description="Este bloque concentrara fechas, tecnico, sucursal, estado y exportes."
        />
      </div>
    </section>
  );
}
