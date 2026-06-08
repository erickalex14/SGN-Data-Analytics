import { BarChart3, Building2, FileOutput, HardDrive, Shield, ShieldCheck, Stethoscope, Wallet } from "lucide-react";
import { NavLink } from "react-router-dom";
import { cn } from "@/shared/utils/cn";

const navigationItems = [
  { to: "/", label: "Resumen Ejecutivo", icon: BarChart3 },
  { to: "/operaciones", label: "Operaciones", icon: Building2 },
  { to: "/financiero", label: "Financiero", icon: Wallet },
  { to: "/tecnico", label: "Tecnico", icon: Stethoscope },
  { to: "/inventario", label: "Inventario", icon: HardDrive },
  { to: "/crm", label: "CRM", icon: Building2 },
  { to: "/garantias", label: "Garantias", icon: ShieldCheck },
  { to: "/organizacional", label: "Organizacional", icon: Shield },
  { to: "/exportes", label: "Exportes", icon: FileOutput },
];

// Renderiza la navegacion lateral principal del portal.
export function SidebarNav() {
  return (
    <aside className="hidden w-72 shrink-0 border-r border-slate-200 bg-white/90 p-6 lg:block">
      <div className="mb-10 space-y-2">
        <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
          Novitec Analytics
        </p>
        <h2 className="text-2xl font-semibold text-slate-950">Portal Ejecutivo</h2>
      </div>
      <nav className="space-y-2">
        {navigationItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-slate-950 text-white"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-950",
                )
              }
            >
              <Icon className="h-4 w-4" />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
