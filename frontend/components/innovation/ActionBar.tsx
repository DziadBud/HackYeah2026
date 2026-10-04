"use client";

import { useEffect, useId, useRef, useState } from "react";
import { api, ApiError } from "@/lib/api";
import { Icon } from "@/components/Icon";

const field =
  "min-h-12 w-full rounded-lg border-[1.5px] border-outline bg-surface p-space-sm text-body-md text-on-surface";

export function ActionBar({ innovationId, pdfUrl, title }: { innovationId: string; pdfUrl: string; title: string }) {
  const [copied, setCopied] = useState(false);
  const [formOpen, setFormOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const emailRef = useRef<HTMLInputElement>(null);
  const formId = useId();

  useEffect(() => {
    if (!formOpen) return;
    emailRef.current?.focus();
  }, [formOpen]);

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="flex flex-col gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
      <div className="flex flex-col items-stretch gap-space-sm sm:flex-row sm:flex-wrap sm:items-center">
        <button
          type="button"
          aria-expanded={formOpen}
          aria-controls={formId}
          onClick={() => {
            setFormOpen((v) => !v);
            setError("");
            setStatus("");
          }}
          className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-secondary px-space-md py-2 text-center text-label-lg font-semibold text-on-secondary shadow-sm hover:bg-secondary-hover"
        >
          <Icon name="how_to_reg" size={22} />
          <span>Zgłoś się do testowania</span>
        </button>
        <a
          href={pdfUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-surface-container-lowest px-space-md py-2 text-center text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge"
        >
          <Icon name="info" size={22} />
          <span>
            Więcej informacji (PDF)
            <span className="sr-only">, otwiera się w nowej karcie</span>
          </span>
        </a>
        <button
          type="button"
          onClick={copyLink}
          className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-surface-container-lowest px-space-md py-2 text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge"
        >
          <Icon name="content_copy" size={22} />
          <span>Skopiuj link do tej strony</span>
        </button>
        <span role="status" className="text-body-md font-semibold text-primary">
          {copied ? "Skopiowano link." : ""}
        </span>
      </div>

      {formOpen && (
        <form
          id={formId}
          className="flex flex-col gap-space-sm rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge"
          onSubmit={async (e) => {
            e.preventDefault();
            const mail = email.trim();
            if (!mail) {
              setError("Podaj adres e-mail, na który ROPS ma się odezwać.");
              return;
            }
            setBusy(true);
            setError("");
            setStatus("");
            try {
              await api.signUpForTest(innovationId, { email: mail, consent: true });
              setStatus(
                "Dziękujemy! ROPS przejrzy zgłoszenie i napisze na podany e-mail, czy możesz przetestować tę innowację.",
              );
              setEmail("");
              setFormOpen(false);
            } catch (err) {
              setError(
                err instanceof ApiError && err.status === 404
                  ? "Ta innowacja nie przyjmuje teraz zgłoszeń do testów."
                  : "Nie udało się wysłać zgłoszenia. Sprawdź połączenie i spróbuj ponownie.",
              );
            } finally {
              setBusy(false);
            }
          }}
        >
          <h2 className="flex items-center gap-2 text-headline-sm font-semibold text-primary">
            <Icon name="mail" size={22} />
            Zostaw e-mail do kontaktu
          </h2>
          <p className="text-body-md text-on-surface-variant">
            Koordynator ROPS przejrzy zgłoszenie. O decyzji w sprawie testów innowacji „{title}” dowiesz się
            mailowo.
          </p>
          <div className="flex flex-col gap-1">
            <label htmlFor={`${formId}-email`} className="text-label-lg font-semibold text-primary">
              Adres e-mail
            </label>
            <input
              ref={emailRef}
              id={`${formId}-email`}
              type="email"
              required
              maxLength={254}
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={field}
              placeholder="twoj.email@instytucja.pl"
            />
          </div>
          <label className="flex min-h-12 items-start gap-space-sm text-body-md text-on-surface">
            <input type="checkbox" required className="mt-0.5 size-6 shrink-0 accent-primary-container" />
            <span>Zgadzam się na kontakt ROPS w sprawie testowania tej innowacji.</span>
          </label>
          <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
            {error || status}
          </p>
          <div className="flex flex-wrap justify-end gap-space-xs">
            <button
              type="button"
              onClick={() => {
                setFormOpen(false);
                setError("");
              }}
              className="min-h-12 rounded-lg px-space-md text-body-md font-bold text-on-surface-variant hover:bg-surface-container-high"
            >
              Anuluj
            </button>
            <button
              type="submit"
              disabled={busy}
              className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-secondary px-space-md text-label-lg font-semibold text-on-secondary hover:bg-secondary-hover disabled:cursor-wait disabled:opacity-80"
            >
              <Icon name="send" />
              Wyślij zgłoszenie
            </button>
          </div>
        </form>
      )}

      {!formOpen && status && (
        <p role="status" className="text-body-md font-semibold text-primary">
          {status}
        </p>
      )}
    </div>
  );
}
