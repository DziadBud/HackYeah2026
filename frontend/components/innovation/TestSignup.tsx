"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";

const field =
  "min-h-12 rounded-lg border-[1.5px] border-outline bg-surface-container-lowest px-4 text-body-md text-on-surface";

// sign-up for testing (Tester innowacji). email is optional: without it the
// backend hands out a status link instead (see notifications-without-accounts.md)
export function TestSignup({ title }: { title: string }) {
  const [sent, setSent] = useState(false);

  return (
    <section
      id="zglos-do-testow"
      aria-labelledby="test-signup-heading"
      tabIndex={-1}
      className="flex scroll-mt-28 flex-col gap-space-md rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge lg:p-space-lg"
    >
      <h2 id="test-signup-heading" className="flex items-center gap-2 text-headline-sm font-semibold text-primary">
        <Icon name="how_to_reg" size={24} />
        Zgłoś się do testowania
      </h2>
      {sent ? (
        <p role="status" className="text-body-md text-on-surface">
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
          <p className="text-body-md text-on-surface-variant">
            Przetestuj rozwiązanie w swojej gminie lub instytucji i pomóż je ulepszyć.
          </p>
          <div className="flex flex-col gap-1">
            <label htmlFor="tester-location" className="text-label-lg font-semibold text-primary">
              Gmina lub instytucja (wymagane)
            </label>
            <input id="tester-location" required className={field} placeholder="np. GOPS Iwanowice" />
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="tester-email" className="text-label-lg font-semibold text-primary">
              E-mail do powiadomień (opcjonalnie)
            </label>
            <input id="tester-email" type="email" autoComplete="email" className={field} aria-describedby="tester-email-hint" />
            <p id="tester-email-hint" className="text-caption text-on-surface-variant">
              Bez adresu dostaniesz link do sprawdzania statusu zgłoszenia.
            </p>
          </div>
          <label className="flex min-h-12 items-start gap-space-sm text-body-md text-on-surface">
            <input type="checkbox" required className="mt-0.5 size-6 shrink-0 accent-primary-container" />
            <span>Zgadzam się na kontakt w sprawie testów tej innowacji (wymagane).</span>
          </label>
          <button
            type="submit"
            className="flex min-h-12 items-center justify-center gap-2 rounded-xl bg-secondary px-space-md text-label-lg font-semibold text-on-secondary hover:bg-secondary-hover"
          >
            <Icon name="send" />
            Wyślij zgłoszenie
          </button>
        </form>
      )}
    </section>
  );
}
