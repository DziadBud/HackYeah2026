import { Icon } from "@/components/Icon";

// single-series charts for the admin stats. one hue (primary, remapped in high contrast),
// every bar carries its value as text, so nothing is read from colour or length alone.

export interface Bar {
  label: string;
  // null = hidden for privacy; `note` is shown instead of a bar
  value: number | null;
  note?: string;
}

export function BarList({ bars, unit, empty }: { bars: Bar[]; unit: (n: number) => string; empty: string }) {
  if (bars.length === 0) return <p className="text-body-md text-on-surface-variant">{empty}</p>;
  const max = Math.max(1, ...bars.map((b) => b.value ?? 0));
  return (
    <ul className="flex flex-col gap-space-sm">
      {bars.map((b) => (
        <li key={b.label} className="flex flex-col gap-1">
          <span className="flex flex-wrap items-baseline justify-between gap-2 text-body-md">
            <span className="font-semibold text-on-surface">{b.label}</span>
            <span className="text-on-surface-variant">{b.value === null ? b.note : unit(b.value)}</span>
          </span>
          {b.value !== null && (
            <span aria-hidden="true" className="h-2 w-full rounded-full bg-surface-container hc-edge">
              <span
                className="block h-full rounded-full bg-primary"
                style={{ width: `${(b.value / max) * 100}%` }}
              />
            </span>
          )}
        </li>
      ))}
    </ul>
  );
}

const weekLabel = (iso: string) => new Date(iso).toLocaleDateString("pl-PL", { day: "numeric", month: "short" });

export function WeeklyColumns({ weeks, caption }: { weeks: { week_start: string; matches: number }[]; caption: string }) {
  const max = Math.max(1, ...weeks.map((w) => w.matches));
  return (
    <figure className="flex flex-col gap-space-sm">
      <figcaption className="sr-only">{caption}</figcaption>
      <div aria-hidden="true" className="flex h-44 items-end gap-space-sm border-b-2 border-outline px-1">
        {weeks.map((w) => (
          <div key={w.week_start} className="flex h-full flex-1 flex-col items-center justify-end gap-1">
            <span className="text-label-md font-semibold text-on-surface">{w.matches}</span>
            <span
              className="w-full max-w-12 rounded-t bg-primary"
              style={{ height: `${(w.matches / max) * 80}%`, minHeight: w.matches ? 4 : 0 }}
            />
          </div>
        ))}
      </div>
      <div aria-hidden="true" className="flex gap-space-sm px-1">
        {weeks.map((w) => (
          <span key={w.week_start} className="flex-1 text-center text-caption text-on-surface-variant">
            {weekLabel(w.week_start)}
          </span>
        ))}
      </div>
      <details className="text-body-md">
        <summary className="flex min-h-12 cursor-pointer items-center font-semibold text-primary">Pokaż jako tabelę</summary>
        <table className="w-full border-collapse">
          <caption className="sr-only">{caption}</caption>
          <thead>
            <tr>
              <th scope="col" className="border-b-2 border-outline px-3 py-2 text-left">Tydzień od</th>
              <th scope="col" className="border-b-2 border-outline px-3 py-2 text-right">Dopasowania</th>
            </tr>
          </thead>
          <tbody>
            {weeks.map((w) => (
              <tr key={w.week_start}>
                <td className="border-b border-surface-container-highest px-3 py-2">{weekLabel(w.week_start)}</td>
                <td className="border-b border-surface-container-highest px-3 py-2 text-right">{w.matches}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  );
}

// week-over-week change, spelled out (icon + text, never colour alone)
export function Trend({ now, before }: { now: number; before: number }) {
  const diff = now - before;
  const icon = diff > 0 ? "trending_up" : diff < 0 ? "trending_down" : "trending_flat";
  const text = diff === 0 ? "bez zmian" : `${diff > 0 ? "+" : "−"}${Math.abs(diff)}`;
  return (
    <span className="inline-flex items-center gap-1 text-label-md text-on-surface-variant">
      <Icon name={icon} size={18} className="text-primary" />
      {text}
      <span className="sr-only"> względem poprzednich 7 dni</span>
    </span>
  );
}

export function Stars({ avg, count }: { avg: number | null; count: number }) {
  if (avg === null) return <span className="text-on-surface-variant">brak ocen</span>;
  return (
    <span className="inline-flex items-center gap-1">
      <Icon name="star" fill size={18} className="text-primary" />
      <strong className="text-on-surface">{avg.toLocaleString("pl-PL", { maximumFractionDigits: 1 })}</strong>
      <span className="text-on-surface-variant">/ 5 ({count} {plural(count, "ocena", "oceny", "ocen")})</span>
    </span>
  );
}

// polish plural forms: 1 ocena, 2-4 oceny, 5+ ocen (12-14 too)
export function plural(n: number, one: string, few: string, many: string) {
  if (n === 1) return one;
  const d = n % 10;
  const t = n % 100;
  return d >= 2 && d <= 4 && (t < 12 || t > 14) ? few : many;
}
