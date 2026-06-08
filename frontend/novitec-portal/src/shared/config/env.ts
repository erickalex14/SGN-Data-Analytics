import { z } from "zod";

// Valida las variables de entorno usadas por el frontend.
const envSchema = z.object({
  VITE_API_BASE_URL: z.string().min(1),
  VITE_API_TOKEN: z.string().optional().default(""),
});

const parsedEnv = envSchema.parse(import.meta.env);

export const env = {
  apiBaseUrl: parsedEnv.VITE_API_BASE_URL,
  apiToken: parsedEnv.VITE_API_TOKEN,
};
