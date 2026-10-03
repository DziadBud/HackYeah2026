"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";

const field =
  "min-h-12 rounded-lg border border-outline bg-surface-container-lowest px-4 text-body-sm text-on-surface";

// sign-up for testing (Tester innowacji). email is optional: without it the
// backend hands out a status link instead (see notifications-without-accounts.md)
export function TestSignup({ title }: { title: string }) {
  const [sent, setSent] = useState(false);

  return (
    <section
      id="zglos-do-testow"
      aria-labelledby="test-signup-heading"
      tabIndex={-1}
      className="flex scroll-mt-28 flex-col gap-5 rounded-xl border border-border-subtle bg-surface-container-lowest p-6 shadow-sm hc-edge"
    >
      <h2 id="test-signup-heading" className="flex items-center gap-2 border-b border-border-subtle pb-3 text-headline-sm font-bold text-primary sm:text-[1.25rem]">
        <Icon name="how_to_reg" size={24} />
        Zgłoś się do testowania
      </h2>
      {sent ? (
        <p role="status" className="text-body-sm text-on-surface">
          Dziękujemy! Zgłoszenie do testów innowacji „{title}” zostało przyjęte. Koordynator ROPS odezwie się z
          informacją o terminie.
        </p>
      ) : (
        <form
          className="flex flex-col gap-space-sm"
          onSubmit={(e) => {
            e.preventDefault();
            setSent(true);
          }}
        >
          <p className="text-body-sm text-on-surface-variant">
            Przetestuj rozwiązanie w swojej gminie lub instytucji i pomóż je ulepszyć.
          </p>
          <div className="flex flex-col gap-1">
            <label htmlFor="tester-location" className="text-body-sm font-semibold text-primary">
              Gmina lub instytucja (wymagane)
            </label>
            <input id="tester-location" required className={field} placeholder="np. GOPS Iwanowice" />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="tester-email" className="text-body-sm font-semibold text-primary">
              E-mail do powiadomień (opcjonalnie)
            </label>
            <input id="tester-email" type="email" autoComplete="email" className={field} aria-describedby="tester-email-hint" />
            <p id="tester-email-hint" className="text-label-sm font-normal text-on-surface-variant">
              Bez adresu dostaniesz link do sprawdzania statusu zgłoszenia.
            </p>
          </div>
          <label className="flex min-h-12 items-start gap-space-sm text-body-sm text-on-surface">
            <input type="checkbox" required className="mt-0.5 size-5 shrink-0 accent-primary" />
            <span>Zgadzam się na kontakt w sprawie testów tej innowacji (wymagane).</span>
          </label>
          <button
            type="submit"
            className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-secondary px-4 text-label-md font-semibold text-on-secondary shadow-md hover:bg-secondary-hover"
          >
            <Icon name="send" />
            Wyślij zgłoszenie
          </button>
        </form>
      )}
    </section>
  );
}
