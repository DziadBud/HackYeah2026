import Link from "next/link";
import { Icon } from "@/components/Icon";

// testing is part of matching (POST /match?test_signup=true, .claude/designs/innovation-testing.md):
// there is no per-innovation sign-up, so this points to the chat with the tester option on
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
        Chcesz przetestować „{title}” lub podobne rozwiązanie w swojej gminie lub instytucji? Opisz w czacie problem, z
        którym się mierzycie, i zaznacz „Chcę testować”. Asystent dobierze pasujące innowacje, a koordynator ROPS
        odezwie się na podany adres e-mail.
      </p>
      <Link
        href="/?testuj=1"
        className="flex min-h-12 items-center justify-center gap-2 rounded-xl bg-secondary px-space-md text-label-lg font-semibold text-on-secondary hover:bg-secondary-hover"
      >
        <Icon name="send" />
        Opisz problem i zgłoś się do testów
      </Link>
    </section>
  );
}
