"use client";

import Link from "next/link";
import { useState } from "react";
import {
  ApiError,
  adminApi,
  type AdminInnovation,
  type InnovationStats,
  type TestSignup,
  type TestSignupDecision,
} from "@/lib/api";
import { ADMIN_MOCK, mockInnovationStats } from "@/lib/admin-mock";
import { AREA_LABEL, COST, READINESS } from "@/lib/labels";
import { Icon } from "@/components/Icon";
import { BarList, Stars, Trend, WeeklyColumns, plural } from "@/components/admin/charts";
import { StatusBadge } from "@/components/admin/InnovationList";
import { card, fmtDate, ghostBtn, h2 } from "@/components/admin/styles";
import { RatingsDropdown } from "@/components/admin/RatingsDropdown";
import { useApiOrMock } from "@/components/admin/useApiOrMock";
import { SIGNUP_DONE, SIGNUP_STATUS, SignupActions, decideSignup } from "@/components/admin/TestSignupList";

interface Data {
  innovation: AdminInnovation | null;
  stats: InnovationStats | null;
  signups: TestSignup[];
}

// waiting for a decision first, then the newest
const SIGNUP_ORDER: Record<TestSignup["status"], number> = { applied: 0, accepted: 1, completed: 2, rated: 3, rejected: 4 };

type Counted = keyof InnovationStats["test_signups"];
const isCounted = (status: TestSignup["status"]): status is Counted =>
  status === "applied" || status === "accepted" || status === "rejected";

const LOCATION_NOTE = "mniej niż 5 zgłoszeń, nie pokazujemy";

export function InnovationStatsView({ id }: { id: string }) {
  const [busyId, setBusyId] = useState<string | null>(null);
  const { data, setData, source, notice, setNotice } = useApiOrMock<Data>(
    async () => {
      try {
        const [innovation, stats, signups] = await Promise.all([
          adminApi.innovation(id),
          adminApi.innovationStats(id),
          adminApi.testSignups(id),
        ]);
        return { innovation, stats, signups };
      } catch (err) {
        // a real 404 is an answer, not an outage
        if (err instanceof ApiError && err.status === 404) return { innovation: null, stats: null, signups: [] };
        throw err;
      }
    },
    () => {
      const innovation = ADMIN_MOCK.innovations.find((i) => i.id === id) ?? null;
      const stats = innovation && mockInnovationStats(id);
      return {
        innovation,
        stats,
        signups: structuredClone(ADMIN_MOCK.testSignups.filter((s) => s.innovation_id === id)),
      };
    },
  );

  if (!data) {
    return (
      <p role="status" className="py-space-lg text-body-lg text-on-surface-variant">
        Wczytuję statystyki innowacji…
      </p>
    );
  }

  const { innovation: i, stats: s } = data;
  if (!i || !s) {
    return (
      <section className={`${card} flex flex-col gap-space-sm`}>
        <h2 className="text-headline-lg-mobile font-bold text-primary">Nie znaleziono innowacji</h2>
        <p className="text-body-lg text-on-surface-variant">Innowacja o tym identyfikatorze nie istnieje w bazie.</p>
        <Link href="/admin" className={`${ghostBtn} self-start`}>
          <Icon name="arrow_back" />
          Wróć do listy innowacji
        </Link>
      </section>
    );
  }

  async function togglePublished(current: AdminInnovation) {
    const publish = current.status !== "published";
    try {
      const updated =
        source === "api"
          ? await adminApi.setInnovationPublished(current.id, publish)
          : { ...current, status: publish ? ("published" as const) : ("draft" as const) };
      setData((d) => d && { ...d, innovation: updated });
      setNotice(publish ? "Innowacja opublikowana: pojawi się w czacie i bibliotece." : "Publikacja wycofana.");
    } catch {
      setNotice("Operacja nie powiodła się. Spróbuj ponownie.");
    }
  }

  async function decide(signup: TestSignup, to: TestSignupDecision) {
    setBusyId(signup.id);
    try {
      const updated = await decideSignup(source, signup, to);
      setData((d) => {
        if (!d?.stats) return d;
        // keep the counters in step without refetching the stats
        const counts = { ...d.stats.test_signups };
        if (isCounted(signup.status)) counts[signup.status] -= 1;
        if (isCounted(updated.status)) counts[updated.status] += 1;
        return {
          ...d,
          stats: { ...d.stats, test_signups: counts },
          signups: d.signups.map((x) => (x.id === signup.id ? updated : x)),
        };
      });
      setNotice(SIGNUP_DONE[to]);
    } catch {
      setNotice("Operacja nie powiodła się. Spróbuj ponownie.");
    } finally {
      setBusyId(null);
    }
  }

  const signups = s.test_signups.applied + s.test_signups.accepted + s.test_signups.rejected;
  const kpis = [
    { icon: "search_check", label: "Dopasowania łącznie", value: s.matches_total },
    {
      icon: "schedule",
      label: "Dopasowania w ostatnich 7 dniach",
      value: s.matches_7d,
      extra: <Trend now={s.matches_7d} before={s.matches_prev_7d} />,
    },
    { icon: "groups", label: "Osoby objęte (zgłoszenia + „Mnie też”)", value: s.people_reached },
    { icon: "place", label: "Gminy, z których przyszły problemy", value: s.distinct_locations },
    { icon: "how_to_reg", label: "Zgłoszenia do testów", value: signups },
    {
      icon: "star",
      label: `Średnia ocena (${s.rating_count} ${plural(s.rating_count, "ocena", "oceny", "ocen")})`,
      value: s.rating_avg === null ? "–" : s.rating_avg.toLocaleString("pl-PL", { maximumFractionDigits: 1 }),
    },
  ];

  return (
    <div className="flex flex-col gap-space-lg">
      <nav aria-label="Ścieżka powrotu">
        <ol className="flex flex-wrap items-center gap-space-xs text-body-md text-on-surface-variant">
          <li>
            <Link href="/admin" className="flex min-h-12 items-center gap-1 rounded px-1 underline hover:text-primary">
              <Icon name="arrow_back" />
              Innowacje i statystyki
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

      <header className={`${card} flex flex-col gap-space-sm`}>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge status={i.status} />
          {i.challenge_areas.map((a) => (
            <span key={a} className="rounded bg-surface-container-high px-2 py-0.5 text-caption text-primary">
              {AREA_LABEL[a]}
            </span>
          ))}
          {source === "mock" && (
            <span className="rounded bg-tertiary-fixed px-2 py-0.5 text-caption font-semibold text-on-tertiary-fixed">Dane testowe</span>
          )}
        </div>
        <h2 className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">{i.title}</h2>
        <p className="text-body-lg text-on-surface-variant">{i.summary}</p>
        <dl className="grid grid-cols-1 gap-x-space-md gap-y-1 text-body-md sm:grid-cols-[max-content_1fr]">
          <dt className="font-semibold text-primary">Dla kogo</dt>
          <dd>{i.target_group.join(", ")}</dd>
          <dt className="font-semibold text-primary">Etap</dt>
          <dd>{i.readiness ? READINESS[i.readiness] : "–"}</dd>
          <dt className="font-semibold text-primary">Koszt wdrożenia</dt>
          <dd>{i.cost_level ? COST[i.cost_level] : "–"}</dd>
          {i.video_url && (
            <>
              <dt className="font-semibold text-primary">Film</dt>
              <dd>
                <a href={i.video_url} className="inline-flex min-h-12 items-center gap-1 underline hover:text-primary">
                  <Icon name="play_circle" />
                  Obejrzyj film o innowacji
                </a>
              </dd>
            </>
          )}
        </dl>
        <div className="flex flex-wrap items-center gap-space-sm">
          <button type="button" className={ghostBtn} onClick={() => togglePublished(i)}>
            {i.status === "published" ? "Wycofaj publikację" : "Opublikuj"}
          </button>
          <span className="text-body-md text-on-surface-variant">
            {s.last_matched_at ? `Ostatnie dopasowanie: ${fmtDate(s.last_matched_at)}` : "Jeszcze nie dopasowano"}
          </span>
        </div>
        <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
          {notice}
        </p>
      </header>

      <section aria-labelledby="kpi-h" className={card}>
        <h2 id="kpi-h" className={h2}>
          <Icon name="bar_chart" size={28} />
          Najważniejsze liczby
        </h2>
        <ul className="mt-space-md grid grid-cols-1 gap-space-sm sm:grid-cols-2 lg:grid-cols-3">
          {kpis.map((k) => (
            <li key={k.label} className="flex items-center gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
              <span className="flex size-12 shrink-0 items-center justify-center rounded-lg bg-surface-container text-primary">
                <Icon name={k.icon} size={28} />
              </span>
              <span className="flex flex-col">
                <span className="text-headline-md font-bold text-primary">{k.value}</span>
                <span className="text-body-md text-on-surface-variant">{k.label}</span>
                {k.extra}
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="tygodnie-h" className={card}>
        <h2 id="tygodnie-h" className={h2}>
          <Icon name="trending_up" size={28} />
          Dopasowania tydzień po tygodniu
        </h2>
        <p className="mb-space-md text-body-md text-on-surface-variant">
          Ile razy innowacja znalazła się w propozycjach dla opisanych problemów (ostatnie 6 tygodni).
        </p>
        <WeeklyColumns weeks={s.matches_by_week} caption={`Dopasowania tygodniowo: ${i.title}`} />
      </section>

      <div className="grid grid-cols-1 gap-space-lg lg:grid-cols-2">
        <section aria-labelledby="obszary-h" className={card}>
          <h2 id="obszary-h" className={h2}>
            <Icon name="psychology" size={28} />
            Na jakie problemy odpowiada
          </h2>
          <p className="mb-space-md text-body-md text-on-surface-variant">Obszary Mapy Wyzwań Społecznych dopasowanych zgłoszeń.</p>
          <BarList
            bars={s.matches_by_area.map((a) => ({ label: AREA_LABEL[a.challenge_area], value: a.matches }))}
            unit={(n) => `${n} ${plural(n, "dopasowanie", "dopasowania", "dopasowań")}`}
            empty="Brak dopasowań."
          />
        </section>

        <section aria-labelledby="gminy-h" className={card}>
          <h2 id="gminy-h" className={h2}>
            <Icon name="place" size={28} />
            Skąd przychodzą problemy
          </h2>
          <p className="mb-space-md text-body-md text-on-surface-variant">Gminy z mniej niż 5 zgłoszeniami są ukryte (ochrona prywatności).</p>
          <BarList
            bars={s.matches_by_location.map((l) => ({ label: l.location, value: l.matches, note: LOCATION_NOTE }))}
            unit={(n) => `${n} ${plural(n, "dopasowanie", "dopasowania", "dopasowań")}`}
            empty="Brak dopasowań."
          />
        </section>
      </div>

      <section aria-labelledby="tester-h" className={`${card} flex flex-col gap-space-md`}>
        <h2 id="tester-h" className={h2}>
          <Icon name="how_to_reg" size={28} />
          Tester innowacji
        </h2>
        <div className="grid grid-cols-1 gap-space-lg lg:grid-cols-2">
          <div className="flex flex-col gap-space-sm">
            <h3 className="text-headline-sm font-semibold text-primary">Zgłoszenia do testów</h3>
            <dl className="grid grid-cols-3 gap-space-sm">
              {[
                ["Czeka na decyzję", s.test_signups.applied],
                ["Przyjęte", s.test_signups.accepted],
                ["Odrzucone", s.test_signups.rejected],
              ].map(([label, n]) => (
                <div key={label} className="flex flex-col rounded-lg bg-surface-container-low p-space-sm hc-edge">
                  <dt className="text-label-md text-on-surface-variant">{label}</dt>
                  <dd className="text-headline-md font-bold text-primary">{n}</dd>
                </div>
              ))}
            </dl>
            {data.signups.length === 0 ? (
              <p className="text-body-md text-on-surface-variant">Nikt jeszcze nie zgłosił się do testów.</p>
            ) : (
              <ul
                aria-label="Osoby zgłoszone do testów"
                tabIndex={0}
                className="flex max-h-96 flex-col gap-space-sm overflow-y-auto rounded-lg pr-1"
              >
                {[...data.signups]
                  .sort((a, b) => SIGNUP_ORDER[a.status] - SIGNUP_ORDER[b.status] || b.created_at.localeCompare(a.created_at))
                  .map((sg) => (
                    <li key={sg.id} className="flex flex-col gap-space-xs rounded-xl bg-surface-container-low p-space-sm hc-edge">
                      <span className="flex flex-wrap items-center gap-2 text-caption text-on-surface-variant">
                        <span className="rounded bg-tertiary-fixed px-2 py-0.5 font-semibold text-on-tertiary-fixed">
                          {SIGNUP_STATUS[sg.status]}
                        </span>
                        • {fmtDate(sg.created_at)}
                      </span>
                      <a href={`mailto:${sg.email}`} className="break-all text-body-md underline hover:text-primary">
                        {sg.email}
                      </a>
                      <SignupActions signup={sg} busy={busyId === sg.id} onDecide={(to) => void decide(sg, to)} />
                    </li>
                  ))}
              </ul>
            )}
            <Link href="/admin/testerzy" className={`${ghostBtn} self-start`}>
              Wszystkie zgłoszenia do testów
            </Link>
          </div>
          <div className="flex flex-col gap-space-sm">
            <h3 className="text-headline-sm font-semibold text-primary">Oceny</h3>
            <Stars avg={s.rating_avg} count={s.rating_count} />
            <BarList
              bars={[5, 4, 3, 2, 1].map((star) => ({
                label: `${star} ${plural(star, "gwiazdka", "gwiazdki", "gwiazdek")}`,
                value: s.rating_distribution[star - 1],
              }))}
              unit={(n) => `${n} ${plural(n, "ocena", "oceny", "ocen")}`}
              empty="Brak ocen."
            />
            <RatingsDropdown innovationId={i.id} title={i.title} count={s.rating_count} source={source} />
          </div>
        </div>
      </section>

      <div className="grid grid-cols-1 gap-space-lg lg:grid-cols-2">
        <section aria-labelledby="opinie-h" className={card}>
          <h2 id="opinie-h" className={h2}>
            <Icon name="chat_bubble" size={28} />
            Opinie i propozycje usprawnień
          </h2>
          {s.recent_comments.length === 0 ? (
            <p className="mt-space-sm text-body-md text-on-surface-variant">Brak opinii.</p>
          ) : (
            <ul className="mt-space-md flex flex-col gap-space-sm">
              {s.recent_comments.map((c) => (
                <li key={c.created_at + c.comment} className="flex flex-col gap-1 rounded-xl bg-surface-container-low p-space-md hc-edge">
                  <span className="flex flex-wrap items-center gap-2 text-caption text-on-surface-variant">
                    <span className="inline-flex items-center gap-1">
                      <Icon name="star" fill size={16} className="text-primary" />
                      {c.rating} / 5
                    </span>
                    • {fmtDate(c.created_at)}
                  </span>
                  <p className="text-body-md text-on-surface">{c.comment}</p>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section aria-labelledby="problemy-h" className={card}>
          <h2 id="problemy-h" className={h2}>
            <Icon name="forum" size={28} />
            Ostatnie dopasowane problemy
          </h2>
          {s.recent_problem_reports.length === 0 ? (
            <p className="mt-space-sm text-body-md text-on-surface-variant">Jeszcze nikt nie opisał pasującego problemu.</p>
          ) : (
            <ul className="mt-space-md flex flex-col gap-space-sm">
              {s.recent_problem_reports.map((r) => (
                <li key={r.id} className="flex flex-col gap-1 rounded-xl bg-surface-container-low p-space-md hc-edge">
                  <span className="flex flex-wrap items-center gap-2 text-caption text-on-surface-variant">
                    <span className="rounded bg-surface-container-high px-2 py-0.5 text-primary">{AREA_LABEL[r.challenge_area]}</span>
                    <span className="inline-flex items-center gap-1">
                      <Icon name="place" size={16} className="text-primary" />
                      {r.location}
                    </span>
                    • {fmtDate(r.created_at)}
                  </span>
                  <p className="text-body-md text-on-surface">{r.text}</p>
                  <span className="text-caption text-on-surface-variant">„Mnie też”: {r.support_count}</span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
