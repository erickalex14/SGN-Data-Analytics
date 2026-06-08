import { ShieldCheck } from "lucide-react";
import { PremiumPanel } from "@/shared/ui/aceternity/premium-panel";

// Presenta la puerta de entrada inicial del portal.
export function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 p-6">
      <PremiumPanel className="max-w-lg">
        <div className="space-y-6">
          <div className="flex items-center gap-3 text-slate-50">
            <div className="rounded-lg bg-cyan-400/15 p-3 text-cyan-300">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm uppercase tracking-[0.24em] text-slate-400">
                Novitec Analytics
              </p>
              <h1 className="text-2xl font-semibold">Portal Ejecutivo</h1>
            </div>
          </div>
          <p className="text-sm leading-6 text-slate-300">
            Esta pantalla queda lista para integrar autenticacion por sesion segura
            en una siguiente fase.
          </p>
        </div>
      </PremiumPanel>
    </div>
  );
}
