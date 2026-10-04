"use client";

import Link from "next/link";
import { useId, useState } from "react";
import { adminApi, type TestSignup, type TestSignupDecision, type TestSignupStatus } from "@/lib/api";
import { ADMIN_MOCK } from "@/lib/admin-mock";
import { Icon } from "@/components/Icon";
import { card, field, fmtDate, ghostBtn, h2, primaryBtn } from "@/components/admin/styles";
import { useApiOrMock, type Source } from "@/components/admin/useApiOrMock";

export const SIGNUP_STATUS: Record<TestSignupStatus, string> = {
  applied: "Nowe",
  accepted: "Przyjęte",
  completed: "Test zakończony",
  rated: "Ocenione",
  rejected: "Odrzucone",
};

// what the admin can do next; each decision mails the tester
const ACTIONS: Record<TestSignupStatus, { to: TestSignupDecision; label: string; icon: string; primary?: boolean }[]> = {
  applied: [
    { to: "accepted", label: "Przyjmij do testów", icon: "verified", primary: true },
    { to: "rejected", label: "Odrzuć", icon: "close" },
  ],
  accepted: [{ to: "completed", label: "Oznacz test jako zakończony", icon: "how_to_reg", primary: true }],
  completed: [],
  rated: [],
  rejected: [],
};

export const SIGNUP_DONE: Record<TestSignupDecision, string> = {
  accepted: "Przyjęto zgłoszenie. Tester dostał e-mail z zaproszeniem do testów i linkiem do oceny.",
  rejected: "Odrzucono zgłoszenie. Tester dostał e-mail z podziękowaniem.",
  completed: "Oznaczono test jako zakończony. Tester dostał e-mail z prośbą o ocenę.",
};

const NOTE: Partial<Record<TestSignupStatus, string>> = {
  completed: "Czekamy na ocenę testera z e-maila.",
  rated: "Tester ocenił rozwiązanie. Ocena jest w statystykach innowacji.",
};

// in api mode the server answers with the updated row; offline we patch locally
export function decideSignup(source: Source, s: TestSignup, to: TestSignupDecision): Promise<TestSignup> {
  return source === "api" ? adminApi.setTestSignupStatus(s.id, to) : Promise.resolve({ ...s, status: to });
}

export function SignupActions({
  signup,
  busy,
  onDecide,
}: {
  signup: TestSignup;
  busy: boolean;
  onDecide: (to: TestSignupDecision) => void;
}) {
  const actions = ACTIONS[signup.status];
  if (actions.length === 0) return null;
  return (
    <div className="flex flex-wrap justify-end gap-space-xs">
      {actions.map((a) => (
        <button
          key={a.to}
          type="button"
          disabled={busy}
          onClick={() => onDecide(a.to)}
          className={a.primary ? primaryBtn : ghostBtn}
        >
          <Icon name={a.icon} />
          {a.label}
          <span className="sr-only">: {signup.innovation_title}, {signup.email}</span>
        </button>
      ))}
    </div>
  );
}

type Filter = TestSignupStatus | "all";

export function TestSignupList() {
  const filterId = useId();
  const [filter, setFilter] = useState<Filter>("applied");
  const [busyId, setBusyId] = useState<string | null>(null);
  const { data, setData, source, notice, setNotice } = useApiOrMock<TestSignup[]>(() => adminApi.testSignups(), () =>
    structuredClone(ADMIN_MOCK.testSignups),
  );

  async function decide(s: TestSignup, to: TestSignupDecision) {
    setBusyId(s.id);
    try {
      const updated = await decideSignup(source, s, to);
      setData((d) => d && d.map((x) => (x.id === s.id ? updated : x)));
      setNotice(SIGNUP_DONE[to]);
    } catch {
      setNotice("Operacja nie powiodła się. Spróbuj ponownie.");
    } finally {
      setBusyId(null);
    }
  }

  if (!data) {
    return (
      <p role="status" className="py-space-lg text-body-lg text-on-surface-variant">
        Wczytuję dane…
      </p>
    );
  }

  const count = (f: Filter) => (f === "all" ? data.length : data.filter((s) => s.status === f).length);
  const shown = [...data]
    .filter((s) => filter === "all" || s.status === filter)
    .sort((a, b) => b.created_at.localeCompare(a.created_at));

  return (
    <section aria-labelledby="testerzy-h" className={`${card} flex flex-col gap-space-md`}>
      <div className="flex flex-col gap-1">
        <h2 id="testerzy-h" className={h2}>
          <Icon name="how_to_reg" size={28} />
          Zgłoszenia do testów
        </h2>
        <p className="text-body-md text-on-surface-variant">
          Każda decyzja wysyła e-mail do osoby zgłaszającej. Po zakończeniu testu tester dostaje link do oceny
          rozwiązania.
        </p>
      </div>

      <div className="flex flex-col gap-1 sm:max-w-xs">
        <label htmlFor={filterId} className="text-label-md font-semibold text-primary">
          Pokaż zgłoszenia
        </label>
        <select id={filterId} value={filter} onChange={(e) => setFilter(e.target.value as Filter)} className={field}>
          {(Object.keys(SIGNUP_STATUS) as TestSignupStatus[]).map((s) => (
            <option key={s} value={s}>
              {SIGNUP_STATUS[s]} ({count(s)})
            </option>
          ))}
          <option value="all">Wszystkie ({count("all")})</option>
        </select>
      </div>

      <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
        {notice}
      </p>

      {shown.length === 0 ? (
        <p className="text-body-lg text-on-surface-variant">Brak zgłoszeń w tym widoku.</p>
      ) : (
        <ul className="flex flex-col gap-space-md">
          {shown.map((s) => (
            <li key={s.id}>
              <article
                aria-labelledby={`${s.id}-h`}
                className="flex flex-col gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge"
              >
                <div className="flex flex-wrap items-center gap-2">
                  <span className="rounded bg-tertiary-fixed px-2 py-0.5 text-caption font-semibold text-on-tertiary-fixed">
                    {SIGNUP_STATUS[s.status]}
                  </span>
                  <span className="rounded bg-surface-container-high px-2 py-0.5 text-caption text-primary">
                    {s.problem_report_id ? "Z czatu" : "Ze strony innowacji"}
                  </span>
                  <span className="text-caption text-on-surface-variant">• {fmtDate(s.created_at)}</span>
                </div>
                <h3 id={`${s.id}-h`} className="text-headline-sm font-semibold text-primary">
                  <Link href={`/admin/innowacje/${encodeURIComponent(s.innovation_id)}`} className="underline-offset-4 hover:underline">
                    {s.innovation_title}
                  </Link>
                </h3>
                <dl className="grid grid-cols-1 gap-x-space-md gap-y-1 text-body-md sm:grid-cols-[max-content_1fr]">
                  <dt className="font-semibold text-primary">E-mail</dt>
                  <dd>
                    <a href={`mailto:${s.email}`} className="break-all underline hover:text-primary">
                      {s.email}
                    </a>
                  </dd>
                </dl>
                {NOTE[s.status] && <p className="text-body-md text-on-surface-variant">{NOTE[s.status]}</p>}
                <SignupActions signup={s} busy={busyId === s.id} onDecide={(to) => void decide(s, to)} />
              </article>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
