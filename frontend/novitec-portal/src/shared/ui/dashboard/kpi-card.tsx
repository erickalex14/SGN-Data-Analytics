import { cn } from "@/shared/utils/cn";

type KpiCardProps = {
  label: string;
  value?: number | string | null;
  className?: string;
};

// Presenta un KPI ejecutivo con lectura rapida y formato sobrio.
export function KpiCard({ label, value, className }: KpiCardProps) {
  return (
    <article
      className={cn(
        "rounded-xl border border-slate-200 bg-white p-5 shadow-sm",
        className,
      )}
    >
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-3 text-3xl font-semibold tracking-tight text-slate-950">
        {value ?? "--"}
      </p>
    </article>
  );
}
