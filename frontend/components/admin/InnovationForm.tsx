"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import {
  adminApi,
  ApiError,
  MAX_PDF_BYTES,
  type AdminInnovation,
  type ChallengeArea,
  type InnovationUpdate,
  type InnovationUploaded,
} from "@/lib/api";
import { AREA_LABEL } from "@/lib/labels";
import { Icon } from "@/components/Icon";
import { card, field, ghostBtn, h2, primaryBtn } from "@/components/admin/styles";

const LIMITS = { title: 300, summary: 5000, city: 200, page_url: 2000 };
const POLL_MS = 3000;
const POLL_FOR_MS = 90_000;

type Field = "title" | "summary" | "areas" | "page_url" | "pdf";
type Errors = Partial<Record<Field, string>>;

interface Values {
  title: string;
  summary: string;
  areas: ChallengeArea[];
  city: string;
  page_url: string;
  tags: string;
}

const EMPTY: Values = { title: "", summary: "", areas: [], city: "", page_url: "", tags: "" };

function toValues(i: AdminInnovation): Values {
  return { title: i.title, summary: i.summary, areas: i.challenge_areas, city: i.city, page_url: i.page_url ?? "", tags: "" };
}

// only changed fields go into the PATCH; an emptied link is sent as null to clear it
function changes(base: AdminInnovation, v: Values): InnovationUpdate {
  const out: InnovationUpdate = {};
  const title = v.title.trim();
  const summary = v.summary.trim();
  const city = v.city.trim();
  const pageUrl = v.page_url.trim() || null;
  if (title !== base.title) out.title = title;
  if (summary !== base.summary) out.summary = summary;
  if (city !== base.city) out.city = city;
  if (pageUrl !== (base.page_url ?? null)) out.page_url = pageUrl;
  const sameAreas =
    v.areas.length === base.challenge_areas.length && v.areas.every((a) => base.challenge_areas.includes(a));
  if (!sameAreas) out.challenge_areas = v.areas;
  return out;
}

// the summary links to these ids
const ID: Record<Field, string> = {
  title: "nowa-title",
  summary: "nowa-summary",
  areas: "nowa-area-0",
  page_url: "nowa-page-url",
  pdf: "nowa-pdf",
};

function validate(v: Values, pdf: File | null, needsPdf: boolean): Errors {
  const e: Errors = {};
  if (!v.title.trim()) e.title = "Podaj nazwę innowacji.";
  if (!v.summary.trim()) e.summary = "Podaj krótki opis.";
  if (v.areas.length === 0) e.areas = "Wybierz co najmniej jeden obszar wyzwań.";
  if (v.page_url.trim() && !/^https?:\/\/\S+$/i.test(v.page_url.trim()))
    e.page_url = "Link musi zaczynać się od http:// lub https://.";
  // editing: the pdf is optional, but a chosen file is checked the same way
  if (!needsPdf && !pdf) return e;
  if (!pdf) e.pdf = "Dołącz kartę innowacji w PDF.";
  else if (!/\.pdf$/i.test(pdf.name) && pdf.type !== "application/pdf") e.pdf = "Plik musi być w formacie PDF.";
  else if (pdf.size > MAX_PDF_BYTES) e.pdf = `Plik jest za duży: maksymalnie ${fmtSize(MAX_PDF_BYTES)}.`;
  return e;
}

// area:* and type:* are set by the backend from the form, so they are not typed by hand
function parseTags(raw: string): string[] {
  const tags = raw
    .split(",")
    .map((t) => t.trim())
    .filter((t) => t && !/^(area|type):/i.test(t));
  return [...new Set(tags)];
}

function serverError(err: unknown): string {
  if (!(err instanceof ApiError)) return "Nie udało się połączyć z API. Sprawdź połączenie i spróbuj ponownie.";
  if (err.status === 401) return "Sesja wygasła: odśwież stronę i zaloguj się ponownie. Wpisane dane zostaną utracone.";
  if (err.status === 404) return "Ta innowacja już nie istnieje. Wróć do listy.";
  if (err.status === 413) return `Plik PDF jest za duży: maksymalnie ${fmtSize(MAX_PDF_BYTES)}.`;
  if (err.status === 415) return "Przesłany plik nie jest prawidłowym PDF-em. Wybierz inny plik.";
  if (err.status === 422) return "Serwer odrzucił formularz. Sprawdź, czy wszystkie pola są poprawnie wypełnione.";
  return "Nie udało się zapisać innowacji. Spróbuj ponownie za chwilę.";
}

function fmtSize(bytes: number) {
  return `${(bytes / 1024 / 1024).toLocaleString("pl-PL", { maximumFractionDigits: 1 })} MB`;
}

// without `initial` it creates (multipart with the pdf), with it it edits (PATCH of the changed fields)
export function InnovationForm({ initial }: { initial?: AdminInnovation }) {
  const [saved, setSaved] = useState(initial);
  const [values, setValues] = useState<Values>(initial ? toValues(initial) : EMPTY);
  const [notice, setNotice] = useState("");
  const [pdf, setPdf] = useState<File | null>(null);
  const [errors, setErrors] = useState<Errors>({});
  const [failure, setFailure] = useState("");
  const [busy, setBusy] = useState(false);
  const [created, setCreated] = useState<InnovationUploaded | null>(null);
  const summaryRef = useRef<HTMLDivElement>(null);

  const set = <K extends keyof Values>(k: K, v: Values[K]) => setValues((prev) => ({ ...prev, [k]: v }));

  function toggleArea(a: ChallengeArea) {
    set("areas", values.areas.includes(a) ? values.areas.filter((x) => x !== a) : [...values.areas, a]);
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    const found = validate(values, pdf, !saved);
    setErrors(found);
    setFailure("");
    setNotice("");
    if (Object.keys(found).length > 0) {
      // after render, so the summary exists
      requestAnimationFrame(() => summaryRef.current?.focus());
      return;
    }
    if (saved) return save(saved);
    if (!pdf) return;
    setBusy(true);
    try {
      const res = await adminApi.createInnovation(
        {
          title: values.title.trim(),
          summary: values.summary.trim(),
          challenge_areas: values.areas,
          tags: parseTags(values.tags),
          city: values.city.trim(),
          page_url: values.page_url.trim() || null,
        },
        pdf,
      );
      setCreated(res);
    } catch (err) {
      setFailure(serverError(err));
      requestAnimationFrame(() => summaryRef.current?.focus());
    } finally {
      setBusy(false);
    }
  }

  async function save(base: AdminInnovation) {
    const body = changes(base, values);
    const hasChanges = Object.keys(body).length > 0;
    if (!hasChanges && !pdf) {
      setNotice("Brak zmian do zapisania.");
      return;
    }
    setBusy(true);
    try {
      const updated = hasChanges ? await adminApi.updateInnovation(base.id, body) : base;
      // 202: rag re-indexes the new card in the background; the download link serves it at once
      if (pdf) await adminApi.replaceInnovationPdf(base.id, pdf);
      setSaved(updated);
      setValues(toValues(updated));
      setPdf(null);
      setNotice(
        pdf
          ? "Zapisano zmiany. Nowa karta PDF jest już do pobrania; asystent przelicza dopasowania w tle."
          : "Zapisano zmiany.",
      );
    } catch (err) {
      setFailure(serverError(err));
      requestAnimationFrame(() => summaryRef.current?.focus());
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setValues(EMPTY);
    setPdf(null);
    setErrors({});
    setFailure("");
    setCreated(null);
  }

  if (created) return <Created innovation={created} onAnother={reset} />;

  const errorList = Object.entries(errors) as [Field, string][];
  const describe = (f: Field, hint?: string) =>
    [hint, errors[f] ? `${ID[f]}-err` : undefined].filter(Boolean).join(" ") || undefined;
  const backHref = saved ? `/admin/innowacje/${encodeURIComponent(saved.id)}` : "/admin";

  return (
    <section aria-labelledby="nowa-h" className={`${card} flex flex-col gap-space-md`}>
      <div className="flex flex-col gap-space-xs">
        <h2 id="nowa-h" className={h2}>
          <Icon name={saved ? "edit" : "add_circle"} size={28} />
          {saved ? `Edytuj: ${saved.title}` : "Dodaj innowację"}
        </h2>
        <p className="text-body-md text-on-surface-variant">
          {saved
            ? "Zmiany widać od razu w bibliotece i panelu. Asystent dopasowuje innowacje na podstawie karty PDF: zmiana opisu nie wpływa na dopasowania, nowa karta PDF tak."
            : "Innowacja zapisze się jako szkic. Po przetworzeniu karty PDF opublikuje się automatycznie i trafi do biblioteki oraz czatu."}{" "}
          Pola oznaczone gwiazdką (*) są wymagane.
        </p>
      </div>

      {(errorList.length > 0 || failure) && (
        <div
          ref={summaryRef}
          tabIndex={-1}
          role="alert"
          className="flex flex-col gap-space-xs rounded-lg border-2 border-error bg-surface-container-low p-space-md hc-edge"
        >
          <p className="flex items-center gap-2 text-body-lg font-semibold text-error">
            <Icon name="report_problem" />
            {failure || "Popraw formularz:"}
          </p>
          {errorList.length > 0 && (
            <ul className="flex list-disc flex-col gap-1 pl-space-md">
              {errorList.map(([f, msg]) => (
                <li key={f}>
                  <a href={`#${ID[f]}`} className="text-body-md text-on-surface underline underline-offset-4">
                    {msg}
                  </a>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      <form noValidate onSubmit={submit} className="flex flex-col gap-space-md">
        <div className="flex flex-col gap-1">
          <label htmlFor={ID.title} className="text-label-lg font-semibold text-primary">
            Nazwa innowacji *
          </label>
          <input
            id={ID.title}
            value={values.title}
            onChange={(e) => set("title", e.target.value)}
            required
            maxLength={LIMITS.title}
            aria-invalid={!!errors.title}
            aria-describedby={describe("title")}
            className={field}
          />
          <FieldError id={`${ID.title}-err`} msg={errors.title} />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor={ID.summary} className="text-label-lg font-semibold text-primary">
            Krótki opis *
          </label>
          <p id="nowa-summary-hint" className="text-body-md text-on-surface-variant">
            Jaki problem rozwiązuje, dla kogo i jak działa. Opis widać w bibliotece i pomaga w dopasowaniu.
          </p>
          <textarea
            id={ID.summary}
            value={values.summary}
            onChange={(e) => set("summary", e.target.value)}
            required
            rows={6}
            maxLength={LIMITS.summary}
            aria-invalid={!!errors.summary}
            aria-describedby={describe("summary", "nowa-summary-hint nowa-summary-count")}
            className={`${field} py-space-sm`}
          />
          <p id="nowa-summary-count" className="text-caption text-on-surface-variant">
            {values.summary.length} / {LIMITS.summary} znaków
          </p>
          <FieldError id={`${ID.summary}-err`} msg={errors.summary} />
        </div>

        <fieldset
          aria-invalid={!!errors.areas}
          aria-describedby={errors.areas ? "nowa-areas-err" : undefined}
          className="flex flex-col gap-space-xs"
        >
          <legend className="mb-space-xs text-label-lg font-semibold text-primary">Obszary wyzwań *</legend>
          <div className="grid grid-cols-1 gap-space-xs sm:grid-cols-2">
            {(Object.keys(AREA_LABEL) as ChallengeArea[]).map((a, i) => (
              <label
                key={a}
                htmlFor={`nowa-area-${i}`}
                className="flex min-h-12 cursor-pointer items-center gap-space-sm rounded-lg bg-surface-container-low px-space-sm text-body-md text-on-surface hc-edge"
              >
                <input
                  id={`nowa-area-${i}`}
                  type="checkbox"
                  checked={values.areas.includes(a)}
                  onChange={() => toggleArea(a)}
                  className="size-5 accent-primary"
                />
                {AREA_LABEL[a]}
              </label>
            ))}
          </div>
          <FieldError id="nowa-areas-err" msg={errors.areas} />
        </fieldset>

        <div className="grid grid-cols-1 gap-space-md sm:grid-cols-2">
          <div className="flex flex-col gap-1">
            <label htmlFor="nowa-city" className="text-label-lg font-semibold text-primary">
              Miejscowość wdrożenia
            </label>
            <input
              id="nowa-city"
              value={values.city}
              onChange={(e) => set("city", e.target.value)}
              maxLength={LIMITS.city}
              autoComplete="address-level2"
              className={field}
            />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor={ID.page_url} className="text-label-lg font-semibold text-primary">
              Link do strony lub filmu
            </label>
            <input
              id={ID.page_url}
              type="url"
              inputMode="url"
              placeholder="https://"
              value={values.page_url}
              onChange={(e) => set("page_url", e.target.value)}
              maxLength={LIMITS.page_url}
              aria-invalid={!!errors.page_url}
              aria-describedby={describe("page_url")}
              className={field}
            />
            <FieldError id={`${ID.page_url}-err`} msg={errors.page_url} />
          </div>
        </div>

        {saved && (
          <div className="flex flex-col gap-1">
            <label htmlFor={ID.pdf} className="text-label-lg font-semibold text-primary">
              Nowa karta innowacji (PDF, opcjonalnie)
            </label>
            <p id="nowa-pdf-hint" className="text-body-md text-on-surface-variant">
              Zastępuje obecny plik pod tym samym linkiem „Więcej informacji (PDF)”. Maksymalnie{" "}
              {fmtSize(MAX_PDF_BYTES)}.
            </p>
            <input
              id={ID.pdf}
              type="file"
              accept="application/pdf,.pdf"
              onChange={(e) => setPdf(e.target.files?.[0] ?? null)}
              aria-invalid={!!errors.pdf}
              aria-describedby={describe("pdf", "nowa-pdf-hint")}
              className={`${field} py-space-sm file:mr-space-sm file:min-h-10 file:rounded-lg file:border-0 file:bg-surface-container-high file:px-space-sm file:text-label-lg file:font-semibold file:text-primary`}
            />
            {pdf && (
              <p className="flex items-center gap-1 text-body-md text-on-surface">
                <Icon name="attach_file" size={18} />
                {pdf.name} ({fmtSize(pdf.size)})
              </p>
            )}
            <FieldError id={`${ID.pdf}-err`} msg={errors.pdf} />
          </div>
        )}

        {!saved && (
          <>
        <div className="flex flex-col gap-1">
          <label htmlFor="nowa-tags" className="text-label-lg font-semibold text-primary">
            Tagi
          </label>
          <p id="nowa-tags-hint" className="text-body-md text-on-surface-variant">
            Oddziel przecinkami, np. osoby niesłyszące, aktywizacja zawodowa.
          </p>
          <input
            id="nowa-tags"
            value={values.tags}
            onChange={(e) => set("tags", e.target.value)}
            aria-describedby="nowa-tags-hint"
            className={field}
          />
        </div>

        <div className="flex flex-col gap-1">
          <label htmlFor={ID.pdf} className="text-label-lg font-semibold text-primary">
            Karta innowacji (PDF) *
          </label>
          <p id="nowa-pdf-hint" className="text-body-md text-on-surface-variant">
            Pełny opis innowacji. Na jego podstawie asystent dopasowuje ją do problemów. Maksymalnie{" "}
            {fmtSize(MAX_PDF_BYTES)}.
          </p>
          <input
            id={ID.pdf}
            type="file"
            accept="application/pdf,.pdf"
            required
            onChange={(e) => setPdf(e.target.files?.[0] ?? null)}
            aria-invalid={!!errors.pdf}
            aria-describedby={describe("pdf", "nowa-pdf-hint")}
            className={`${field} py-space-sm file:mr-space-sm file:min-h-10 file:rounded-lg file:border-0 file:bg-surface-container-high file:px-space-sm file:text-label-lg file:font-semibold file:text-primary`}
          />
          {pdf && (
            <p className="flex items-center gap-1 text-body-md text-on-surface">
              <Icon name="attach_file" size={18} />
              {pdf.name} ({fmtSize(pdf.size)})
            </p>
          )}
          <FieldError id={`${ID.pdf}-err`} msg={errors.pdf} />
        </div>

          </>
        )}

        <div className="flex flex-wrap gap-space-sm">
          <button type="submit" disabled={busy} className={primaryBtn}>
            <Icon name={saved ? "check" : "add_circle"} />
            {busy ? (saved ? "Zapisuję…" : "Wysyłam…") : saved ? "Zapisz zmiany" : "Dodaj innowację"}
          </button>
          <Link href={backHref} className={ghostBtn}>
            {saved ? "Wróć do innowacji" : "Anuluj"}
          </Link>
        </div>
        <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
          {busy ? (saved ? "Zapisuję zmiany…" : "Wysyłam innowację i kartę PDF…") : notice}
        </p>
      </form>
    </section>
  );
}

function FieldError({ id, msg }: { id: string; msg: string | undefined }) {
  if (!msg) return null;
  return (
    <p id={id} className="flex items-center gap-1 text-body-md font-semibold text-error">
      <Icon name="info" size={18} />
      {msg}
    </p>
  );
}

type Phase = "indexing" | "published" | "timeout";

// the backend publishes after rag has embedded the pdf, but has no "failed" state,
// so a draft after the timeout may be slow or failed; the copy says both
function Created({ innovation, onAnother }: { innovation: InnovationUploaded; onAnother: () => void }) {
  const [phase, setPhase] = useState<Phase>(innovation.status === "published" ? "published" : "indexing");
  const headingRef = useRef<HTMLHeadingElement>(null);

  useEffect(() => {
    headingRef.current?.focus();
  }, []);

  useEffect(() => {
    if (phase !== "indexing") return;
    const deadline = Date.now() + POLL_FOR_MS;
    let live = true;
    const timer = setInterval(async () => {
      if (Date.now() > deadline) {
        clearInterval(timer);
        if (live) setPhase("timeout");
        return;
      }
      try {
        const row = await adminApi.innovation(innovation.id);
        if (live && row.status === "published") {
          clearInterval(timer);
          setPhase("published");
        }
      } catch {
        // a missed poll is retried on the next tick
      }
    }, POLL_MS);
    return () => {
      live = false;
      clearInterval(timer);
    };
  }, [innovation.id, phase]);

  const copy: Record<Phase, { icon: string; text: string }> = {
    indexing: {
      icon: "schedule",
      text: "Zapisano szkic. Przetwarzam kartę PDF – innowacja opublikuje się automatycznie, zwykle w ciągu minuty. Możesz zostać na tej stronie albo wrócić do listy.",
    },
    published: {
      icon: "verified",
      text: "Opublikowano. Innowacja jest widoczna w bibliotece i asystent może ją proponować w czacie.",
    },
    timeout: {
      icon: "info",
      text: "Innowacja jest wciąż szkicem: przetwarzanie PDF trwa dłużej albo się nie udało. Szkic nie jest widoczny dla mieszkańców. Sprawdź status na liście za kilka minut; jeśli się nie zmieni, dodaj innowację ponownie z innym plikiem PDF.",
    },
  };

  return (
    <section aria-labelledby="nowa-done-h" className={`${card} flex flex-col gap-space-md`}>
      <h2 id="nowa-done-h" ref={headingRef} tabIndex={-1} className={h2}>
        <Icon name={copy[phase].icon} size={28} />
        {innovation.title}
      </h2>
      <p role="status" className="text-body-lg text-on-surface">
        {copy[phase].text}
      </p>
      <div className="flex flex-wrap gap-space-sm">
        <Link href={`/admin/innowacje/${encodeURIComponent(innovation.id)}`} className={primaryBtn}>
          <Icon name="bar_chart" />
          Zobacz innowację w panelu
        </Link>
        <Link href="/admin" className={ghostBtn}>
          <Icon name="arrow_back" />
          Wróć do listy
        </Link>
        <button type="button" onClick={onAnother} className={ghostBtn}>
          <Icon name="add_circle" />
          Dodaj kolejną
        </button>
      </div>
    </section>
  );
}

// /admin/innowacje/{id}/edytuj: loads the row, then the same form in edit mode
export function InnovationEdit({ id }: { id: string }) {
  const [state, setState] = useState<AdminInnovation | "loading" | "missing" | "error">("loading");

  useEffect(() => {
    let live = true;
    adminApi
      .innovation(id)
      .then((i) => live && setState(i))
      .catch((err: unknown) => live && setState(err instanceof ApiError && err.status === 404 ? "missing" : "error"));
    return () => {
      live = false;
    };
  }, [id]);

  if (typeof state === "object") return <InnovationForm initial={state} />;
  if (state === "loading")
    return (
      <p role="status" className="py-space-lg text-body-lg text-on-surface-variant">
        Wczytuję innowację…
      </p>
    );
  return (
    <section className={`${card} flex flex-col gap-space-sm`}>
      <h2 className={h2}>{state === "missing" ? "Nie znaleziono innowacji" : "Nie udało się wczytać innowacji"}</h2>
      <p className="text-body-md text-on-surface-variant">
        {state === "missing"
          ? "Mogła zostać usunięta. Wróć do listy."
          : "Edycja wymaga połączenia z API. Odśwież stronę lub spróbuj za chwilę."}
      </p>
      <Link href="/admin" className={`${ghostBtn} self-start`}>
        <Icon name="arrow_back" />
        Wróć do listy
      </Link>
    </section>
  );
}
