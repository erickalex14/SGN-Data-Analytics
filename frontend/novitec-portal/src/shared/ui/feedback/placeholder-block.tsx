type PlaceholderBlockProps = {
  title: string;
  description: string;
};

// Reserva espacio visual para bloques funcionales pendientes de integrar.
export function PlaceholderBlock({ title, description }: PlaceholderBlockProps) {
  return (
    <article className="rounded-xl border border-dashed border-slate-300 bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-950">{title}</h2>
      <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600">{description}</p>
    </article>
  );
}
