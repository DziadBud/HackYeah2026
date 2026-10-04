import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mt-auto w-full border-t border-outline/20 bg-surface-container-low">
      <div className="mx-auto flex max-w-7xl flex-col gap-space-sm px-gutter-sm py-space-md sm:flex-row sm:items-center sm:justify-between sm:px-gutter">
        <p className="text-caption text-on-surface-variant">
          © 2026 Regionalny Ośrodek Polityki Społecznej w Krakowie. Wszelkie
          prawa zastrzeżone.
        </p>
        <Link
          href="/deklaracja-dostepnosci"
          className="flex min-h-12 items-center text-body-md font-semibold text-primary underline-offset-4 hover:underline sm:min-h-0"
        >
          Zgodność z WCAG 2.1 AA
        </Link>
      </div>
    </footer>
  );
}
