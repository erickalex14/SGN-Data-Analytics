import { QueryClient } from "@tanstack/react-query";

// Centraliza la estrategia de cache y reintentos del portal.
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 3,
    },
  },
});
