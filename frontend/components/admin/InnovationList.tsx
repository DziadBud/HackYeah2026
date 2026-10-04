"use client";

import Link from "next/link";
import { useId, useState } from "react";
import { adminApi, type AdminInnovation, type ChallengeArea, type InnovationStatsRow } from "@/lib/api";
import { ADMIN_MOCK, mockInnovationStatsReport } from "@/lib/admin-mock";
import { AREA_LABEL, COST, READINESS } from "@/lib/labels";
import { Icon } from "@/components/Icon";
import { Trend, plural } from "@/components/admin/charts";
import { card, field, fmtDate, ghostBtn, h2, primaryBtn } from "@/components/admin/styles";
import { RatingsDropdown } from "@/components/admin/RatingsDropdown";
import { useApiOrMock, type Source } from "@/components/admin/useApiOrMock";

export interface Row {
  innovation: AdminInnovation;
  stats: InnovationStatsRow | undefined;
}

type Sort = "matches" | "growth" | "rating" | "testers" | "title";
const SORTS: Record<Sort, string> = {
  matches: "Najczęściej dopasowywane",
  growth: "Najszybciej rosnące (7 dni)",
  testers: "Najwięcej zgłoszeń do testów",
  rating: "Najwyżej oceniane",
  title: "Nazwa (A–Ż)",
};

async function load(): Promise<Row[]> {
  const [page, report] = await Promise.all([adminApi.innovations(), adminApi.innovationStatsReport()]);
  const byId = new Map(report.map((r) => [r.innovation_id, r]));
  return page.items.map((innovation) => ({ innovation, stats: byId.get(innovation.id) }));
}

function mock(): Row[] {
  const innovations = structuredClone(ADMIN_MOCK.innovations);
  const byId = new Map(mockInnovationStatsReport(innovations).map((r) => [r.innovation_id, r]));
  return innovations.map((innovation) => ({ innovation, stats: byId.get(innovation.id) }));
}

function sortValue(r: Row, sort: Sort): number {
  const s = r.stats;
  if (!s) return -Infinity;
  if (sort === "matches") return s.matches_total;
  if (sort === "growth") return s.matches_7d - s.matches_prev_7d;
  if (sort === "rating") return s.rating_avg ?? -1;
  return s.test_signups_applied;
}

// short reasons to look at an innovation now
function attention(r: Row): string[] {
  const s = r.stats;
  const out: string[] = [];
  if (r.innovation.status === "draft") out.push("Szkic: niewidoczna w czacie i bibliotece");
  if (s && s.test_signups_applied > 0)
    out.push(`${s.test_signups_applied} ${plural(s.test_signups_applied, "osoba czeka", "osoby czekają", "osób czeka")} na decyzję o testach`);
  if (s && s.rating_avg !== null && s.rating_avg < 3.5) out.push("Niska średnia ocen");
  if (r.innovation.status === "published" && s && s.matches_total === 0) out.push("Brak dopasowań: sprawdź opis i tagi");
  return out;
}

export function InnovationList() {
  const { data, setData, source, notice, setNotice } = useApiOrMock(load, mock);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<"" | "published" | "draft">("");
  const [area, setArea] = useState<"" | ChallengeArea>("");
  const [sort, setSort] = useState<Sort>("matches");
  const ids = { q: useId(), status: useId(), area: useId(), sort: useId() };

  if (!data) {
    return (
      <p role="status" className="py-space-lg text-body-lg text-on-surface-variant">
        Wczytuję innowacje i statystyki…
      </p>
    );
  }

  async function togglePublished(r: Row) {
    const publish = r.innovation.status !== "published";
    try {
      const updated =
        source === "api"
          ? await adminApi.setInnovationPublished(r.innovation.id, publish)
          : { ...r.innovation, status: publish ? ("published" as const) : ("draft" as const) };
      setData((rows) => rows && rows.map((x) => (x.innovation.id === updated.id ? { ...x, innovation: updated } : x)));
      setNotice(publish ? `Opublikowano: ${updated.title}.` : `Wycofano publikację: ${updated.title}.`);
    } catch {
      setNotice("Operacja nie powiodła się. Spróbuj ponownie.");
    }
  }

  const rows = data
    .filter((r) => !status || r.innovation.status === status)
    .filter((r) => !area || r.innovation.challenge_areas.includes(area))
    .filter((r) => !q || `${r.innovation.title} ${r.innovation.summary}`.toLowerCase().includes(q.toLowerCase()))
    .sort((a, b) =>
      sort === "title"
        ? a.innovation.title.localeCompare(b.innovation.title, "pl")
        : sortValue(b, sort) - sortValue(a, sort),
    );

  const stats = data.map((r) => r.stats).filter((s): s is InnovationStatsRow => !!s);
  const sum = (f: (s: InnovationStatsRow) => number) => stats.reduce((acc, s) => acc + f(s), 0);
  const ratingCount = sum((s) => s.rating_count);
  const ratingAvg = ratingCount ? sum((s) => (s.rating_avg ?? 0) * s.rating_count) / ratingCount : null;
  const published = data.filter((r) => r.innovation.status === "published").length;

  const kpis = [
    { icon: "verified", label: "Opublikowane innowacje", value: `${published} z ${data.length}` },
    {
      icon: "search_check",
      label: "Dopasowania w ostatnich 7 dniach",
      value: String(sum((s) => s.matches_7d)),
      trend: <Trend now={sum((s) => s.matches_7d)} before={sum((s) => s.matches_prev_7d)} />,
    },
    { icon: "groups", label: "Osoby objęte dopasowaniami", value: String(sum((s) => s.people_reached)) },
    { icon: "how_to_reg", label: "Zgłoszenia do testów czekające na decyzję", value: String(sum((s) => s.test_signups_applied)) },
    {
      icon: "star",
      label: `Średnia ocena (${ratingCount} ${plural(ratingCount, "ocena", "oceny", "ocen")})`,
      value: ratingAvg === null ? "–" : ratingAvg.toLocaleString("pl-PL", { maximumFractionDigits: 1 }),
    },
  ];

  return (
    <div className="flex flex-col gap-space-lg">
      <section aria-labelledby="podsumowanie-h" className={card}>
        <h2 id="podsumowanie-h" className={h2}>
          <Icon name="bar_chart" size={28} />
          Podsumowanie bazy innowacji
        </h2>
        <p className="text-body-md text-on-surface-variant">
          Dopasowanie = innowacja znalazła się w trzech propozycjach dla opisanego problemu.
          {source === "mock" && " Dane testowe."}
        </p>
        <p role="status" className="text-body-md font-semibold text-primary">
          {notice}
        </p>
        <ul className="mt-space-md grid grid-cols-2 gap-space-sm lg:grid-cols-5">
          {kpis.map((k) => (
            <li key={k.label} className="flex flex-col gap-1 rounded-xl bg-surface-container-low p-space-md hc-edge">
              <Icon name={k.icon} size={28} className="text-primary" />
              <span className="text-headline-md font-bold text-primary">{k.value}</span>
              <span className="text-body-md text-on-surface-variant">{k.label}</span>
              {k.trend}
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="lista-h" className={`${card} flex flex-col gap-space-md`}>
        <div className="flex flex-wrap items-center justify-between gap-space-sm">
          <h2 id="lista-h" className={h2}>
            <Icon name="verified" size={28} />
            Innowacje
          </h2>
          {source === "api" ? (
            <a href={adminApi.reportCsvUrl("innovations")} className={ghostBtn}>
              <Icon name="download" />
              Pobierz statystyki (CSV)
            </a>
          ) : (
            <span className="text-caption text-on-surface-variant">Eksport CSV dostępny po połączeniu z API</span>
          )}
        </div>

        <form role="search" aria-label="Filtruj innowacje" className="grid grid-cols-1 gap-space-sm sm:grid-cols-2 lg:grid-cols-4" onSubmit={(e) => e.preventDefault()}>
          <div className="flex flex-col gap-1">
            <label htmlFor={ids.q} className="text-label-md font-semibold text-primary">Szukaj</label>
            <input id={ids.q} type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="nazwa lub opis" className={field} />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor={ids.status} className="text-label-md font-semibold text-primary">Status</label>
            <select id={ids.status} value={status} onChange={(e) => setStatus(e.target.value as typeof status)} className={field}>
              <option value="">Wszystkie</option>
              <option value="published">Opublikowane</option>
              <option value="draft">Szkice</option>
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor={ids.area} className="text-label-md font-semibold text-primary">Obszar wyzwań</label>
            <select id={ids.area} value={area} onChange={(e) => setArea(e.target.value as typeof area)} className={field}>
              <option value="">Wszystkie obszary</option>
              {(Object.keys(AREA_LABEL) as ChallengeArea[]).map((a) => (
                <option key={a} value={a}>{AREA_LABEL[a]}</option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor={ids.sort} className="text-label-md font-semibold text-primary">Sortuj</label>
            <select id={ids.sort} value={sort} onChange={(e) => setSort(e.target.value as Sort)} className={field}>
              {(Object.keys(SORTS) as Sort[]).map((s) => (
                <option key={s} value={s}>{SORTS[s]}</option>
              ))}
            </select>
          </div>
        </form>

        <p aria-live="polite" className="text-body-md text-on-surface-variant">
          Wyświetlono {rows.length} z {data.length} innowacji.
        </p>

        <ul className="flex flex-col gap-space-md">
          {rows.map((r) => (
            <li key={r.innovation.id}>
              <InnovationRow row={r} source={source} onToggle={() => togglePublished(r)} />
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function InnovationRow({ row, source, onToggle }: { row: Row; source: Source; onToggle: () => void }) {
  const { innovation: i, stats: s } = row;
  const hId = `${i.id}-h`;
  const flags = attention(row);
  return (
    <article aria-labelledby={hId} className="flex flex-col gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
      <div className="flex flex-wrap items-center gap-2">
        <StatusBadge status={i.status} />
        {i.challenge_areas.map((a) => (
          <span key={a} className="rounded bg-surface-container-high px-2 py-0.5 text-caption text-primary">
            {AREA_LABEL[a]}
          </span>
        ))}
        <span className="text-caption text-on-surface-variant">
          • {i.readiness ? READINESS[i.readiness] : "etap nieznany"} • koszt wdrożenia: {i.cost_level ? COST[i.cost_level] : "nieznany"}
        </span>
      </div>
      <h3 id={hId} className="text-headline-sm font-semibold text-primary">
        <Link href={`/admin/innowacje/${encodeURIComponent(i.id)}`} className="underline-offset-4 hover:underline">
          {i.title}
        </Link>
      </h3>
      <p className="text-body-md text-on-surface-variant">{i.summary}</p>

      {s ? (
        <dl className="grid grid-cols-2 gap-space-sm sm:grid-cols-3 lg:grid-cols-6">
          <Stat label="Dopasowania">
            {s.matches_total}
          </Stat>
          <Stat label="Ostatnie 7 dni">
            {s.matches_7d} <Trend now={s.matches_7d} before={s.matches_prev_7d} />
          </Stat>
          <Stat label="Osoby objęte">{s.people_reached}</Stat>
          <Stat label="Gminy">{s.distinct_locations}</Stat>
          <Stat label="Testerzy">
            {s.test_signups_accepted} przyjętych
            <span className="block text-label-md font-normal text-on-surface-variant">{s.test_signups_applied} czeka</span>
          </Stat>
          <Stat label="Ocena">
            {s.rating_avg === null ? (
              "brak ocen"
            ) : (
              <>
                <span className="inline-flex items-center gap-1">
                  <Icon name="star" fill size={18} className="text-primary" />
                  {s.rating_avg.toLocaleString("pl-PL", { maximumFractionDigits: 1 })}
                  <span className="sr-only">na 5</span>
                </span>
                <span className="block text-label-md font-normal text-on-surface-variant">
                  {s.rating_count} {plural(s.rating_count, "ocena", "oceny", "ocen")}
                </span>
              </>
            )}
          </Stat>
        </dl>
      ) : (
        <p className="text-body-md text-on-surface-variant">Brak statystyk dla tej innowacji.</p>
      )}

      {flags.length > 0 && (
        <ul aria-label="Wymaga uwagi" className="flex flex-col gap-1">
          {flags.map((f) => (
            <li key={f} className="flex items-center gap-2 text-body-md text-on-surface">
              <Icon name="info" size={18} className="text-primary" />
              {f}
            </li>
          ))}
        </ul>
      )}

      <RatingsDropdown innovationId={i.id} title={i.title} count={s?.rating_count ?? 0} source={source} />

      <div className="flex flex-wrap items-center justify-between gap-space-sm">
        <span className="text-caption text-on-surface-variant">
          {s?.last_matched_at ? `Ostatnie dopasowanie: ${fmtDate(s.last_matched_at)}` : "Jeszcze nie dopasowano"}
        </span>
        <div className="flex flex-wrap gap-space-xs">
          <button type="button" className={ghostBtn} onClick={onToggle}>
            {i.status === "published" ? "Wycofaj publikację" : "Opublikuj"}
            <span className="sr-only">: {i.title}</span>
          </button>
          <Link href={`/admin/innowacje/${encodeURIComponent(i.id)}`} className={primaryBtn}>
            <Icon name="bar_chart" />
            Szczegółowe statystyki<span className="sr-only">: {i.title}</span>
          </Link>
        </div>
      </div>
    </article>
  );
}

function Stat({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-0.5 rounded-lg bg-surface-container-lowest p-space-sm hc-edge">
      <dt className="text-label-md text-on-surface-variant">{label}</dt>
      <dd className="text-body-lg font-bold text-on-surface">{children}</dd>
    </div>
  );
}

export function StatusBadge({ status }: { status: AdminInnovation["status"] }) {
  return status === "published" ? (
    <span className="flex items-center gap-1 rounded bg-tertiary-fixed px-2 py-0.5 text-caption font-semibold text-on-tertiary-fixed">
      <Icon name="verified" size={16} />
      Opublikowana
    </span>
  ) : (
    <span className="flex items-center gap-1 rounded bg-surface-container-highest px-2 py-0.5 text-caption font-semibold text-on-surface">
      <Icon name="schedule" size={16} />
      Szkic
    </span>
  );
}
