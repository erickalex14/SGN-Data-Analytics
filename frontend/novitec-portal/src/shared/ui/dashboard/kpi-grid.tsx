import { KpiCard } from "@/shared/ui/dashboard/kpi-card";

type KpiGridProps = {
  isLoading?: boolean;
  items: Array<{
    label: string;
    value?: number | string | null;
  }>;
};

// Organiza los KPIs principales del dashboard en una grilla uniforme.
export function KpiGrid({ isLoading = false, items }: KpiGridProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {items.map((item) => (
        <KpiCard
          key={item.label}
          label={item.label}
          value={isLoading ? "Cargando..." : item.value}
        />
      ))}
    </div>
  );
}
