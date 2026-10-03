import type { Metadata } from "next";
import Link from "next/link";
import { Icon } from "@/components/Icon";
import { InnovationCard } from "@/components/InnovationCard";
import { INNOVATIONS, toInnovation } from "@/lib/demo-data";

export const metadata: Metadata = { title: "Biblioteka innowacji" };

type Props = { searchParams: Promise<{ q?: string }> };

export default async function LibraryPage({ searchParams }: Props) {
  const q = ((await searchParams).q ?? "").trim();
  const needle = q.toLowerCase();
  const found = needle
    ? INNOVATIONS.filter((i) =>
        [i.title, i.summary, i.problem, ...i.tags, ...i.keywords].join(" ").toLowerCase().includes(needle),
      )
    : INNOVATIONS;

  return (
    <div className="flex flex-col gap-6">
      <nav aria-label="Ścieżka powrotu">
        <ol className="flex flex-wrap items-center gap-1.5 text-body-sm text-on-surface-variant">
          <li>
            <Link href="/" className="flex min-h-10 items-center gap-1 rounded px-1.5 underline hover:text-primary">
              <Icon name="home" size={18} className="text-primary" />
              Strona główna
            </Link>
          </li>
          <li aria-hidden="true" className="flex items-center">
            <Icon name="chevron_right" size={18} />
          </li>
          <li aria-current="page" className="flex min-h-10 items-center font-bold text-primary">
            Biblioteka innowacji
          </li>
        </ol>
      </nav>
      <header className="flex flex-col gap-4 rounded-xl border border-border-subtle bg-surface-container-lowest p-6 shadow-sm hc-edge lg:p-8">
        <h1 className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">
          Biblioteka innowacji
        </h1>
        <p className="max-w-3xl text-body-md text-on-surface-variant">
          Przetestowane rozwiązania z Małopolski, gotowe do wdrożenia w gminie, organizacji lub instytucji. Nie wiesz,
          czego szukać?{" "}
          <Link href="/" className="font-bold text-primary underline">
            Opisz problem w czacie
          </Link>
          , a asystent dobierze innowacje za Ciebie.
        </p>
        <form id="szukaj" role="search" action="/innowacje" className="flex flex-col gap-1.5 sm:max-w-xl">
          <label htmlFor="library-q" className="text-body-sm font-bold text-primary">
            Szukaj w bibliotece
          </label>
          <div className="flex gap-2">
            <input
              id="library-q"
              name="q"
              type="search"
              defaultValue={q}
              placeholder="np. seniorzy, słuch, rehabilitacja"
              className="min-h-11 grow rounded-lg border border-outline bg-surface-container-lowest px-4 text-body-md text-on-surface"
            />
            <button
              type="submit"
              className="flex min-h-11 items-center gap-2 rounded-lg bg-primary px-5 text-label-md font-bold text-on-primary shadow-sm hover:bg-primary-hover"
            >
              <Icon name="search" />
              Szukaj
            </button>
          </div>
        </form>
      </header>
      <p role="status" className="text-body-sm text-on-surface-variant">
        {q ? `Wyniki dla „${q}”: ${found.length}` : `Wszystkie innowacje: ${found.length}`}
        {q && (
          <>
            {" · "}
            <Link href="/innowacje" className="font-semibold text-primary underline">
              Pokaż wszystkie
            </Link>
          </>
        )}
      </p>
      {found.length > 0 ? (
        <ul className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {found.map((i) => (
            <li key={i.id} className="flex">
              <InnovationCard innovation={toInnovation(i)} headingLevel="h2" />
            </li>
          ))}
        </ul>
      ) : (
        <p className="rounded-xl border border-border-subtle bg-surface-container-lowest p-6 text-body-md hc-edge">
          Nie znaleźliśmy innowacji dla tego hasła.{" "}
          <Link href="/" className="font-bold text-primary underline">
            Opisz problem w czacie
          </Link>{" "}
          albo zgłoś własny pomysł.
        </p>
      )}
    </div>
  );
}
