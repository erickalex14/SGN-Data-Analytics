import { DashboardHeader } from "@/shared/ui/dashboard/dashboard-header";
import { PlaceholderBlock } from "@/shared/ui/feedback/placeholder-block";

type DomainPagePlaceholderProps = {
  title: string;
  description: string;
};

// Muestra un estado inicial mientras se construyen las paginas por dominio.
export function DomainPagePlaceholder({
  title,
  description,
}: DomainPagePlaceholderProps) {
  return (
    <section className="space-y-6">
      <DashboardHeader
        eyebrow="Modulo en construccion"
        title={title}
        description={description}
      />
      <div className="grid gap-6 xl:grid-cols-2">
        <PlaceholderBlock
          title="Filtros y KPIs"
          description="Aqui viviran los indicadores y filtros ejecutivos de este dominio."
        />
        <PlaceholderBlock
          title="Graficos y tablas"
          description="Aqui viviran los graficos ECharts y tablas enterprise del dominio."
        />
      </div>
    </section>
  );
}
