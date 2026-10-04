"use client";

import Link from "next/link";
import { useId, useState } from "react";
import { adminApi, type GrantApplication, type GrantApplicationStatus, type GrantCall } from "@/lib/api";
import { ADMIN_MOCK } from "@/lib/admin-mock";
import { Icon } from "@/components/Icon";
import { APPLICANT_LABELS } from "@/components/grant/labels";
import { card, field, fmtDate, h2, td, th } from "@/components/admin/styles";
import { useApiOrMock } from "@/components/admin/useApiOrMock";

export const APPLICATION_STATUS: Record<GrantApplicationStatus, string> = {
  submitted: "Wysłany",
  draft: "Szkic",
};

export function fmtPln(amount: string | number | null) {
  return amount == null || amount === ""
    ? "—"
    : Number(amount).toLocaleString("pl-PL", { style: "currency", currency: "PLN", maximumFractionDigits: 0 });
}

type Data = { applications: GrantApplication[]; calls: GrantCall[] };
type Filter = GrantApplicationStatus | "all";

// drafts are often abandoned half-way, so the default view is what applicants actually sent
export function GrantApplicationList() {
  const statusId = useId();
  const callId = useId();
  const [status, setStatus] = useState<Filter>("submitted");
  const [call, setCall] = useState("all");
  const { data, notice } = useApiOrMock<Data>(
    async () => {
      const [applications, calls] = await Promise.all([adminApi.grantApplications(), adminApi.grantCalls()]);
      return { applications, calls };
    },
    () => ({ applications: structuredClone(ADMIN_MOCK.grantApplications), calls: structuredClone(ADMIN_MOCK.grantCalls) }),
  );

  if (!data) {
    return (
      <p role="status" className="py-space-lg text-body-lg text-on-surface-variant">
        Wczytuję dane…
      </p>
    );
  }

  const callName = new Map(data.calls.map((c) => [c.id, c.name]));
  const inCall = data.applications.filter((a) => call === "all" || a.grant_call_id === call);
  const count = (f: Filter) => (f === "all" ? inCall.length : inCall.filter((a) => a.status === f).length);
  const shown = inCall
    .filter((a) => status === "all" || a.status === status)
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at));

  return (
    <section aria-labelledby="wnioski-h" className={`${card} flex flex-col gap-space-md`}>
      <div className="flex flex-col gap-1">
        <h2 id="wnioski-h" className={h2}>
          <Icon name="description" size={28} />
          Wnioski o grant
        </h2>
        <p className="text-body-md text-on-surface-variant">
          Formularze Zał. 3 wypełnione przez pomysłodawców w generatorze wniosków. Podgląd jest tylko do odczytu.
        </p>
      </div>

      <div className="flex flex-wrap gap-space-md">
        <div className="flex flex-col gap-1 sm:w-64">
          <label htmlFor={statusId} className="text-label-md font-semibold text-primary">
            Status
          </label>
          <select id={statusId} value={status} onChange={(e) => setStatus(e.target.value as Filter)} className={field}>
            {(Object.keys(APPLICATION_STATUS) as GrantApplicationStatus[]).map((s) => (
              <option key={s} value={s}>
                {APPLICATION_STATUS[s]} ({count(s)})
              </option>
            ))}
            <option value="all">Wszystkie ({count("all")})</option>
          </select>
        </div>
        <div className="flex flex-col gap-1 sm:w-80">
          <label htmlFor={callId} className="text-label-md font-semibold text-primary">
            Nabór
          </label>
          <select id={callId} value={call} onChange={(e) => setCall(e.target.value)} className={field}>
            <option value="all">Wszystkie nabory</option>
            {data.calls.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
        {notice}
      </p>

      {shown.length === 0 ? (
        <p className="text-body-lg text-on-surface-variant">Brak wniosków w tym widoku.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <caption className="sr-only">Wnioski o grant</caption>
            <thead>
              <tr>
                <th scope="col" className={th}>Tytuł</th>
                <th scope="col" className={th}>Wnioskodawca</th>
                <th scope="col" className={th}>Nabór</th>
                <th scope="col" className={th}>Kwota</th>
                <th scope="col" className={th}>Status</th>
                <th scope="col" className={th}>Ostatnia zmiana</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((a) => (
                <tr key={a.id}>
                  <td className={td}>
                    <Link
                      href={`/admin/wnioski/${encodeURIComponent(a.id)}`}
                      className="font-semibold text-primary underline underline-offset-4"
                    >
                      {a.title || "Bez tytułu"}
                    </Link>
                  </td>
                  <td className={td}>{APPLICANT_LABELS[a.applicant_type]}</td>
                  <td className={td}>{(a.grant_call_id && callName.get(a.grant_call_id)) || "—"}</td>
                  <td className={`${td} whitespace-nowrap`}>{fmtPln(a.grant_amount_pln)}</td>
                  <td className={td}>{APPLICATION_STATUS[a.status]}</td>
                  <td className={`${td} whitespace-nowrap`}>{fmtDate(a.updated_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
