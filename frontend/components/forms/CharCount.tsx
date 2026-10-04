// shown from 80% of the limit: below that a counter is noise, at the limit pasted text gets cut silently
export function CharCount({ id, length, max }: { id: string; length: number; max: number }) {
  if (length < max * 0.8) return null;
  const full = length >= max;
  return (
    <p id={id} className={`text-body-md ${full ? "font-semibold text-error" : "text-on-surface-variant"}`}>
      {length.toLocaleString("pl-PL")} / {max.toLocaleString("pl-PL")} znaków{full ? ": osiągnięto limit, dalszy tekst nie zostanie dodany" : ""}
    </p>
  );
}
