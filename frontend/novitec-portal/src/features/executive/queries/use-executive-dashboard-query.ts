import { useQuery } from "@tanstack/react-query";
import { executiveService } from "@/services/executive-service";

// Consulta el resumen ejecutivo consolidado desde la API actual.
export function useExecutiveDashboardQuery() {
  return useQuery({
    queryKey: ["executive-dashboard"],
    queryFn: () => executiveService.getExecutiveDashboard(),
  });
}
