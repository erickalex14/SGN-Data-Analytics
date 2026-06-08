import { httpClient } from "@/services/http-client";
import type { ExecutiveDashboardResponse } from "@/types/executive";

// Centraliza las consultas del dashboard ejecutivo.
async function getExecutiveDashboard() {
  return httpClient.request<ExecutiveDashboardResponse>("/dashboard/executive");
}

export const executiveService = {
  getExecutiveDashboard,
};
