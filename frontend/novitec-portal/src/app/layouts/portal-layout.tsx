import { Outlet } from "react-router-dom";
import { SidebarNav } from "@/shared/ui/navigation/sidebar-nav";
import { Topbar } from "@/shared/ui/navigation/topbar";

// Define el cascaron principal del portal con navegacion lateral y cabecera.
export function PortalLayout() {
  return (
    <div className="min-h-screen bg-slate-100 text-slate-950">
      <div className="mx-auto flex min-h-screen max-w-[1680px]">
        <SidebarNav />
        <div className="flex min-h-screen flex-1 flex-col">
          <Topbar />
          <main className="flex-1 p-6 md:p-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
}
