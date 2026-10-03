import type { Metadata } from "next";
import Link from "next/link";
import { LibraryList } from "@/components/innovation/LibraryList";

export const metadata: Metadata = { title: "Biblioteka innowacji" };

export default function LibraryPage() {
  return (
    <div className="flex flex-col gap-space-lg py-space-md">
      <nav aria-label="Ścieżka powrotu">
        <ol className="flex flex-wrap items-center gap-space-xs text-body-md text-on-surface-variant">
          <li>
            <Link href="/" className="flex min-h-12 items-center rounded px-1 underline hover:text-primary">
              Strona główna
            </Link>
          </li>
          <li aria-hidden="true">›</li>
          <li aria-current="page" className="flex min-h-12 items-center font-bold text-primary">
            Biblioteka innowacji
          </li>
        </ol>
      </nav>
      <header className="flex flex-col gap-space-xs">
        <h1 className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">
          Biblioteka innowacji
        </h1>
        <p className="max-w-3xl text-body-lg text-on-surface-variant">
          Przetestowane rozwiązania z Małopolski, gotowe do wdrożenia w gminie, organizacji lub instytucji. Nie wiesz,
          czego szukać?{" "}
          <Link href="/" className="font-bold text-primary underline">
            Opisz problem w czacie
          </Link>
          , a asystent dobierze innowacje za Ciebie.
        </p>
      </header>
      <LibraryList />
    </div>
  );
}
