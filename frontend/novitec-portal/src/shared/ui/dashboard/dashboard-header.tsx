import { PremiumPanel } from "@/shared/ui/aceternity/premium-panel";

type DashboardHeaderProps = {
  eyebrow: string;
  title: string;
  description: string;
};

// Presenta el encabezado de cada modulo con una capa visual premium.
export function DashboardHeader({
  eyebrow,
  title,
  description,
}: DashboardHeaderProps) {
  return (
    <PremiumPanel className="text-slate-50">
      <div className="space-y-3">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">{eyebrow}</p>
        <h1 className="text-3xl font-semibold">{title}</h1>
        <p className="max-w-3xl text-sm leading-6 text-slate-300">{description}</p>
      </div>
    </PremiumPanel>
  );
}
