"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ApiError, api, type LibraryInnovation, type Thread } from "@/lib/api";
import { CARETAKER, SAMPLE_PDF_URL, findInnovation, type DemoInnovation } from "@/lib/demo-data";
import { AREA_LABEL, COST, READINESS } from "@/lib/labels";
import { Icon } from "@/components/Icon";
import { ActionBar } from "@/components/innovation/ActionBar";
import { Community } from "@/components/innovation/Community";

const SITE = "Małopolski Hub Innowacji Społecznych";
const card = "flex flex-col gap-space-md rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge lg:p-space-lg";

// one shape for the api record and the offline demo entry
interface View {
  id: string;
  title: string;
  tags: string[];
  author?: string;
  partner?: string;
  recommended: boolean;
  problem?: string;
  solution: string;
  results?: string;
  deployedIn?: string;
  details: { label: string; value: string }[];
  videoUrl?: string | null;
  pdfUrl: string;
}

type State =
  | { kind: "loading" }
  | { kind: "api"; view: View }
  | { kind: "demo"; view: View; threads: Thread[] }
  | { kind: "missing" }
  | { kind: "error" };

function fromApi(i: LibraryInnovation): View {
  const details = [
    { label: "Dla kogo", value: (i.target_group ?? []).join(", ") },
    { label: "Etap", value: i.readiness ? READINESS[i.readiness] : "" },
    { label: "Koszt wdrożenia", value: i.cost_level ? COST[i.cost_level] : "" },
    {
      label: "Ocena",
      value:
        i.rating_avg === null
          ? ""
          : `${i.rating_avg.toLocaleString("pl-PL", { maximumFractionDigits: 1 })} na 5 (liczba ocen: ${i.rating_count})`,
    },
  ].filter((d) => d.value);
  return {
    id: i.id,
    title: i.title,
    tags: i.challenge_areas.map((a) => AREA_LABEL[a]),
    author: i.innovator || undefined,
    recommended: false,
    problem: i.problem || undefined,
    solution: i.summary,
    deployedIn: i.city || undefined,
    details,
    // the backend has no video_url; films are linked through page_url
    videoUrl: i.video_url || i.page_url,
    pdfUrl: i.has_pdf ? api.innovationPdfUrl(i.id) : SAMPLE_PDF_URL,
  };
}

function fromDemo(d: DemoInnovation): View {
  return {
    id: d.id,
    title: d.fullTitle,
    tags: d.tags,
    author: d.author,
    partner: d.partner,
    recommended: d.recommended,
    problem: d.problem,
    solution: d.solution,
    results: d.results,
    deployedIn: d.deployedIn,
    details: [],
    pdfUrl: SAMPLE_PDF_URL,
  };
}

export function InnovationDetail({ id }: { id: string }) {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let live = true;
    api
      .innovation(id)
      .then((i) => live && setState({ kind: "api", view: fromApi(i) }))
      .catch((err: unknown) => {
        if (!live) return;
        // a 404 is an answer (unknown or unpublished), not an outage
        if (err instanceof ApiError && err.status === 404) return setState({ kind: "missing" });
        const demo = findInnovation(id);
        setState(demo ? { kind: "demo", view: fromDemo(demo), threads: demo.threads } : { kind: "error" });
      });
    return () => {
      live = false;
    };
  }, [id]);

  const title = state.kind === "api" || state.kind === "demo" ? state.view.title : state.kind === "missing" ? "Nie znaleziono innowacji" : null;
  useEffect(() => {
    if (title) document.title = `${title} – ${SITE}`;
  }, [title]);

  if (state.kind === "loading") {
    return (
      <p role="status" className="py-space-xl text-body-lg text-on-surface-variant">
        Wczytuję innowację…
      </p>
    );
  }

  if (state.kind === "missing" || state.kind === "error") {
    return (
      <div className="flex flex-col gap-space-sm py-space-xl">
        <h1 className="text-headline-lg font-bold text-primary">
          {state.kind === "missing" ? "Nie znaleziono innowacji" : "Nie udało się wczytać innowacji"}
        </h1>
        <p role="status" className="text-body-lg text-on-surface-variant">
          {state.kind === "missing"
            ? "Ta innowacja nie istnieje albo nie jest jeszcze opublikowana."
            : "Serwer jest chwilowo niedostępny. Odśwież stronę za chwilę."}
        </p>
        <p>
          <Link href="/innowacje" className="flex min-h-12 items-center text-body-lg font-bold text-primary underline">
            Wróć do biblioteki innowacji
          </Link>
        </p>
      </div>
    );
  }

  const i = state.view;
  const facts = [
    ...(i.problem ? [{ icon: "report_problem", tone: "text-secondary", label: "Zdiagnozowany problem", text: i.problem }] : []),
    { icon: "lightbulb", tone: "text-tertiary-strong", label: "Wypracowane rozwiązanie", text: i.solution },
    ...(i.results
      ? [{ icon: "sentiment_very_satisfied", tone: "text-primary", label: "Rezultaty i korzyści", text: i.results }]
      : []),
  ];

  return (
    <div className="flex flex-col pb-space-md">
      <nav aria-label="Ścieżka powrotu" className="py-space-md">
        <ol className="flex flex-wrap items-center gap-space-xs text-body-md text-on-surface-variant">
          <li>
            <Link href="/" className="flex min-h-12 items-center gap-1 rounded px-1 underline hover:text-primary">
              <Icon name="home" />
              Strona główna
            </Link>
          </li>
          <li aria-hidden="true" className="flex items-center">
            <Icon name="chevron_right" size={18} />
          </li>
          <li>
            <Link href="/innowacje" className="flex min-h-12 items-center rounded px-1 underline hover:text-primary">
              Biblioteka innowacji
            </Link>
          </li>
          <li aria-hidden="true" className="flex items-center">
            <Icon name="chevron_right" size={18} />
          </li>
          <li aria-current="page" className="flex min-h-12 items-center font-bold text-primary">
            {i.title}
          </li>
        </ol>
      </nav>

      {state.kind === "demo" && (
        <p className="mb-space-md flex items-start gap-2 rounded-lg bg-surface-container p-space-sm text-caption text-on-surface-variant">
          <Icon name="info" size={18} className="mt-0.5 text-primary" />
          <span>Tryb demonstracyjny: serwer jest niedostępny, opis pochodzi z przykładowej bazy innowacji.</span>
        </p>
      )}

      <header className={`${card} mb-space-lg`}>
        {(i.recommended || i.tags.length > 0) && (
          <ul className="flex flex-wrap items-center gap-space-xs" aria-label="Oznaczenia">
            {i.recommended && (
              <li className="flex items-center gap-1.5 rounded-lg bg-tertiary-fixed px-3 py-1.5 text-label-md font-semibold text-on-tertiary-fixed">
                <Icon name="verified" size={18} />
                Innowacja przetestowana i rekomendowana
              </li>
            )}
            {i.tags.map((t, n) => (
              <li key={t} className="flex items-center gap-1 rounded-lg bg-surface-container-high px-3 py-1.5 text-label-md font-semibold text-primary">
                <Icon name={n === 0 ? "groups" : "holiday_village"} size={18} />
                {t}
              </li>
            ))}
          </ul>
        )}
        <div className="flex flex-col gap-2">
          <h1 className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">{i.title}</h1>
          {i.author && (
            <p className="flex items-start gap-2 text-body-lg text-on-surface-variant">
              <Icon name="account_balance" size={22} className="mt-1 text-primary" />
              <span>
                Autorstwo: <strong className="text-on-surface">{i.author}</strong>
                {i.partner && (
                  <>
                    {" "}
                    we współpracy z <strong className="text-on-surface">{i.partner}</strong>
                  </>
                )}
              </span>
            </p>
          )}
        </div>
        <ActionBar innovationId={i.id} pdfUrl={i.pdfUrl} title={i.title} />
      </header>

      <div className="grid grid-cols-1 items-start gap-space-lg lg:grid-cols-12">
        {/* on phones the wrapper dissolves so the contact box comes before the forum */}
        <div className="contents lg:col-span-8 lg:flex lg:flex-col lg:gap-space-lg">
          <section aria-labelledby="opis-heading" className={card}>
            <h2 id="opis-heading" className="flex items-center gap-2 text-headline-md font-semibold text-primary">
              <Icon name="info" size={28} />
              Opis innowacji i założenia społeczne
            </h2>
            <div className="grid grid-cols-1 gap-space-md">
              {facts.map((f) => (
                <div key={f.label} className="flex flex-col gap-2 rounded-xl bg-surface-container-low p-space-md hc-edge">
                  <h3 className="flex items-center gap-1.5 text-label-lg font-semibold text-primary">
                    <Icon name={f.icon} className={f.tone} />
                    {f.label}
                  </h3>
                  <p className="text-body-md text-on-surface-variant">{f.text}</p>
                </div>
              ))}
            </div>
            {(i.details.length > 0 || i.videoUrl) && (
              <dl className="grid grid-cols-1 gap-x-space-md gap-y-1 text-body-md sm:grid-cols-[max-content_1fr]">
                {i.details.map((d) => (
                  <div key={d.label} className="contents">
                    <dt className="font-semibold text-primary">{d.label}</dt>
                    <dd className="text-on-surface-variant">{d.value}</dd>
                  </div>
                ))}
                {i.videoUrl && (
                  <>
                    <dt className="font-semibold text-primary">Strona lub film</dt>
                    <dd>
                      <a href={i.videoUrl} className="inline-flex min-h-12 items-center gap-1 text-primary underline">
                        <Icon name="arrow_forward" />
                        Zobacz stronę lub film o innowacji
                      </a>
                    </dd>
                  </>
                )}
              </dl>
            )}
            {i.deployedIn && (
              <p className="flex items-center gap-2 text-body-md text-on-surface-variant">
                <Icon name="place" className="text-primary" />
                Dotychczasowe wdrożenia: {i.deployedIn}
              </p>
            )}
          </section>

          <div className="order-last lg:order-none">
            <Community innovationId={i.id} demoThreads={state.kind === "demo" ? state.threads : undefined} />
          </div>
        </div>

        <aside aria-label="Kontakt" className="flex flex-col gap-space-lg lg:col-span-4">
          <section aria-labelledby="opiekun-heading" className={card}>
            <h2 id="opiekun-heading" className="flex items-center gap-2 text-headline-sm font-semibold text-primary">
              <Icon name="support_agent" size={24} />
              Dedykowany opiekun w ROPS
            </h2>
            <div className="flex items-center gap-3">
              <span aria-hidden="true" className="flex size-14 shrink-0 items-center justify-center rounded-full bg-surface-container-high">
                <Icon name="face_6" size={36} className="text-primary" />
              </span>
              <span className="flex flex-col">
                <span className="text-body-lg font-bold text-primary">{CARETAKER.name}</span>
                <span className="text-caption text-on-surface-variant">{CARETAKER.role}</span>
              </span>
            </div>
            <ul className="flex flex-col gap-2 text-body-md">
              <li>
                <a href={CARETAKER.phoneHref} className="flex min-h-12 items-center gap-3 rounded-lg bg-surface-container-low px-3 text-primary hover:bg-surface-container hc-edge">
                  <Icon name="call" />
                  <span>
                    <span className="sr-only">Telefon: </span>
                    {CARETAKER.phone}
                  </span>
                </a>
              </li>
              <li>
                <a href={`mailto:${CARETAKER.email}`} className="flex min-h-12 items-center gap-3 rounded-lg bg-surface-container-low px-3 text-primary hover:bg-surface-container hc-edge">
                  <Icon name="mail" />
                  <span>
                    <span className="sr-only">E-mail: </span>
                    {CARETAKER.email}
                  </span>
                </a>
              </li>
              <li className="flex items-start gap-3 rounded-lg bg-surface-container-low p-3 text-on-surface-variant hc-edge">
                <Icon name="schedule" className="mt-0.5 text-primary" />
                <span className="flex flex-col">
                  <span className="text-label-md font-semibold text-primary">Dyżur konsultacyjny stacjonarny:</span>
                  <span className="text-caption">
                    {CARETAKER.hours}
                    <br />
                    {CARETAKER.place}
                  </span>
                </span>
              </li>
            </ul>
          </section>
        </aside>
      </div>
    </div>
  );
}
