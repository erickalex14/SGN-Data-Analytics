import { env } from "@/shared/config/env";

// Ejecuta solicitudes HTTP hacia la API analitica del portal.
async function request<T>(endpoint: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);

  headers.set("Content-Type", "application/json");

  // Permite seguir usando el token actual mientras migramos a sesiones seguras.
  if (env.apiToken) {
    headers.set("Authorization", `Bearer ${env.apiToken}`);
  }

  const response = await fetch(`${env.apiBaseUrl}${endpoint}`, {
    ...init,
    headers,
  });

  if (!response.ok) {
    throw new Error(`La API respondio con estado ${response.status}.`);
  }

  return (await response.json()) as T;
}

export const httpClient = {
  request,
};
