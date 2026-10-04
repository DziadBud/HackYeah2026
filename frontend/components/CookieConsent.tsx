"use client";

import { useEffect, useId, useState } from "react";
import { Icon } from "@/components/Icon";

export const COOKIE_CONSENT_KEY = "cookie-consent";

/** `necessary` = only required storage; `all` reserved if optional cookies are added later. */
export type CookieConsentChoice = "all" | "necessary";

function readChoice(): CookieConsentChoice | null {
  try {
    const v = localStorage.getItem(COOKIE_CONSENT_KEY);
    if (v === "all" || v === "necessary") return v;
  } catch {
    // private mode / blocked storage
  }
  return null;
}

function writeChoice(choice: CookieConsentChoice) {
  try {
    localStorage.setItem(COOKIE_CONSENT_KEY, choice);
  } catch {
    // still dismiss for this session
  }
}

export function CookieConsent() {
  const [open, setOpen] = useState(false);
  const titleId = useId();
  const descId = useId();

  useEffect(() => {
    if (!readChoice()) setOpen(true);
  }, []);

  function choose(choice: CookieConsentChoice) {
    writeChoice(choice);
    setOpen(false);
  }

  if (!open) return null;

  return (
    <div
      role="region"
      aria-labelledby={titleId}
      aria-describedby={descId}
      className="fixed inset-x-0 bottom-0 z-50 p-space-sm sm:p-space-md"
    >
      <div className="mx-auto flex max-w-3xl flex-col gap-space-sm rounded-xl border border-outline bg-surface-container-lowest p-space-md shadow-xl hc-edge sm:p-space-lg">
        <div className="flex items-start gap-space-sm">
          <span
            aria-hidden="true"
            className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-surface-container text-primary"
          >
            <Icon name="info" size={22} />
          </span>
          <div className="flex min-w-0 flex-col gap-1">
            <h2 id={titleId} className="text-headline-sm font-semibold text-primary">
              Pliki cookies i dane w przeglądarce
            </h2>
            <p id={descId} className="text-body-md text-on-surface-variant">
              Serwis korzysta wyłącznie z niezbędnych mechanizmów: cookie sesji administratora (po
              zalogowaniu) oraz zapis preferencji dostępności i tej zgody w pamięci przeglądarki
              (localStorage). Nie używamy cookies reklamowych ani analitycznych. Twój wybór zapamiętujemy
              w tej przeglądarce.
            </p>
          </div>
        </div>
        <div className="flex flex-col gap-space-xs sm:flex-row sm:flex-wrap sm:justify-end">
          <button
            type="button"
            onClick={() => choose("necessary")}
            className="flex min-h-12 items-center justify-center rounded-lg bg-surface-container-high px-space-md text-label-lg font-semibold text-primary hover:bg-surface-container-highest hc-edge"
          >
            Tylko niezbędne
          </button>
          <button
            type="button"
            onClick={() => choose("all")}
            className="flex min-h-12 items-center justify-center rounded-lg bg-primary px-space-md text-label-lg font-semibold text-on-primary hover:bg-primary-container"
          >
            Akceptuję
          </button>
        </div>
      </div>
    </div>
  );
}
