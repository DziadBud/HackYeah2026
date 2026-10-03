import Link from "next/link";

// compact footer so chat stays the main focus of the viewport
export function SiteFooter() {
  return (
    <footer className="mt-auto w-full py-space-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-center px-gutter-sm sm:px-gutter">
        <Link
          href="/deklaracja-dostepnosci"
          className="flex min-h-12 items-center px-space-sm text-body-md font-semibold text-on-surface-variant underline-offset-4 hover:text-primary hover:underline"
        >
          Deklaracja dostępności
        </Link>
      </div>
    </footer>
  );
}
