// Muestra una carga limpia mientras una ruta diferida termina de descargarse.
export function RouteLoadingFallback() {
  return (
    <div className="flex min-h-[40vh] items-center justify-center">
      <div className="rounded-xl border border-slate-200 bg-white px-6 py-5 text-sm font-medium text-slate-600 shadow-sm">
        Cargando modulo del portal...
      </div>
    </div>
  );
}
