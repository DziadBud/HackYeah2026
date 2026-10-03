"use client";

import { useEffect, useRef, useState } from "react";
import { api, type IdeaStage } from "@/lib/api";
import { Icon } from "@/components/Icon";

const field =
  "min-h-12 w-full rounded-lg border-[1.5px] border-outline bg-surface p-space-sm text-body-md text-on-surface";
const labelCls = "text-body-md font-bold text-primary";

const STAGES: Record<IdeaStage, string> = {
  concept: "Pomysł lub koncepcja",
  prototype: "Prototyp",
  pilot: "Pilotaż (pierwsze testy)",
  running: "Już działa",
};

// POST /ideas: the idea lands in the ROPS admin inbox
export function IdeaForm({ initialSummary, onDone, onCancel }: { initialSummary: string; onDone: (msg: string) => void; onCancel: () => void }) {
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const first = useRef<HTMLInputElement>(null);

  useEffect(() => {
    first.current?.focus();
    first.current?.scrollIntoView({ block: "center" });
  }, []);

  return (
    <section aria-labelledby="idea-form-heading" className="flex flex-col gap-space-sm rounded-xl bg-surface-container-lowest p-space-md shadow-xl hc-edge">
      <h2 id="idea-form-heading" className="flex items-center gap-2 text-headline-sm font-semibold text-primary">
        <Icon name="lightbulb" />
        Zgłoś własny pomysł lub innowację
      </h2>
      <p className="text-body-md text-on-surface-variant">
        Pomysł trafi do zespołu ROPS. Pola bez dopisku „opcjonalnie” są wymagane.
      </p>
      <form
        className="flex flex-col gap-space-sm"
        onSubmit={async (e) => {
          e.preventDefault();
          const f = new FormData(e.currentTarget);
          const mail = email.trim();
          setBusy(true);
          setError("");
          try {
            await api.createIdea({
              summary: String(f.get("summary")).trim(),
              essence: String(f.get("essence")).trim(),
              target_group: String(f.get("target_group")).trim(),
              stage: String(f.get("stage")) as IdeaStage,
              ...(mail ? { email: mail, consent: true } : {}),
            });
            onDone(
              mail
                ? "Dziękujemy! Pomysł trafił do ROPS. Odpowiedź wyślemy na podany adres e-mail."
                : "Dziękujemy! Pomysł trafił do ROPS.",
            );
          } catch {
            setError("Nie udało się wysłać pomysłu. Sprawdź połączenie z serwerem i spróbuj ponownie.");
            setBusy(false);
          }
        }}
      >
        <div className="flex flex-col gap-1">
          <label htmlFor="idea-summary" className={labelCls}>
            Krótko: jaki to pomysł?
          </label>
          <input ref={first} id="idea-summary" name="summary" required maxLength={2000} defaultValue={initialSummary} className={field} />
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="idea-essence" className={labelCls}>
            Na czym polega rozwiązanie?
          </label>
          <textarea id="idea-essence" name="essence" required maxLength={2000} rows={3} className={`${field} resize-y`} />
        </div>
        <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
          <div className="flex flex-col gap-1">
            <label htmlFor="idea-target" className={labelCls}>
              Dla kogo jest?
            </label>
            <input id="idea-target" name="target_group" required maxLength={500} placeholder="np. seniorzy z małych miejscowości" className={field} />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="idea-stage" className={labelCls}>
              Na jakim jest etapie?
            </label>
            <select id="idea-stage" name="stage" defaultValue="concept" className={field}>
              {(Object.keys(STAGES) as IdeaStage[]).map((s) => (
                <option key={s} value={s}>
                  {STAGES[s]}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="flex flex-col gap-1">
          <label htmlFor="idea-email" className={labelCls}>
            E-mail do odpowiedzi (opcjonalnie)
          </label>
          <input id="idea-email" type="email" maxLength={254} autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} className={field} />
        </div>
        {email.trim() && (
          <label className="flex min-h-12 items-start gap-space-sm text-body-md text-on-surface">
            <input type="checkbox" required className="mt-0.5 size-6 shrink-0 accent-primary-container" />
            <span>Zgadzam się na kontakt ROPS w sprawie tego pomysłu (wymagane, gdy podajesz adres).</span>
          </label>
        )}
        <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
          {error}
        </p>
        <div className="flex flex-wrap justify-end gap-space-xs">
          <button type="button" onClick={onCancel} className="min-h-12 rounded-lg px-space-md text-body-md font-bold text-on-surface-variant hover:bg-surface-container-high">
            Anuluj
          </button>
          <button
            type="submit"
            disabled={busy}
            className="flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-primary px-space-lg text-body-lg font-bold text-on-primary shadow-md hover:bg-primary-container disabled:cursor-wait disabled:opacity-80"
          >
            <Icon name="send" size={22} />
            {busy ? "Wysyłam…" : "Wyślij pomysł do ROPS"}
          </button>
        </div>
      </form>
    </section>
  );
}
