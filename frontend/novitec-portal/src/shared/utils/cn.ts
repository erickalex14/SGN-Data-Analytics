import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// Une clases utilitarias sin duplicados para componentes reutilizables.
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
