"use client";

import { useEffect, useId, useRef, useState } from "react";
import { ApiError, api, type ActionPlan, type ApplicantType, type GrantApplication, type PlanStep, type PublicGrantCall } from "@/lib/api";
import { Icon } from "@/components/Icon";
import {
  APPLICANT_LABELS,
  CONTACT_FIELDS,
  INFORMAL_FIELDS,
  NARRATIVE_SECTIONS,
  ORG_DECL,
  ORG_FIELDS,
  PERSON_DECL,
  PERSON_FIELDS,
} from "@/components/grant/labels";
import { MoneyInput, fmtZl } from "@/components/grant/MoneyInput";
import { CharCount } from "@/components/forms/CharCount";
import { fieldKind, formatError, inputAttrs, sanitize } from "@/components/forms/validation";

const field =
  "min-h-12 w-full rounded-lg border-[1.5px] border-outline bg-surface p-space-sm text-body-md text-on-surface aria-[invalid=true]:border-error";
const labelCls = "text-body-md font-bold text-primary";
const headingCls = "text-title-md font-semibold text-primary";
const sectionCls =
  "flex flex-col gap-space-sm rounded-xl border border-outline-variant/40 bg-surface-container-lowest p-space-md";
const primaryBtn =
  "flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-primary px-space-lg text-body-lg font-bold text-on-primary shadow-md hover:bg-primary-container disabled:cursor-wait disabled:opacity-80";
const secondaryBtn =
  "min-h-12 rounded-lg border-[1.5px] border-outline px-space-md text-body-md font-bold text-primary hover:bg-surface-container-high disabled:opacity-80";
const textBtn =
  "min-h-12 rounded-lg px-space-md text-body-md font-bold text-on-surface-variant hover:bg-surface-container-high";

// placeholder note the generator puts on steps without a cost
const ESTIMATE_NOTE = "do oszacowania";
const SAVED_MSG = "Szkic wniosku został zapisany.";

type StepKey = "preparation" | "testing_phase_1" | "testing_phase_2";
type Errors = Record<string, string>;

// minimum to send: who applies, how to reach them, what for and how much; all declarations are mandatory
const REQUIRED_APPLICANT: Record<ApplicantType, string[]> = {
  person: ["app-first_name", "app-last_name", "app-email"],
  organization: ["org-name", "org-email"],
  informal_group: ["inf-representative_full_name", "inf-representative_email"],
};

function emptyStep(): PlanStep {
  return { action: "", timeline: "", cost_pln: null, note: ESTIMATE_NOTE };
}

function str(v: unknown) {
  return typeof v === "string" ? v : "";
}

function sumSteps(steps: PlanStep[]) {
  return steps.reduce((sum, s) => sum + (s.cost_pln ?? 0), 0);
}

function sumPlan(plan: ActionPlan) {
  return sumSteps(plan.preparation) + sumSteps(plan.testing_phase_1) + sumSteps(plan.testing_phase_2);
}

function amountOf(d: GrantApplication): number | null {
  const raw = d.grant_amount_pln;
  return raw === null || raw === "" ? null : Number(raw);
}

function declLabelsFor(t: ApplicantType) {
  return t === "organization" ? ORG_DECL : PERSON_DECL;
}

function hasApplicantData(d: GrantApplication) {
  const filled = (v: unknown): boolean =>
    typeof v === "string" ? v.trim() !== "" : v !== null && typeof v === "object" && Object.values(v).some(filled);
  return filled(d.applicant) || Object.values(d.declarations).some(Boolean);
}

type ApplicantInput = { id: string; key: string; label: string; value: string };

// every §2 input of the current applicant type, in form order
function applicantInputs(d: GrantApplication): ApplicantInput[] {
  const from = (prefix: string, fields: readonly (readonly [string, string])[], values: Record<string, unknown>) =>
    fields.map(([key, label]) => ({ id: `${prefix}-${key}`, key, label, value: str(values[key]) }));
  if (d.applicant_type === "person") return from("app", PERSON_FIELDS, d.applicant);
  if (d.applicant_type === "informal_group") return from("inf", INFORMAL_FIELDS, d.applicant);
  const contact = (which: string) => (d.applicant[which] as Record<string, unknown> | undefined) ?? {};
  return [
    ...from("org", ORG_FIELDS, d.applicant),
    ...from("representative", CONTACT_FIELDS, contact("representative")),
    ...from("working_contact", CONTACT_FIELDS, contact("working_contact")),
  ];
}

// format errors always; missing required fields only once the user tries to send
function validate(d: GrantApplication, requiredToo: boolean): Errors {
  const e: Errors = {};
  if (requiredToo && !d.title.trim()) e["app-title"] = "Wpisz tytuł innowacji.";
  const required = new Set(REQUIRED_APPLICANT[d.applicant_type]);
  for (const f of applicantInputs(d)) {
    if (!f.value.trim()) {
      if (requiredToo && required.has(f.id)) e[f.id] = `Uzupełnij pole „${f.label}”.`;
      continue;
    }
    const msg = formatError(fieldKind(f.key), f.value);
    if (msg) e[f.id] = msg;
  }
  if (!requiredToo) return e;
  const amount = amountOf(d);
  if (amount === null || amount <= 0) e["app-amount"] = "Podaj wnioskowaną kwotę grantu.";
  const missing = Object.keys(declLabelsFor(d.applicant_type)).filter((k) => !d.declarations[k]);
  if (missing.length) e["decl-all"] = `Zaznacz wszystkie oświadczenia (brakuje: ${missing.length}).`;
  return e;
}

function errProps(errors: Errors, id: string, extra?: string) {
  const describedBy = [errors[id] ? `${id}-err` : "", extra ?? ""].filter(Boolean).join(" ");
  return { "aria-invalid": errors[id] ? true : undefined, "aria-describedby": describedBy || undefined };
}

function FieldError({ errors, id }: { errors: Errors; id: string }) {
  return errors[id] ? (
    <p id={`${id}-err`} className="text-body-md font-semibold text-error">
      {errors[id]}
    </p>
  ) : null;
}

function TextField({
  id,
  fieldKey,
  label,
  value,
  onChange,
  onBlur,
  errors,
}: {
  id: string;
  fieldKey: string;
  label: string;
  value: string;
  onChange: (v: string) => void;
  onBlur: (id: string) => void;
  errors: Errors;
}) {
  const kind = fieldKind(fieldKey);
  return (
    <div className="flex flex-col gap-1">
      <label className={labelCls} htmlFor={id}>
        {label}
      </label>
      <input
        id={id}
        className={field}
        value={value}
        onChange={(e) => onChange(sanitize(kind, e.target.value))}
        onBlur={() => onBlur(id)}
        {...inputAttrs(fieldKey)}
        {...errProps(errors, id)}
      />
      <FieldError errors={errors} id={id} />
    </div>
  );
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
  const summaryRef = useRef<HTMLDivElement>(null);
  const confirmRef = useRef<HTMLButtonElement>(null);
  const [summary, setSummary] = useState(initialSummary);
  const [calls, setCalls] = useState<PublicGrantCall[]>([]);
  const [callsError, setCallsError] = useState("");
  const [draft, setDraft] = useState<GrantApplication | null>(null);
  const [dirty, setDirty] = useState(false);
  const [showErrors, setShowErrors] = useState(false);
  // fields the user has left; their format errors show before the first send
  const [touched, setTouched] = useState<Set<string>>(new Set());
  const [confirmClose, setConfirmClose] = useState(false);
  const [busy, setBusy] = useState(false);
  const [busyLabel, setBusyLabel] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    closeRef.current?.focus();
  }, []);

  useEffect(() => {
    if (confirmClose) confirmRef.current?.focus();
  }, [confirmClose]);

  // no deps: the handler reads the latest draft/dirty state
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      if (confirmClose) setConfirmClose(false);
      else requestClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  });

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

  function requestClose() {
    if (busy) return;
    if (!draft || draft.status === "submitted") return onClose();
    if (dirty) return setConfirmClose(true);
    onDone(SAVED_MSG);
  }

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
      setDirty(false);
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

  async function save(submit: boolean): Promise<boolean> {
    if (!draft) return false;
    if (submit) {
      setShowErrors(true);
      if (Object.keys(validate(draft, true)).length > 0) {
        setError("");
        requestAnimationFrame(() => summaryRef.current?.focus());
        return false;
      }
    }
    // the field loses focus when the form goes inert; give it back after the save
    const focused = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    setBusy(true);
    setBusyLabel(submit ? "Wysyłam wniosek…" : "Zapisuję szkic…");
    setError("");
    try {
      const amount = amountOf(draft);
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
        grant_amount_pln: amount === null ? null : String(amount),
        team: draft.team,
        declarations: draft.declarations,
        ...(submit ? { status: "submitted" as const } : {}),
      });
      setDraft(updated);
      setDirty(false);
      if (submit) onDone("Wniosek grantowy został wysłany. Dziękujemy!");
      else setError("Zapisano szkic.");
      return true;
    } catch (err) {
      const detail = err instanceof ApiError ? ` (HTTP ${err.status})` : "";
      setError(
        submit
          ? `Nie udało się wysłać wniosku${detail}. Spróbuj ponownie.`
          : `Nie udało się zapisać szkicu${detail}. Spróbuj ponownie.`,
      );
      return false;
    } finally {
      setBusy(false);
      setBusyLabel("");
      requestAnimationFrame(() => focused?.isConnected && focused.focus());
    }
  }

  function edit(change: (d: GrantApplication) => GrantApplication) {
    setDraft((d) => (d ? change(d) : d));
    setDirty(true);
  }

  function setText(key: keyof GrantApplication, value: string) {
    edit((d) => ({ ...d, [key]: value }));
  }

  function setApplicantField(key: string, value: string) {
    edit((d) => ({ ...d, applicant: { ...d.applicant, [key]: value } }));
  }

  function setOrgContact(which: "representative" | "working_contact", key: string, value: string) {
    edit((d) => {
      const current = (d.applicant[which] as Record<string, string> | undefined) ?? {};
      return { ...d, applicant: { ...d.applicant, [which]: { ...current, [key]: value } } };
    });
  }

  function setAmount(value: number | null) {
    edit((d) => ({ ...d, grant_amount_pln: value === null ? null : String(value) }));
  }

  // local only: saved with the rest of the form, so other unsaved edits survive the switch
  function changeApplicantType(next: ApplicantType) {
    if (!draft || next === draft.applicant_type) return;
    if (
      hasApplicantData(draft) &&
      !window.confirm("Zmiana typu wnioskodawcy wyczyści dane z sekcji 2 i oświadczenia. Kontynuować?")
    ) {
      return;
    }
    edit((d) => ({ ...d, applicant_type: next, applicant: {}, declarations: {} }));
  }

  async function saveAndClose() {
    setConfirmClose(false);
    if (await save(false)) onDone(SAVED_MSG);
  }

  const touch = (id: string) => setTouched((t) => (t.has(id) ? t : new Set(t).add(id)));
  const errors: Errors = !draft
    ? {}
    : showErrors
      ? validate(draft, true)
      : Object.fromEntries(Object.entries(validate(draft, false)).filter(([id]) => touched.has(id)));
  const errorList = Object.entries(errors);
  const declLabels = declLabelsFor(draft?.applicant_type ?? "person");
  const declError = errorList.find(([id]) => id === "decl-all");
  const declKeys = Object.keys(declLabels);
  const declTicked = draft ? declKeys.filter((k) => draft.declarations[k]).length : 0;
  const amount = draft ? amountOf(draft) : null;
  const planTotal = draft ? sumPlan(draft.action_plan) : 0;
  const amountA11y = errProps(errors, "app-amount", planTotal > 0 ? "amount-hint" : undefined);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-on-surface/50 p-space-sm sm:items-center"
      role="presentation"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) requestClose();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        className="relative flex max-h-[92vh] w-full max-w-3xl flex-col overflow-hidden rounded-2xl bg-surface shadow-2xl hc-edge"
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
            onClick={requestClose}
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
            <div className="flex flex-col gap-space-sm" inert={busy}>
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
                  aria-describedby="ai-summary-count"
                  placeholder="Jaki problem chcesz rozwiązać? Na czym polega Twój pomysł? (wymagane tylko przy generacji AI)"
                />
                <CharCount id="ai-summary-count" length={summary.length} max={2000} />
              </div>
            </div>
          ) : (
            // inert while saving: keys typed now would be overwritten by the server's copy
            <div className="flex flex-col gap-space-md" inert={busy}>
              <p className="text-body-md text-on-surface-variant">
                Szkic:{" "}
                {draft.generated_by === "gemini"
                  ? "Gemini"
                  : draft.generated_by === "template"
                    ? "szablon"
                    : (draft.generated_by ?? "—")}
                {" · "}
                status: {draft.status === "draft" ? "szkic" : "wysłany"}
                {dirty && " · niezapisane zmiany"}
              </p>

              {errorList.length > 0 && (
                <div
                  ref={summaryRef}
                  tabIndex={-1}
                  role="alert"
                  className="flex flex-col gap-space-xs rounded-xl border-2 border-error bg-surface-container-lowest p-space-md"
                >
                  <p className="text-body-md font-bold text-error">Przed wysłaniem popraw:</p>
                  <ul className="flex list-disc flex-col gap-1 pl-space-md">
                    {errorList.map(([id, msg]) => (
                      <li key={id}>
                        <a
                          href={`#${id}`}
                          className="text-body-md text-on-surface underline underline-offset-4"
                          onClick={(e) => {
                            e.preventDefault();
                            document.getElementById(id)?.focus();
                          }}
                        >
                          {msg}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              <section className={sectionCls}>
                <h3 className={headingCls}>
                  <label htmlFor="app-title">1. Tytuł innowacji</label>
                </h3>
                <input
                  id="app-title"
                  className={field}
                  value={draft.title}
                  onChange={(e) => setText("title", e.target.value)}
                  maxLength={500}
                  {...errProps(errors, "app-title")}
                />
                <FieldError errors={errors} id="app-title" />
              </section>

              <section className={sectionCls} aria-labelledby="sec-2">
                <h3 id="sec-2" className={headingCls}>
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
                    {PERSON_FIELDS.map(([key, label]) => (
                      <TextField
                        key={key}
                        id={`app-${key}`}
                        fieldKey={key}
                        label={label}
                        onBlur={touch}
                        value={str(draft.applicant[key])}
                        onChange={(v) => setApplicantField(key, v)}
                        errors={errors}
                      />
                    ))}
                  </div>
                )}
                {draft.applicant_type === "organization" && (
                  <div className="flex flex-col gap-space-sm">
                    <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
                      {ORG_FIELDS.map(([key, label]) => (
                        <TextField
                          key={key}
                          id={`org-${key}`}
                          fieldKey={key}
                          label={label}
                          onBlur={touch}
                          value={str(draft.applicant[key])}
                          onChange={(v) => setApplicantField(key, v)}
                          errors={errors}
                        />
                      ))}
                    </div>
                    {(
                      [
                        ["representative", "Osoba upoważniona do reprezentowania"],
                        ["working_contact", "Kontakt roboczy"],
                      ] as const
                    ).map(([which, title]) => {
                      const contact = (draft.applicant[which] as Record<string, string> | undefined) ?? {};
                      return (
                        <fieldset key={which} className="rounded-lg border border-outline-variant/30 p-space-sm">
                          <legend className="px-1 text-body-md font-bold text-primary">{title}</legend>
                          <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
                            {CONTACT_FIELDS.map(([key, label]) => (
                              <TextField
                                key={key}
                                id={`${which}-${key}`}
                                fieldKey={key}
                                label={label}
                                onBlur={touch}
                                value={contact[key] ?? ""}
                                onChange={(v) => setOrgContact(which, key, v)}
                                errors={errors}
                              />
                            ))}
                          </div>
                        </fieldset>
                      );
                    })}
                  </div>
                )}
                {draft.applicant_type === "informal_group" && (
                  <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
                    {INFORMAL_FIELDS.map(([key, label]) => (
                      <TextField
                        key={key}
                        id={`inf-${key}`}
                        fieldKey={key}
                        label={label}
                        onBlur={touch}
                        value={str(draft.applicant[key])}
                        onChange={(v) => setApplicantField(key, v)}
                        errors={errors}
                      />
                    ))}
                  </div>
                )}
              </section>

              {NARRATIVE_SECTIONS.map(([key, heading]) => (
                <section key={key} className={sectionCls}>
                  <h3 className={headingCls}>
                    <label htmlFor={`app-${key}`}>{heading}</label>
                  </h3>
                  <textarea
                    id={`app-${key}`}
                    rows={4}
                    className={`${field} resize-y`}
                    value={draft[key]}
                    onChange={(e) => setText(key, e.target.value)}
                  />
                </section>
              ))}

              <section className={sectionCls} aria-labelledby="sec-9">
                <h3 id="sec-9" className={headingCls}>
                  9. Plan działania i koszty
                </h3>
                <PlanEditor plan={draft.action_plan} onChange={(plan) => edit((d) => ({ ...d, action_plan: plan }))} />
              </section>

              <section className={sectionCls}>
                <h3 className={headingCls}>
                  <label htmlFor="app-amount">10. Wnioskowana kwota grantu</label>
                </h3>
                <div className="sm:max-w-xs">
                  <MoneyInput
                    id="app-amount"
                    value={amount}
                    onChange={setAmount}
                    className={field}
                    invalid={amountA11y["aria-invalid"]}
                    describedBy={amountA11y["aria-describedby"]}
                  />
                </div>
                <FieldError errors={errors} id="app-amount" />
                {planTotal > 0 && (
                  <div className="flex flex-wrap items-center gap-space-sm">
                    <p id="amount-hint" className="text-body-md text-on-surface-variant">
                      Suma kosztów z planu (sekcja 9): <strong className="text-on-surface">{fmtZl(planTotal)}</strong>
                    </p>
                    {amount !== planTotal && (
                      <button type="button" className={secondaryBtn} onClick={() => setAmount(planTotal)}>
                        Wstaw sumę z planu
                      </button>
                    )}
                  </div>
                )}
              </section>

              <section className={sectionCls}>
                <h3 className={headingCls}>
                  <label htmlFor="app-team">11. Zespół projektowy i doświadczenie</label>
                </h3>
                <textarea
                  id="app-team"
                  rows={3}
                  className={`${field} resize-y`}
                  value={draft.team}
                  onChange={(e) => setText("team", e.target.value)}
                />
              </section>

              <section className={sectionCls} aria-labelledby="sec-12">
                <h3 id="sec-12" className={headingCls}>
                  12. Oświadczenia
                </h3>
                {declError && (
                  <p id="decl-err" className="text-body-md font-semibold text-error">
                    {declError[1]}
                  </p>
                )}
                <label className="flex min-h-12 items-center gap-space-sm rounded-lg bg-surface-container-low px-space-sm text-body-md font-bold text-primary hc-edge">
                  <input
                    id="decl-all"
                    type="checkbox"
                    className="size-6 shrink-0 accent-primary-container"
                    checked={declTicked === declKeys.length}
                    ref={(el) => {
                      if (el) el.indeterminate = declTicked > 0 && declTicked < declKeys.length;
                    }}
                    aria-describedby={declError ? "decl-err" : undefined}
                    onChange={(e) => {
                      const on = e.target.checked;
                      edit((d) => ({
                        ...d,
                        declarations: { ...d.declarations, ...Object.fromEntries(declKeys.map((k) => [k, on])) },
                      }));
                    }}
                  />
                  <span>
                    Składam wszystkie poniższe oświadczenia ({declTicked} z {declKeys.length})
                  </span>
                </label>
                <ul className="flex flex-col gap-space-xs">
                  {declKeys.map((key) => (
                    <li key={key}>
                      <label className="flex min-h-12 items-start gap-space-sm text-body-md text-on-surface">
                        <input
                          id={`decl-${key}`}
                          type="checkbox"
                          className="mt-0.5 size-6 shrink-0 accent-primary-container"
                          checked={Boolean(draft.declarations[key])}
                          aria-describedby={declError && !draft.declarations[key] ? "decl-err" : undefined}
                          onChange={(e) =>
                            edit((d) => ({ ...d, declarations: { ...d.declarations, [key]: e.target.checked } }))
                          }
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
            <button type="button" onClick={requestClose} className={textBtn}>
              {draft?.status === "submitted" ? "Zamknij" : "Anuluj"}
            </button>
            {!draft ? (
              <div className="flex w-full flex-col gap-space-xs sm:flex-row sm:flex-wrap sm:justify-end">
                <button type="button" disabled={busy} onClick={() => startDraft(false)} className={secondaryBtn}>
                  {busy && busyLabel.includes("pusty") ? "Otwieram…" : "Pomiń generację — wypełnię sam/a"}
                </button>
                <button type="button" disabled={busy} onClick={() => startDraft(true)} className={primaryBtn}>
                  <Icon name="auto_awesome" size={22} />
                  {busy && busyLabel.includes("AI") ? "Generuję…" : "Wygeneruj szkic AI"}
                </button>
              </div>
            ) : draft.status !== "submitted" ? (
              <>
                <button type="button" disabled={busy} onClick={() => save(false)} className={secondaryBtn}>
                  {busy ? "Zapisuję…" : "Zapisz szkic"}
                </button>
                <button type="button" disabled={busy} onClick={() => save(true)} className={primaryBtn}>
                  <Icon name="send" size={22} />
                  {busy ? "Wysyłam…" : "Wyślij wniosek"}
                </button>
              </>
            ) : null}
          </div>
        </footer>

        {confirmClose && (
          <div className="absolute inset-0 z-20 flex items-center justify-center bg-on-surface/40 p-space-md">
            <div
              role="alertdialog"
              aria-modal="true"
              aria-labelledby="close-h"
              aria-describedby="close-d"
              className="flex w-full max-w-md flex-col gap-space-sm rounded-xl bg-surface p-space-md shadow-2xl hc-edge"
            >
              <h3 id="close-h" className={headingCls}>
                Masz niezapisane zmiany
              </h3>
              <p id="close-d" className="text-body-md text-on-surface">
                Zapisać szkic wniosku przed zamknięciem?
              </p>
              <div className="flex flex-col gap-space-xs sm:flex-row-reverse sm:flex-wrap">
                <button ref={confirmRef} type="button" onClick={() => void saveAndClose()} className={primaryBtn}>
                  Zapisz i zamknij
                </button>
                <button type="button" onClick={onClose} className={secondaryBtn}>
                  Zamknij bez zapisu
                </button>
                <button type="button" onClick={() => setConfirmClose(false)} className={textBtn}>
                  Wróć do edycji
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// module scope: a component declared inside another is a new type on every render,
// which remounted the inputs and dropped focus after each keystroke
function StepList({
  label,
  listKey,
  steps,
  onChange,
}: {
  label: string;
  listKey: StepKey;
  steps: PlanStep[];
  onChange: (steps: PlanStep[]) => void;
}) {
  function patch(idx: number, change: Partial<PlanStep>) {
    onChange(steps.map((s, i) => (i === idx ? { ...s, ...change } : s)));
  }

  return (
    <fieldset className="flex flex-col gap-space-xs">
      <legend className="mb-space-xs text-body-md font-bold text-primary">{label}</legend>
      {steps.length === 0 && <p className="text-body-md text-on-surface-variant">Brak działań.</p>}
      {steps.map((step, idx) => {
        const base = `${listKey}-${idx}`;
        return (
          <div
            key={base}
            className="grid grid-cols-1 gap-space-xs rounded-lg border border-outline-variant/30 p-space-sm sm:grid-cols-[2fr_1fr_1fr_auto] sm:items-end"
          >
            <div className="flex flex-col gap-1">
              <label className={labelCls} htmlFor={`${base}-action`}>
                Działanie
              </label>
              <input
                id={`${base}-action`}
                className={field}
                value={step.action}
                onChange={(e) => patch(idx, { action: e.target.value })}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className={labelCls} htmlFor={`${base}-timeline`}>
                Termin
              </label>
              <input
                id={`${base}-timeline`}
                className={field}
                placeholder="np. 03.2027"
                value={step.timeline}
                onChange={(e) => patch(idx, { timeline: e.target.value })}
              />
            </div>
            <div className="flex flex-col gap-1">
              <label className={labelCls} htmlFor={`${base}-cost`}>
                Koszt
              </label>
              <MoneyInput
                id={`${base}-cost`}
                className={field}
                value={step.cost_pln}
                onChange={(v) =>
                  patch(idx, {
                    cost_pln: v,
                    note: v !== null && step.note === ESTIMATE_NOTE ? null : step.note,
                  })
                }
              />
            </div>
            <button
              type="button"
              className="flex min-h-12 items-center justify-center gap-1 rounded-lg px-space-sm text-body-md font-bold text-error hover:bg-surface-container-high"
              onClick={() => onChange(steps.filter((_, i) => i !== idx))}
            >
              <Icon name="close" />
              Usuń
              <span className="sr-only">
                {" "}
                działanie {idx + 1} ({label})
              </span>
            </button>
          </div>
        );
      })}
      <div className="flex flex-wrap items-center justify-between gap-space-xs">
        <button
          type="button"
          className="min-h-12 rounded-lg px-space-md text-body-md font-bold text-primary hover:bg-surface-container-high"
          onClick={() => onChange([...steps, emptyStep()])}
        >
          + Dodaj działanie
          <span className="sr-only"> ({label})</span>
        </button>
        <p className="text-body-md font-semibold text-on-surface">Razem: {fmtZl(sumSteps(steps))}</p>
      </div>
    </fieldset>
  );
}

function PlanEditor({ plan, onChange }: { plan: ActionPlan; onChange: (p: ActionPlan) => void }) {
  const steps = (key: StepKey) => ({
    listKey: key,
    steps: plan[key] ?? [],
    onChange: (next: PlanStep[]) => onChange({ ...plan, [key]: next }),
  });

  return (
    <div className="flex flex-col gap-space-md">
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
      <StepList label="Przygotowanie — kroki" {...steps("preparation")} />
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
      <StepList label="Faza I testu" {...steps("testing_phase_1")} />
      <StepList label="Faza II testu" {...steps("testing_phase_2")} />
      <p className="text-body-lg font-semibold text-primary">Łączny koszt planu: {fmtZl(sumPlan(plan))}</p>
    </div>
  );
}
