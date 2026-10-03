import Link from "next/link";
import { Icon } from "@/components/Icon";

// the public ui has no test sign-up of its own: this opens the "Złóż wniosek" form (POST /ideas)
// on the chat page, and ROPS follows up from the admin inbox
export function TestSignup({ title }: { title: string }) {
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
      <p className="text-body-md text-on-surface-variant">
        Chcesz przetestować „{title}” lub podobne rozwiązanie w swojej gminie lub instytucji? Złóż wniosek do ROPS:
        opisz, czego potrzebujecie, i zostaw e-mail. Koordynator ROPS odezwie się z propozycją testów.
      </p>
      <Link
        href="/?wniosek=1"
        className="flex min-h-12 items-center justify-center gap-2 rounded-xl bg-secondary px-space-md text-label-lg font-semibold text-on-secondary hover:bg-secondary-hover"
      >
        <Icon name="send" />
        Złóż wniosek
      </Link>
    </section>
  );
}
