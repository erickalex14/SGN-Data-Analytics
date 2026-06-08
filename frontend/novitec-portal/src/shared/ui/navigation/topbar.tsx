import { CalendarRange, Search } from "lucide-react";

// Renderiza la cabecera superior con espacio para filtros globales.
export function Topbar() {
  return (
    <header className="border-b border-slate-200 bg-white/80 px-6 py-4 backdrop-blur md:px-8">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">Panel de control gerencial</p>
          <h1 className="text-xl font-semibold text-slate-950">
            Inteligencia operativa y financiera
          </h1>
        </div>
        <div className="flex flex-col gap-3 md:flex-row">
          <div className="flex min-w-72 items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500">
            <Search className="h-4 w-4" />
            <span>Busqueda global pendiente de integrar</span>
          </div>
          <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-600">
            <CalendarRange className="h-4 w-4" />
            <span>Filtro global de fechas</span>
          </div>
        </div>
      </div>
    </header>
  );
}
