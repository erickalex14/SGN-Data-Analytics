import type { PropsWithChildren } from "react";
import { motion } from "framer-motion";
import { cn } from "@/shared/utils/cn";

type PremiumPanelProps = PropsWithChildren<{
  className?: string;
}>;

// Crea un contenedor premium inspirado en patrones visuales de Aceternity UI.
export function PremiumPanel({ children, className }: PremiumPanelProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className={cn(
        "relative overflow-hidden rounded-xl border border-white/10 bg-slate-900/80 p-6 shadow-executive backdrop-blur",
        className,
      )}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(34,211,238,0.16),transparent_32%),radial-gradient(circle_at_bottom_left,rgba(59,130,246,0.14),transparent_28%)]" />
      <div className="relative">{children}</div>
    </motion.div>
  );
}
