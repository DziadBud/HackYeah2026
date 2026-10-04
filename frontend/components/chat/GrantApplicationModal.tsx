"use client";

import { useEffect, useId, useRef, useState } from "react";
import { ApiError, api, type ActionPlan, type ApplicantType, type GrantApplication, type PlanStep, type PublicGrantCall } from "@/lib/api";
import { Icon } from "@/components/Icon";

const field =
  "min-h-12 w-full rounded-lg border-[1.5px] border-outline bg-surface p-space-sm text-body-md text-on-surface";
const labelCls = "text-body-md font-bold text-primary";
const sectionCls =
  "flex flex-col gap-space-sm rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-space-md";

const APPLICANT_LABELS: Record<ApplicantType, string> = {
  person: "Osoba fizyczna",
  organization: "Podmiot (organizacja)",
  informal_group: "Grupa nieformalna",
};

const PERSON_DECL: Record<string, string> = {
  resides_in_poland: "Posiadam miejsce zamieszkania na terenie Polski",
  full_legal_capacity: "Posiadam pełną zdolność do czynności prawnych",
  no_criminal_conviction: "Nie byłem/am skazany/a prawomocnym wyrokiem za umyślne przestępstwo",
  not_excluded_public_funds: "Nie jestem wykluczony/a z otrzymania środków europejskich (art. 207 u.f.p.)",
  not_under_sanctions: "Nie podlegam wykluczeniu z powodu sankcji związanych z agresją na Ukrainę",
  no_tax_arrears: "Nie zalegam z podatkami, opłatami ani składkami",
  voluntary_participation: "Dobrowolnie deklaruję uczestnictwo w projekcie Inkubator Włączenia Społecznego 2.0",
  accepts_procedures: "Zapoznałem/am się z Procedurami i akceptuję warunki",
  data_truthful: "Dane w formularzu są zgodne z prawdą",
  not_employed_rops_innoagh: "Nie jestem zatrudniony/a w ROPS ani INNOAGH i nie łączą mnie z nimi wskazane więzi",
  no_parallel_application: "Nie aplikuję równolegle o wsparcie na ten sam pomysł w innym projekcie FERS 5.1",
  not_duplicating_existing: "Innowacja nie powiela już wdrożonych / inkubowanych rozwiązań w Polsce",
  no_fees_from_testers: "Nie będę pobierał/a opłat od osób testujących innowację",
  max_two_applications: "W ramach naboru składam nie więcej niż 2 aplikacje",
  not_implementation_character: "Innowacja nie ma charakteru wdrożeniowego",
  aware_form_shared: "Jestem świadomy/a udostępnienia formularza komisji i innym inkubatorom",
  equality_and_dnsh: "Będę stosować zasady równościowe i DNSH",
  rodo_info_received: "Potwierdzam wypełnienie wobec mnie obowiązku informacyjnego RODO",
  rodo_duties_fulfilled: "Wypełniłem/am obowiązki informacyjne RODO wobec osób, których dane pozyskałem/am",
};

const ORG_DECL: Record<string, string> = {
  entity_seat_in_poland: "Podmiot posiada siedzibę (lub oddział) na terenie Polski",
  management_no_conviction: "Członkowie organów / wspólnicy nie byli skazani prawomocnym wyrokiem",
  entity_not_excluded_public_funds: "Podmiot nie jest wykluczony z środków europejskich (art. 207 u.f.p.)",
  entity_not_under_sanctions: "Podmiot nie podlega wykluczeniu z powodu sankcji",
  entity_no_tax_arrears: "Podmiot nie zalega z podatkami, opłatami ani składkami",
  partners_not_employed_rops: "Wspólnicy / członkowie organów nie są zatrudnieni w ROPS ani INNOAGH",
  no_conflict_of_interest: "Brak konfliktu interesów z personelem / władzami ROPS lub INNOAGH",
  not_malopolska_unit: "Podmiot nie jest jednostką / osobą prawną Województwa Małopolskiego",
  not_agh_capital_linked: "Podmiot nie jest powiązany kapitałowo z AGH",
  voluntary_participation: "Dobrowolnie deklaruję uczestnictwo podmiotu w projekcie",
  accepts_procedures: "Zapoznałem/am się z Procedurami i akceptuję warunki",
  data_truthful: "Dane w formularzu są zgodne z prawdą",
  no_parallel_application: "Podmiot nie aplikuje równolegle o wsparcie na ten sam pomysł",
  not_duplicating_existing: "Innowacja nie powiela już wdrożonych / inkubowanych rozwiązań",
  no_fees_from_testers: "Podmiot nie będzie pobierał opłat od osób testujących",
  max_two_applications: "W ramach naboru podmiot składa nie więcej niż 2 aplikacje",
  not_implementation_character: "Innowacja nie ma charakteru wdrożeniowego",
  aware_form_shared: "Jestem świadomy/a udostępnienia formularza komisji i innym inkubatorom",
  equality_and_dnsh: "Będę stosować zasady równościowe i DNSH",
  rodo_info_received: "Potwierdzam wypełnienie wobec mnie obowiązku informacyjnego RODO",
  rodo_duties_fulfilled: "Wypełniłem/am obowiązki informacyjne RODO wobec osób, których dane pozyskałem/am",
};

function emptyStep(): PlanStep {
  return { action: "", timeline: "", cost_pln: null, note: "do oszacowania" };
}

function str(v: unknown) {
  return typeof v === "string" ? v : "";
}

type Props = {
  initialSummary?: string;
  onClose: () => void;
  onDone: (msg: string) => void;
};

/** Popup: 1) sam opis pomysłu → 2) pełny Zał. 3 (AI albo pusty szkic) */
export function GrantApplicationModal({ initialSummary = "", onClose, onDone }: Props) {
  const titleId = useId();
  const closeRef = useRef<HTMLButtonElement>(null);
  const [summary, setSummary] = useState(initialSummary);
  const [calls, setCalls] = useState<PublicGrantCall[]>([]);
  const [callsError, setCallsError] = useState("");
  const [draft, setDraft] = useState<GrantApplication | null>(null);
  const [busy, setBusy] = useState(false);
  const [busyLabel, setBusyLabel] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !busy) onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose, busy]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const list = await api.openGrantCalls();
        if (cancelled) return;
        setCalls(list);
        setCallsError(list.length ? "" : "Brak otwartego naboru grantowego.");
      } catch (err) {
        if (!cancelled) {
          setCallsError(
            err instanceof ApiError
              ? `Nie udało się pobrać naborów (HTTP ${err.status}).`
              : "Nie udało się pobrać otwartych naborów.",
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function startDraft(useAi: boolean) {
    const ideaText = summary.trim();
    if (useAi && !ideaText) {
      setError("Żeby wygenerować szkic AI, wpisz krótki opis pomysłu.");
      return;
    }
    setBusy(true);
    setBusyLabel(useAi ? "Generuję szkic wniosku AI…" : "Otwieram pusty formularz…");
    setError("");
    try {
      let openCalls = calls;
      if (openCalls.length === 0) {
        openCalls = await api.openGrantCalls();
        setCalls(openCalls);
        if (openCalls.length === 0) {
          setCallsError("Brak otwartego naboru grantowego.");
          setError("Brak otwartego naboru grantowego. Spróbuj ponownie później.");
          return;
        }
        setCallsError("");
      }
      const callId = openCalls[0].id;
      // skip path may have empty description — API still needs non-empty idea fields
      const seed = ideaText || "Do uzupełnienia w formularzu wniosku";
      const idea = await api.createIdea({
        summary: seed.slice(0, 2000),
        essence: seed.slice(0, 2000),
        target_group: "do uzupełnienia we wniosku",
        stage: "concept",
      });
      const app = await api.createGrantApplication(idea.id, {
        grant_call_id: callId,
        applicant_type: "person",
        use_ai: useAi,
      });
      // skip without description → blank Zał. 3 for manual fill (keep ids/status from API)
      if (!useAi && !ideaText) {
        setDraft({
          ...app,
          title: "",
          description: "",
          innovativeness: "",
          problem_diagnosis: "",
          beneficiaries: "",
          expected_change: "",
          future_vision: "",
          action_plan: {
            preparation_summary: "",
            preparation: [],
            testing_summary: "",
            testing_phase_1: [],
            testing_phase_2: [],
          },
          team: "",
        });
      } else {
        setDraft(app);
      }
    } catch (err) {
      const detail = err instanceof ApiError ? ` (HTTP ${err.status})` : "";
      setError(
        useAi
          ? `Nie udało się wygenerować wniosku${detail}. Sprawdź API / klucz Gemini i spróbuj ponownie.`
          : `Nie udało się otworzyć formularza${detail}. Sprawdź połączenie z API.`,
      );
    } finally {
      setBusy(false);
      setBusyLabel("");
    }
  }

  async function save(submit: boolean) {
    if (!draft) return;
    setBusy(true);
    setBusyLabel(submit ? "Wysyłam wniosek…" : "Zapisuję szkic…");
    setError("");
    try {
      const amountRaw = draft.grant_amount_pln;
      const amount =
        amountRaw === null || amountRaw === undefined || amountRaw === ""
          ? undefined
          : String(amountRaw);
      const updated = await api.updateGrantApplication(draft.id, {
        title: draft.title,
        applicant_type: draft.applicant_type,
        applicant: draft.applicant,
        description: draft.description,
        innovativeness: draft.innovativeness,
        problem_diagnosis: draft.problem_diagnosis,
        beneficiaries: draft.beneficiaries,
        expected_change: draft.expected_change,
        future_vision: draft.future_vision,
        action_plan: draft.action_plan,
        ...(amount !== undefined ? { grant_amount_pln: amount } : {}),
        team: draft.team,
        declarations: draft.declarations,
        ...(submit ? { status: "submitted" as const } : {}),
      });
      setDraft(updated);
      if (submit) onDone("Wniosek grantowy został wysłany. Dziękujemy!");
    } catch (err) {
      const detail = err instanceof ApiError ? ` (HTTP ${err.status})` : "";
      setError(
        submit
          ? `Nie udało się wysłać wniosku${detail}. Sprawdź pola i spróbuj ponownie.`
          : `Nie udało się zapisać szkicu${detail}. Spróbuj ponownie.`,
      );
    } finally {
      setBusy(false);
      setBusyLabel("");
    }
  }

  function setText(key: keyof GrantApplication, value: string) {
    setDraft((d) => (d ? { ...d, [key]: value } : d));
  }

  function setApplicantField(key: string, value: string) {
    setDraft((d) => (d ? { ...d, applicant: { ...d.applicant, [key]: value } } : d));
  }

  function setOrgContact(
    which: "representative" | "working_contact",
    key: string,
    value: string,
  ) {
    setDraft((d) => {
      if (!d) return d;
      const current = (d.applicant[which] as Record<string, string> | undefined) ?? {};
      return {
        ...d,
        applicant: { ...d.applicant, [which]: { ...current, [key]: value } },
      };
    });
  }

  function setDecl(key: string, checked: boolean) {
    setDraft((d) =>
      d ? { ...d, declarations: { ...d.declarations, [key]: checked } } : d,
    );
  }

  function setPlan(next: ActionPlan) {
    setDraft((d) => (d ? { ...d, action_plan: next } : d));
  }

  async function changeApplicantType(next: ApplicantType) {
    if (!draft || next === draft.applicant_type) return;
    setBusy(true);
    setError("");
    try {
      const updated = await api.updateGrantApplication(draft.id, { applicant_type: next });
      setDraft(updated);
    } catch {
      setError("Nie udało się zmienić typu wnioskodawcy.");
    } finally {
      setBusy(false);
    }
  }

  const declLabels =
    draft?.applicant_type === "organization" ? ORG_DECL : PERSON_DECL;

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-on-surface/50 p-space-sm sm:items-center"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-2xl bg-surface shadow-2xl hc-edge"
      >
        <header className="flex items-start justify-between gap-space-sm border-b border-outline-variant/40 px-space-md py-space-sm">
          <div>
            <h2 id={titleId} className="flex items-center gap-2 text-headline-sm font-semibold text-primary">
              <Icon name={draft ? "description" : "edit_note"} />
              {draft ? "Wniosek grantowy (Zał. 3)" : "Złóż wniosek"}
            </h2>
            <p className="mt-1 text-body-md text-on-surface-variant">
              {draft
                ? "Edytuj treść i uzupełnij dane wnioskodawcy, kwotę, zespół oraz oświadczenia."
                : "Opcjonalnie wpisz opis pomysłu i wygeneruj szkic AI — albo od razu przejdź do pustego formularza."}
            </p>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            className="flex min-h-12 min-w-12 items-center justify-center rounded-lg text-on-surface-variant hover:bg-surface-container-high"
            aria-label="Zamknij"
          >
            <Icon name="close" size={22} />
          </button>
        </header>

        <div className="relative flex-1 overflow-y-auto px-space-md py-space-md">
          {busy && (
            <div
              className="absolute inset-0 z-10 flex flex-col items-center justify-center gap-space-sm bg-surface/80"
              role="status"
              aria-live="polite"
            >
              <span
                className="size-12 animate-spin rounded-full border-4 border-outline border-t-primary"
                aria-hidden="true"
              />
              <p className="text-body-lg font-semibold text-primary">{busyLabel || "Proszę czekać…"}</p>
            </div>
          )}
          {!draft ? (
            <div className="flex flex-col gap-space-sm">
              {callsError && (
                <p role="alert" className="text-body-md font-semibold text-error">
                  {callsError}
                </p>
              )}
              <div className="flex flex-col gap-1">
                <label htmlFor="ai-summary" className={labelCls}>
                  Opis pomysłu <span className="font-normal text-on-surface-variant">(opcjonalnie przy pominięciu AI)</span>
                </label>
                <textarea
                  id="ai-summary"
                  rows={8}
                  maxLength={2000}
                  className={`${field} resize-y`}
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  placeholder="Jaki problem chcesz rozwiązać? Na czym polega Twój pomysł? (wymagane tylko przy generacji AI)"
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-space-md">
              <p className="text-body-sm text-on-surface-variant">
                Szkic:{" "}
                {draft.generated_by === "gemini"
                  ? "Gemini"
                  : draft.generated_by === "template"
                    ? "szablon"
                    : (draft.generated_by ?? "—")}
                {" · "}
                status: {draft.status === "submitted" ? "wysłany" : "szkic"}
              </p>

              <section className={sectionCls} aria-labelledby="sec-1">
                <h3 id="sec-1" className="text-title-md font-semibold text-primary">
                  1. Tytuł innowacji
                </h3>
                <input
                  className={field}
                  value={draft.title}
                  onChange={(e) => setText("title", e.target.value)}
                  maxLength={500}
                />
              </section>

              <section className={sectionCls} aria-labelledby="sec-2">
                <h3 id="sec-2" className="text-title-md font-semibold text-primary">
                  2. Dane pomysłodawcy
                </h3>
                <div className="flex flex-col gap-1">
                  <label htmlFor="edit-applicant-type" className={labelCls}>
                    Typ
                  </label>
                  <select
                    id="edit-applicant-type"
                    className={field}
                    value={draft.applicant_type}
                    disabled={busy}
                    onChange={(e) => changeApplicantType(e.target.value as ApplicantType)}
                  >
                    {(Object.keys(APPLICANT_LABELS) as ApplicantType[]).map((t) => (
                      <option key={t} value={t}>
                        {APPLICANT_LABELS[t]}
                      </option>
                    ))}
                  </select>
                </div>
                {draft.applicant_type === "person" && (
                  <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
                    {(
                      [
                        ["first_name", "Imię"],
                        ["last_name", "Nazwisko"],
                        ["address", "Adres korespondencyjny"],
                        ["postal_code", "Kod pocztowy"],
                        ["city", "Miejscowość"],
                        ["phone", "Telefon"],
                        ["email", "E-mail"],
                      ] as const
                    ).map(([key, label]) => (
                      <div key={key} className="flex flex-col gap-1">
                        <label className={labelCls} htmlFor={`app-${key}`}>
                          {label}
                        </label>
                        <input
                          id={`app-${key}`}
                          className={field}
                          value={str(draft.applicant[key])}
                          onChange={(e) => setApplicantField(key, e.target.value)}
                        />
                      </div>
                    ))}
                  </div>
                )}
                {draft.applicant_type === "organization" && (
                  <div className="flex flex-col gap-space-sm">
                    <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
                      {(
                        [
                          ["name", "Nazwa podmiotu"],
                          ["krs", "KRS"],
                          ["regon", "REGON"],
                          ["nip", "NIP"],
                          ["address", "Adres siedziby"],
                          ["postal_code", "Kod pocztowy"],
                          ["city", "Miejscowość"],
                          ["phone", "Telefon"],
                          ["email", "E-mail"],
                        ] as const
                      ).map(([key, label]) => (
                        <div key={key} className="flex flex-col gap-1">
                          <label className={labelCls} htmlFor={`org-${key}`}>
                            {label}
                          </label>
                          <input
                            id={`org-${key}`}
                            className={field}
                            value={str(draft.applicant[key])}
                            onChange={(e) => setApplicantField(key, e.target.value)}
                          />
                        </div>
                      ))}
                    </div>
                    {(["representative", "working_contact"] as const).map((which) => {
                      const title =
                        which === "representative"
                          ? "Osoba upoważniona do reprezentowania"
                          : "Kontakt roboczy";
                      const contact =
                        (draft.applicant[which] as Record<string, string> | undefined) ?? {};
                      return (
                        <div key={which} className="rounded-lg border border-outline-variant/30 p-space-sm">
                          <p className="mb-space-xs text-body-md font-bold text-primary">{title}</p>
                          <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
                            {(
                              [
                                ["role", "Funkcja"],
                                ["full_name", "Imię i nazwisko"],
                                ["phone", "Telefon"],
                                ["email", "E-mail"],
                              ] as const
                            ).map(([key, label]) => (
                              <div key={key} className="flex flex-col gap-1">
                                <label className={labelCls} htmlFor={`${which}-${key}`}>
                                  {label}
                                </label>
                                <input
                                  id={`${which}-${key}`}
                                  className={field}
                                  value={contact[key] ?? ""}
                                  onChange={(e) => setOrgContact(which, key, e.target.value)}
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                {draft.applicant_type === "informal_group" && (
                  <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
                    {(
                      [
                        ["representative_full_name", "Reprezentant — imię i nazwisko"],
                        ["representative_phone", "Telefon"],
                        ["representative_email", "E-mail"],
                      ] as const
                    ).map(([key, label]) => (
                      <div key={key} className="flex flex-col gap-1">
                        <label className={labelCls} htmlFor={`inf-${key}`}>
                          {label}
                        </label>
                        <input
                          id={`inf-${key}`}
                          className={field}
                          value={str(draft.applicant[key])}
                          onChange={(e) => setApplicantField(key, e.target.value)}
                        />
                      </div>
                    ))}
                  </div>
                )}
              </section>

              {(
                [
                  ["description", "3. Opis innowacji"],
                  ["innovativeness", "4. Innowacyjność rozwiązania"],
                  ["problem_diagnosis", "5. Diagnoza problemu"],
                  ["beneficiaries", "6. Opis odbiorców innowacji"],
                  ["expected_change", "7. Zmiana jaką wprowadza innowacja"],
                  ["future_vision", "8. Wizja przyszłości innowacji"],
                ] as const
              ).map(([key, heading]) => (
                <section key={key} className={sectionCls}>
                  <h3 className="text-title-md font-semibold text-primary">{heading}</h3>
                  <textarea
                    rows={4}
                    className={`${field} resize-y`}
                    value={String(draft[key] ?? "")}
                    onChange={(e) => setText(key, e.target.value)}
                  />
                </section>
              ))}

              <section className={sectionCls} aria-labelledby="sec-9">
                <h3 id="sec-9" className="text-title-md font-semibold text-primary">
                  9. Plan działania i koszty
                </h3>
                <PlanEditor plan={draft.action_plan} onChange={setPlan} />
              </section>

              <section className={sectionCls} aria-labelledby="sec-10">
                <h3 id="sec-10" className="text-title-md font-semibold text-primary">
                  10. Wnioskowana kwota grantu (PLN)
                </h3>
                <input
                  type="number"
                  min={0}
                  step={1}
                  className={field}
                  value={draft.grant_amount_pln ?? ""}
                  onChange={(e) =>
                    setDraft((d) =>
                      d
                        ? {
                            ...d,
                            grant_amount_pln:
                              e.target.value === "" ? null : String(Number(e.target.value)),
                          }
                        : d,
                    )
                  }
                />
              </section>

              <section className={sectionCls} aria-labelledby="sec-11">
                <h3 id="sec-11" className="text-title-md font-semibold text-primary">
                  11. Zespół projektowy i doświadczenie
                </h3>
                <textarea
                  rows={3}
                  className={`${field} resize-y`}
                  value={draft.team}
                  onChange={(e) => setText("team", e.target.value)}
                />
              </section>

              <section className={sectionCls} aria-labelledby="sec-12">
                <h3 id="sec-12" className="text-title-md font-semibold text-primary">
                  12. Oświadczenia
                </h3>
                <ul className="flex flex-col gap-space-xs">
                  {Object.keys(declLabels).map((key) => (
                    <li key={key}>
                      <label className="flex min-h-12 items-start gap-space-sm text-body-md text-on-surface">
                        <input
                          type="checkbox"
                          className="mt-0.5 size-6 shrink-0 accent-primary-container"
                          checked={Boolean(draft.declarations[key])}
                          onChange={(e) => setDecl(key, e.target.checked)}
                        />
                        <span>{declLabels[key]}</span>
                      </label>
                    </li>
                  ))}
                </ul>
              </section>
            </div>
          )}
        </div>

        <footer className="flex flex-col gap-space-xs border-t border-outline-variant/40 px-space-md py-space-sm">
          <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
            {error}
          </p>
          <div className="flex flex-wrap justify-end gap-space-xs">
            <button
              type="button"
              onClick={
                draft
                  ? () => onDone("Szkic wniosku został zapisany w systemie. Możesz wrócić do edycji później.")
                  : onClose
              }
              className="min-h-12 rounded-lg px-space-md text-body-md font-bold text-on-surface-variant hover:bg-surface-container-high"
            >
              {draft?.status === "submitted" ? "Zamknij" : "Anuluj"}
            </button>
            {!draft ? (
              <div className="flex w-full flex-col gap-space-xs sm:flex-row sm:flex-wrap sm:justify-end">
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => startDraft(false)}
                  className="min-h-12 rounded-lg border-[1.5px] border-outline px-space-md text-body-md font-bold text-primary hover:bg-surface-container-high disabled:opacity-80"
                >
                  {busy && busyLabel.includes("pusty") ? "Otwieram…" : "Pomiń generację — wypełnię sam/a"}
                </button>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => startDraft(true)}
                  className="flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-primary px-space-lg text-body-lg font-bold text-on-primary shadow-md hover:bg-primary-container disabled:cursor-wait disabled:opacity-80"
                >
                  <Icon name="auto_awesome" size={22} />
                  {busy && busyLabel.includes("AI") ? "Generuję…" : "Wygeneruj szkic AI"}
                </button>
              </div>
            ) : draft.status !== "submitted" ? (
              <>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => save(false)}
                  className="min-h-12 rounded-lg border-[1.5px] border-outline px-space-md text-body-md font-bold text-primary hover:bg-surface-container-high disabled:opacity-80"
                >
                  {busy ? "Zapisuję…" : "Zapisz szkic"}
                </button>
                <button
                  type="button"
                  disabled={busy}
                  onClick={() => save(true)}
                  className="flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-primary px-space-lg text-body-lg font-bold text-on-primary shadow-md hover:bg-primary-container disabled:cursor-wait disabled:opacity-80"
                >
                  <Icon name="send" size={22} />
                  {busy ? "Wysyłam…" : "Wyślij wniosek"}
                </button>
              </>
            ) : null}
          </div>
        </footer>
      </div>
    </div>
  );
}

function PlanEditor({
  plan,
  onChange,
}: {
  plan: ActionPlan;
  onChange: (p: ActionPlan) => void;
}) {
  function updateSteps(
    key: "preparation" | "testing_phase_1" | "testing_phase_2",
    steps: PlanStep[],
  ) {
    onChange({ ...plan, [key]: steps });
  }

  function StepList({
    label,
    listKey,
  }: {
    label: string;
    listKey: "preparation" | "testing_phase_1" | "testing_phase_2";
  }) {
    const steps = plan[listKey] ?? [];
    return (
      <div className="flex flex-col gap-space-xs">
        <p className="text-body-md font-bold text-primary">{label}</p>
        {steps.map((step, idx) => (
          <div
            key={`${listKey}-${idx}`}
            className="grid grid-cols-1 gap-space-xs rounded-lg border border-outline-variant/30 p-space-sm sm:grid-cols-3"
          >
            <input
              className={field}
              placeholder="Działanie"
              value={step.action}
              onChange={(e) => {
                const next = steps.map((s, i) =>
                  i === idx ? { ...s, action: e.target.value } : s,
                );
                updateSteps(listKey, next);
              }}
            />
            <input
              className={field}
              placeholder="Termin"
              value={step.timeline}
              onChange={(e) => {
                const next = steps.map((s, i) =>
                  i === idx ? { ...s, timeline: e.target.value } : s,
                );
                updateSteps(listKey, next);
              }}
            />
            <input
              type="number"
              className={field}
              placeholder="Koszt PLN"
              value={step.cost_pln ?? ""}
              onChange={(e) => {
                const next = steps.map((s, i) =>
                  i === idx
                    ? {
                        ...s,
                        cost_pln: e.target.value === "" ? null : Number(e.target.value),
                      }
                    : s,
                );
                updateSteps(listKey, next);
              }}
            />
          </div>
        ))}
        <button
          type="button"
          className="min-h-12 self-start rounded-lg px-space-md text-body-md font-bold text-primary hover:bg-surface-container-high"
          onClick={() => updateSteps(listKey, [...steps, emptyStep()])}
        >
          + Dodaj działanie
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-space-sm">
      <div className="flex flex-col gap-1">
        <label className={labelCls} htmlFor="prep-summary">
          Okres przygotowawczy — opis
        </label>
        <textarea
          id="prep-summary"
          rows={2}
          className={`${field} resize-y`}
          value={plan.preparation_summary}
          onChange={(e) => onChange({ ...plan, preparation_summary: e.target.value })}
        />
      </div>
      <StepList label="Przygotowanie — kroki" listKey="preparation" />
      <div className="flex flex-col gap-1">
        <label className={labelCls} htmlFor="test-summary">
          Okres testowania — opis
        </label>
        <textarea
          id="test-summary"
          rows={2}
          className={`${field} resize-y`}
          value={plan.testing_summary}
          onChange={(e) => onChange({ ...plan, testing_summary: e.target.value })}
        />
      </div>
      <StepList label="Faza I testu" listKey="testing_phase_1" />
      <StepList label="Faza II testu" listKey="testing_phase_2" />
    </div>
  );
}
