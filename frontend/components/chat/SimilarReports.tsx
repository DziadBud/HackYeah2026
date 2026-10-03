"use client";

import { useState } from "react";
import { api, type SimilarProblemReport } from "@/lib/api";
import { Icon } from "@/components/Icon";

// similar problem reports from /match; "mnie też" bumps support_count, which feeds the admin's criticality
export function SimilarReports({ reports }: { reports: SimilarProblemReport[] }) {
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [supported, setSupported] = useState<Set<string>>(new Set());
  const [busy, setBusy] = useState<string | null>(null);
  const [status, setStatus] = useState("");

  async function support(id: string) {
    setBusy(id);
    try {
      const { support_count } = await api.supportProblemReport(id);
      setCounts((c) => ({ ...c, [id]: support_count }));
      setSupported((s) => new Set(s).add(id));
      setStatus("Dziękujemy! Zapisaliśmy, że ten problem dotyczy także Ciebie.");
    } catch {
      setStatus("Nie udało się zapisać. Spróbuj ponownie za chwilę.");
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="flex flex-col gap-space-sm border-t border-surface-container-highest pt-space-md">
      <h3 className="text-body-lg font-bold text-primary">Podobne problemy zgłosili też inni</h3>
      <p className="text-body-md text-on-surface-variant">
        Jeśli to także Twój problem, kliknij „Mnie też”. Dzięki temu ROPS widzi, jak wiele osób go dotyczy.
      </p>
      <ul className="flex flex-col gap-space-sm">
        {reports.map((r) => {
          const done = supported.has(r.id);
          const count = counts[r.id] ?? r.support_count;
          return (
            <li key={r.id} className="flex flex-col gap-space-xs rounded-xl bg-surface-container-low p-space-sm hc-edge">
              <p className="text-body-md text-on-surface">{r.text}</p>
              {r.admin_reply && (
                <p className="rounded-lg bg-surface-container p-space-sm text-body-md">
                  <strong className="text-primary">Odpowiedź ROPS: </strong>
                  {r.admin_reply}
                </p>
              )}
              <div className="flex flex-wrap items-center justify-between gap-space-xs">
                <span className="flex items-center gap-1 text-caption text-on-surface-variant">
                  {r.city && (
                    <>
                      <Icon name="place" size={18} className="text-primary" />
                      {r.city} •{" "}
                    </>
                  )}
                  „Mnie też”: {count}
                </span>
                <button
                  type="button"
                  aria-pressed={done}
                  disabled={done || busy === r.id}
                  onClick={() => support(r.id)}
                  className="flex min-h-12 items-center gap-1.5 rounded-lg bg-surface-container-lowest px-3 text-label-md font-semibold text-primary hover:bg-surface-container disabled:cursor-default aria-pressed:bg-secondary-fixed aria-pressed:text-on-secondary-fixed hc-edge"
                >
                  <Icon name="thumb_up" size={18} className="text-secondary" />
                  <span>
                    {done ? "Zapisano: mnie też" : "Mnie też"}
                    <span className="sr-only">: {r.text}</span>
                  </span>
                </button>
              </div>
            </li>
          );
        })}
      </ul>
      <p role="status" className="text-body-md font-semibold text-primary">
        {status}
      </p>
    </div>
  );
}
