"use client";

import { useEffect, useId, useState } from "react";
import { ApiError, adminApi, type AdminInnovation, type Idea, type IdeaStatus, type ProblemReport } from "@/lib/api";
import { ADMIN_MOCK, AREA_LABEL, type AdminData } from "@/lib/admin-mock";
import { Icon } from "@/components/Icon";

type Source = "loading" | "api" | "mock";

const IDEA_STATUS: Record<IdeaStatus, string> = {
  new: "Nowy",
  in_review: "W analizie",
  accepted: "Przyjęty",
  rejected: "Odrzucony",
};
const IDEA_STAGE: Record<Idea["stage"], string> = {
  concept: "Koncepcja",
  prototype: "Prototyp",
  pilot: "Pilotaż",
  running: "Działa",
};

const SECTIONS = [
  { id: "skrzynka", label: "Skrzynka" },
  { id: "zgloszenia", label: "Zgłoszenia problemów" },
  { id: "pomysly", label: "Pomysły" },
  { id: "innowacje", label: "Innowacje" },
  { id: "raporty", label: "Raporty" },
  { id: "nabory", label: "Nabory" },
];

const card = "rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge lg:p-space-lg";
const h2 = "flex items-center gap-2 text-headline-md font-semibold text-primary";
const primaryBtn =
  "flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-primary px-space-md text-label-lg font-semibold text-on-primary hover:bg-primary-container disabled:opacity-70";
const ghostBtn =
  "flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-surface-container-high px-space-md text-label-lg font-semibold text-primary hover:bg-surface-container-highest hc-edge";
const th = "border-b-2 border-outline px-3 py-2 text-left text-label-md font-semibold text-primary";
const td = "border-b border-surface-container-highest px-3 py-2 align-top text-body-md";

function fmtDate(iso: string) {
  return new Date(iso).toLocaleString("pl-PL", { dateStyle: "medium", timeStyle: "short" });
}

async function loadFromApi(): Promise<AdminData> {
  const [problemReports, ideas, innovations, trends, critical, gaps, grantCalls] = await Promise.all([
    adminApi.problemReports(),
    adminApi.ideas(),
    adminApi.innovations(),
    adminApi.trends(),
    adminApi.critical(),
    adminApi.gaps(),
    adminApi.grantCalls(),
  ]);
  return { problemReports, ideas, innovations: innovations.items, trends, critical, gaps, grantCalls };
}

function ReplyForm({ onSend, previous }: { onSend: (msg: string) => Promise<void>; previous?: string | null }) {
  const id = useId();
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <form
      className="flex flex-col gap-2"
      onSubmit={async (e) => {
        e.preventDefault();
        if (!msg.trim()) return;
        setBusy(true);
        await onSend(msg.trim());
        setBusy(false);
        setMsg("");
      }}
    >
      {previous && (
        <p className="rounded-lg bg-surface-container p-space-sm text-body-md">
          <strong className="text-primary">Odpowiedź ROPS: </strong>
          {previous}
        </p>
      )}
      <label htmlFor={id} className="text-label-md font-semibold text-primary">
        {previous ? "Zmień odpowiedź do autorów" : "Odpowiedz autorom (dostaną powiadomienie)"}
      </label>
      <textarea
        id={id}
        rows={2}
        value={msg}
        required
        onChange={(e) => setMsg(e.target.value)}
        className="rounded-lg border-[1.5px] border-outline bg-surface-container-lowest p-space-sm text-body-md text-on-surface"
      />
      <button type="submit" disabled={busy} className={`${primaryBtn} self-end`}>
        <Icon name="send" />
        Wyślij odpowiedź
      </button>
    </form>
  );
}

function AreaChip({ area }: { area: ProblemReport["challenge_area"] }) {
  return <span className="rounded bg-surface-container-high px-2 py-0.5 text-caption text-primary">{AREA_LABEL[area]}</span>;
}

export function AdminPanel() {
  const [source, setSource] = useState<Source>("loading");
  const [data, setData] = useState<AdminData | null>(null);
  const [status, setStatus] = useState("");

  useEffect(() => {
    loadFromApi()
      .then((d) => {
        setData(d);
        setSource("api");
      })
      .catch((err: unknown) => {
        setData(structuredClone(ADMIN_MOCK));
        setSource("mock");
        setStatus(
          err instanceof ApiError && err.status === 401
            ? "API wymaga logowania (ustaw ADMIN_AUTH_DISABLED=true przy DEBUG=true). Pokazuję lokalne dane testowe."
            : "Nie udało się połączyć z API. Pokazuję lokalne dane testowe.",
        );
      });
  }, []);

  // in api mode the server answers with the updated row; offline we patch locally
  async function mutate<T extends { id: string }>(
    key: "problemReports" | "ideas" | "innovations" | "grantCalls",
    id: string,
    call: () => Promise<T>,
    local: (item: T) => T,
    done: string,
  ) {
    try {
      const current = (data?.[key] as unknown as T[]).find((x) => x.id === id);
      if (!current) return;
      const updated = source === "api" ? await call() : local(current);
      setData((d) => d && { ...d, [key]: (d[key] as unknown as T[]).map((x) => (x.id === id ? updated : x)) });
      setStatus(done);
    } catch {
      setStatus("Operacja nie powiodła się. Spróbuj ponownie.");
    }
  }

  if (!data) {
    return (
      <div className="py-space-xl">
        <h1 className="text-headline-lg font-bold text-primary">Panel administratora</h1>
        <p role="status" className="mt-space-sm text-body-lg text-on-surface-variant">
          Wczytuję dane…
        </p>
      </div>
    );
  }

  const newIdeas = data.ideas.filter((i) => i.status === "new");
  const unanswered = data.problemReports.filter((r) => !r.admin_reply);
  const critical = data.problemReports.filter((r) => r.is_critical);
  const published = data.innovations.filter((i) => i.status === "published");

  const stats = [
    { label: "Nowe pomysły", value: newIdeas.length, icon: "lightbulb", href: "#pomysly" },
    { label: "Zgłoszenia bez odpowiedzi", value: unanswered.length, icon: "forum", href: "#zgloszenia" },
    { label: "Zgłoszenia krytyczne", value: critical.length, icon: "report_problem", href: "#zgloszenia" },
    { label: "Opublikowane innowacje", value: published.length, icon: "verified", href: "#innowacje" },
  ];

  return (
    <div className="flex flex-col gap-space-lg py-space-md">
      <header className={`${card} flex flex-col gap-space-sm`}>
        <p className="flex flex-wrap items-center gap-2">
          <span className="rounded bg-secondary-fixed px-2 py-0.5 text-caption font-bold text-on-secondary-fixed">tylko dla ROPS</span>
          <span className="rounded bg-tertiary-fixed px-2 py-0.5 text-caption font-semibold text-on-tertiary-fixed">
            {source === "api" ? "Dane z API (mocki backendu)" : "Tryb offline: lokalne dane testowe"}
          </span>
        </p>
        <h1 className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">Panel administratora</h1>
        <p className="text-body-lg text-on-surface-variant">
          Zgłoszenia mieszkańców, pomysły, baza innowacji i raporty trendów. Logowanie jest wyłączone na czas demonstracji.
        </p>
        <nav aria-label="Sekcje panelu">
          <ul className="flex flex-wrap gap-space-xs">
            {SECTIONS.map((s) => (
              <li key={s.id}>
                <a href={`#${s.id}`} className="flex min-h-11 items-center rounded-lg bg-surface-container px-space-sm text-label-md font-semibold text-primary underline-offset-4 hover:underline">
                  {s.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
        <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
          {status}
        </p>
      </header>

      <section id="skrzynka" aria-labelledby="skrzynka-h" className={card}>
        <h2 id="skrzynka-h" className={h2}>
          <Icon name="mail" size={28} />
          Skrzynka
        </h2>
        <ul className="mt-space-md grid grid-cols-1 gap-space-sm sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((s) => (
            <li key={s.label}>
              <a href={s.href} className="flex h-full items-center gap-space-sm rounded-xl bg-surface-container-low p-space-md hover:bg-surface-container-high hc-edge">
                <span className="flex size-12 shrink-0 items-center justify-center rounded-lg bg-surface-container text-primary">
                  <Icon name={s.icon} size={28} />
                </span>
                <span className="flex flex-col">
                  <span className="text-headline-md font-bold text-primary">{s.value}</span>
                  <span className="text-body-md text-on-surface-variant">{s.label}</span>
                </span>
              </a>
            </li>
          ))}
        </ul>
      </section>

      <section id="zgloszenia" aria-labelledby="zgloszenia-h" className={card}>
        <h2 id="zgloszenia-h" className={h2}>
          <Icon name="forum" size={28} />
          Zgłoszenia problemów
        </h2>
        <p className="text-body-md text-on-surface-variant">
          Odpowiedź trafia do autora i wszystkich osób, które kliknęły „Mnie też to dotyczy”.
        </p>
        <ul className="mt-space-md flex flex-col gap-space-md">
          {[...data.problemReports]
            .sort((a, b) => b.criticality_score - a.criticality_score)
            .map((r) => (
              <li key={r.id}>
                <article aria-labelledby={`${r.id}-text`} className="flex flex-col gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
                  <div className="flex flex-wrap items-center gap-2">
                    {r.is_critical && (
                      <span className="flex items-center gap-1 rounded bg-secondary px-2 py-0.5 text-caption font-bold text-on-secondary">
                        <Icon name="report_problem" size={16} />
                        Krytyczne
                      </span>
                    )}
                    <AreaChip area={r.challenge_area} />
                    <span className="flex items-center gap-1 text-caption text-on-surface-variant">
                      <Icon name="place" size={16} className="text-primary" />
                      {r.location}
                    </span>
                    <span className="text-caption text-on-surface-variant">• {fmtDate(r.created_at)}</span>
                  </div>
                  <p id={`${r.id}-text`} className="text-body-lg text-on-surface">
                    {r.text}
                  </p>
                  <p className="text-body-md text-on-surface-variant">
                    „Mnie też”: <strong className="text-on-surface">{r.support_count}</strong> • wskaźnik krytyczności:{" "}
                    <strong className="text-on-surface">{r.criticality_score.toFixed(1)}</strong>
                  </p>
                  <ReplyForm
                    previous={r.admin_reply}
                    onSend={(msg) =>
                      mutate<ProblemReport>(
                        "problemReports",
                        r.id,
                        () => adminApi.replyToProblemReport(r.id, msg),
                        (x) => ({ ...x, admin_reply: msg }),
                        "Odpowiedź wysłana do autorów zgłoszenia.",
                      )
                    }
                  />
                </article>
              </li>
            ))}
        </ul>
      </section>

      <section id="pomysly" aria-labelledby="pomysly-h" className={card}>
        <h2 id="pomysly-h" className={h2}>
          <Icon name="lightbulb" size={28} />
          Pomysły (Kreator pomysłów)
        </h2>
        <ul className="mt-space-md flex flex-col gap-space-md">
          {data.ideas.map((idea) => (
            <li key={idea.id}>
              <article aria-labelledby={`${idea.id}-h`} className="flex flex-col gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded bg-tertiary-fixed px-2 py-0.5 text-caption font-semibold text-on-tertiary-fixed">
                    {IDEA_STATUS[idea.status]}
                  </span>
                  <span className="rounded bg-surface-container-high px-2 py-0.5 text-caption text-primary">
                    Etap: {IDEA_STAGE[idea.stage]}
                  </span>
                  <span className="text-caption text-on-surface-variant">• {fmtDate(idea.created_at)}</span>
                </div>
                <h3 id={`${idea.id}-h`} className="text-headline-sm font-semibold text-primary">
                  {idea.summary}
                </h3>
                <dl className="grid grid-cols-1 gap-x-space-md gap-y-1 text-body-md sm:grid-cols-[max-content_1fr]">
                  <dt className="font-semibold text-primary">Problem</dt>
                  <dd>{idea.social_canvas.problem}</dd>
                  <dt className="font-semibold text-primary">Rozwiązanie</dt>
                  <dd>{idea.social_canvas.solution}</dd>
                  <dt className="font-semibold text-primary">Dla kogo</dt>
                  <dd>{idea.social_canvas.beneficiaries}</dd>
                  {idea.social_canvas.resources && (
                    <>
                      <dt className="font-semibold text-primary">Zasoby</dt>
                      <dd>{idea.social_canvas.resources}</dd>
                    </>
                  )}
                </dl>
                <form
                  className="flex flex-wrap items-end gap-space-xs"
                  onSubmit={(e) => {
                    e.preventDefault();
                    const next = new FormData(e.currentTarget).get("status") as IdeaStatus;
                    void mutate<Idea>(
                      "ideas",
                      idea.id,
                      () => adminApi.setIdeaStatus(idea.id, next),
                      (x) => ({ ...x, status: next }),
                      `Status pomysłu zmieniony na: ${IDEA_STATUS[next]}.`,
                    );
                  }}
                >
                  <div className="flex flex-col gap-1">
                    <label htmlFor={`${idea.id}-status`} className="text-label-md font-semibold text-primary">
                      Status
                    </label>
                    <select
                      id={`${idea.id}-status`}
                      name="status"
                      defaultValue={idea.status}
                      className="min-h-12 rounded-lg border-[1.5px] border-outline bg-surface-container-lowest px-space-sm text-body-md text-on-surface"
                    >
                      {Object.entries(IDEA_STATUS).map(([v, l]) => (
                        <option key={v} value={v}>
                          {l}
                        </option>
                      ))}
                    </select>
                  </div>
                  <button type="submit" className={ghostBtn}>
                    Zapisz status
                  </button>
                </form>
                <ReplyForm
                  previous={idea.admin_reply}
                  onSend={(msg) =>
                    mutate<Idea>(
                      "ideas",
                      idea.id,
                      () => adminApi.replyToIdea(idea.id, msg),
                      (x) => ({ ...x, admin_reply: msg }),
                      "Odpowiedź wysłana do autora pomysłu.",
                    )
                  }
                />
              </article>
            </li>
          ))}
        </ul>
      </section>

      <section id="innowacje" aria-labelledby="innowacje-h" className={card}>
        <h2 id="innowacje-h" className={h2}>
          <Icon name="verified" size={28} />
          Baza innowacji
        </h2>
        <div className="mt-space-md overflow-x-auto" tabIndex={0} role="region" aria-labelledby="innowacje-caption">
          <table className="w-full min-w-[640px] border-collapse">
            <caption id="innowacje-caption" className="pb-2 text-left text-body-md text-on-surface-variant">
              Innowacje w bazie ROPS. Tylko opublikowane pojawiają się w czacie i bibliotece.
            </caption>
            <thead>
              <tr>
                <th scope="col" className={th}>Nazwa</th>
                <th scope="col" className={th}>Obszar</th>
                <th scope="col" className={th}>Gotowość</th>
                <th scope="col" className={th}>Status</th>
                <th scope="col" className={th}>Akcja</th>
              </tr>
            </thead>
            <tbody>
              {data.innovations.map((i) => (
                <tr key={i.id}>
                  <th scope="row" className={`${td} text-left font-semibold text-primary`}>
                    {i.title}
                    <span className="block font-normal text-on-surface-variant">{i.summary}</span>
                  </th>
                  <td className={td}>{i.challenge_areas.map((a) => AREA_LABEL[a]).join(", ")}</td>
                  <td className={td}>{i.readiness}</td>
                  <td className={td}>{i.status === "published" ? "Opublikowana" : "Szkic"}</td>
                  <td className={td}>
                    <button
                      type="button"
                      className={ghostBtn}
                      onClick={() =>
                        mutate<AdminInnovation>(
                          "innovations",
                          i.id,
                          () => adminApi.setInnovationPublished(i.id, i.status !== "published"),
                          (x) => ({ ...x, status: x.status === "published" ? "draft" : "published" }),
                          i.status === "published" ? `Wycofano publikację: ${i.title}.` : `Opublikowano: ${i.title}.`,
                        )
                      }
                    >
                      {i.status === "published" ? "Wycofaj" : "Opublikuj"}
                      <span className="sr-only">: {i.title}</span>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section id="raporty" aria-labelledby="raporty-h" className={`${card} flex flex-col gap-space-lg`}>
        <div className="flex flex-col gap-1">
          <h2 id="raporty-h" className={h2}>
            <Icon name="psychology" size={28} />
            Raporty i trendy
          </h2>
          <p className="text-body-md text-on-surface-variant">
            Widoczne wyłącznie dla administratora. Krytyczność = liczba zgłoszeń × liczba różnych gmin × tempo wzrostu.
          </p>
        </div>

        {[
          {
            id: "critical",
            title: "Problemy krytyczne",
            head: ["Problem", "Obszar", "Gminy", "Wzrost 7 dni", "Wynik"],
            rows: data.critical.map((c) => [c.text, AREA_LABEL[c.challenge_area], c.distinct_locations, `×${c.growth_ratio_7d}`, c.score]),
          },
          {
            id: "trends",
            title: "Trendy tygodniowe",
            head: ["Tydzień od", "Obszar", "Gmina", "Zgłoszenia", "„Mnie też”"],
            rows: data.trends.map((t) => [t.week_start, AREA_LABEL[t.challenge_area], t.location, t.problem_reports, t.support_count]),
          },
          {
            id: "gaps",
            title: "Luki: problemy bez pasującej innowacji",
            head: ["Problem", "Obszar", "Najlepsze dopasowanie"],
            rows: data.gaps.map((g) => [g.text, AREA_LABEL[g.challenge_area], `${Math.round(g.best_match_similarity * 100)}%`]),
          },
        ].map((r) => (
          <div key={r.id} className="flex flex-col gap-space-xs">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <h3 id={`${r.id}-h`} className="text-headline-sm font-semibold text-primary">
                {r.title}
              </h3>
              {source === "api" ? (
                <a href={adminApi.reportCsvUrl(r.id as "critical" | "trends" | "gaps")} className={ghostBtn}>
                  Pobierz CSV<span className="sr-only">: {r.title}</span>
                </a>
              ) : (
                <span className="text-caption text-on-surface-variant">Eksport CSV dostępny po połączeniu z API</span>
              )}
            </div>
            <div className="overflow-x-auto" tabIndex={0} role="region" aria-labelledby={`${r.id}-h`}>
              <table className="w-full min-w-[560px] border-collapse">
                <thead>
                  <tr>
                    {r.head.map((h) => (
                      <th key={h} scope="col" className={th}>
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {r.rows.map((row, i) => (
                    <tr key={i}>
                      {row.map((cell, j) => (
                        <td key={j} className={td}>
                          {cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </section>

      <section id="nabory" aria-labelledby="nabory-h" className={card}>
        <h2 id="nabory-h" className={h2}>
          <Icon name="schedule" size={28} />
          Nabory grantowe
        </h2>
        <p className="text-body-md text-on-surface-variant">
          Otwarty nabór włącza generator wniosków w Kreatorze pomysłów.
        </p>
        <ul className="mt-space-md flex flex-col gap-space-sm">
          {data.grantCalls.map((c) => (
            <li key={c.id} className="flex flex-wrap items-center justify-between gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
              <div className="flex flex-col">
                <span className="text-body-lg font-bold text-primary">{c.name}</span>
                <span className="text-body-md text-on-surface-variant">
                  Termin: {new Date(c.deadline).toLocaleDateString("pl-PL", { dateStyle: "long" })} • Sekcje wniosku:{" "}
                  {c.sections.map((s) => s.title).join(", ")}
                </span>
              </div>
              <button
                type="button"
                role="switch"
                aria-checked={c.open}
                className={ghostBtn}
                onClick={() =>
                  mutate(
                    "grantCalls",
                    c.id,
                    () => adminApi.setGrantCallOpen(c.id, !c.open),
                    (x) => ({ ...x, open: !x.open }),
                    c.open ? `Zamknięto nabór: ${c.name}.` : `Otwarto nabór: ${c.name}.`,
                  )
                }
              >
                <Icon name={c.open ? "verified" : "close"} />
                Nabór otwarty: {c.open ? "tak" : "nie"}
              </button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
