"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { Icon } from "@/components/Icon";

const NAV: { label: string; href?: string }[] = [
  { label: "Czat (Strona główna)", href: "/" },
  { label: "Biblioteka innowacji", href: "/innowacje" },
  { label: "Mapa wyzwań Małopolski" },
  { label: "Kreator pomysłów" },
  { label: "Testuj innowacje" },
  { label: "Moje zgłoszenia" },
];

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

export function SiteHeader() {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const pathname = usePathname();

  // close the drawer after navigating
  useEffect(() => {
    dialogRef.current?.close();
  }, [pathname]);

  const item =
    "min-h-12 px-space-md flex items-center rounded-lg text-body-lg text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface aria-[current=page]:bg-primary-container aria-[current=page]:font-bold aria-[current=page]:text-on-primary";

  return (
    <header className="sticky top-0 z-40 w-full bg-surface/95 shadow-[0_1px_8px_rgba(0,0,0,0.06)] backdrop-blur-xl hc-edge">
      <div className="mx-auto flex min-h-20 max-w-7xl items-center justify-between gap-space-sm px-gutter-sm sm:px-gutter">
        <Link href="/" className="flex min-w-0 items-center gap-space-sm rounded-lg py-2 sm:gap-space-md">
          {/* eslint-disable-next-line @next/next/no-img-element -- static svg logo */}
          <img src="/logo.svg" alt="" width={128} height={32} className="h-10 w-auto shrink-0 md:h-8" />
          {/* on phones the logo carries the name; the text stays for screen readers */}
          <span className="sr-only flex-col md:not-sr-only md:flex md:min-w-0">
            <span className="text-headline-sm font-semibold leading-tight text-primary">
              Małopolski Hub Innowacji Społecznych
            </span>
            <span className="text-label-md font-semibold leading-tight text-on-surface-variant">
              Regionalny Ośrodek Polityki Społecznej w Krakowie
            </span>
          </span>
        </Link>
        <div className="flex shrink-0 items-center gap-space-xs">
          <button
            type="button"
            aria-haspopup="dialog"
            aria-controls="site-menu"
            onClick={() => dialogRef.current?.showModal()}
            className="flex min-h-12 items-center gap-space-xs rounded-lg bg-primary-container px-space-md text-label-lg font-semibold text-on-primary hover:bg-primary"
          >
            <Icon name="menu" size={24} />
            <span>Menu</span>
          </button>
          <Link
            href="/admin"
            aria-label="Panel administratora"
            title="Panel administratora"
            className="flex size-12 items-center justify-center rounded-full"
          >
            <span className="flex size-8 items-center justify-center rounded-full bg-primary text-on-primary">
              <Icon name="person" size={18} />
            </span>
          </Link>
        </div>
      </div>

      <dialog
        ref={dialogRef}
        id="site-menu"
        aria-labelledby="site-menu-title"
        className="fixed inset-y-0 right-0 left-auto m-0 h-full max-h-none w-80 max-w-full bg-surface-container-lowest p-space-md text-on-surface shadow-[0_8px_24px_rgba(15,45,89,0.16)] backdrop:bg-black/40 hc-edge"
        onClick={(e) => {
          // click on the backdrop closes the drawer
          if (e.target === e.currentTarget) e.currentTarget.close();
        }}
      >
        <div className="flex h-full flex-col justify-between">
          <div className="flex flex-col">
            <div className="mb-space-sm flex items-center justify-between border-b border-surface-container-highest pb-space-sm">
              <div className="flex flex-col">
                <h2 id="site-menu-title" className="text-headline-sm font-semibold text-primary">
                  Nawigacja
                </h2>
                <span className="text-caption text-on-surface-variant">Małopolski Hub Innowacji</span>
              </div>
              <button
                type="button"
                aria-label="Zamknij menu"
                onClick={() => dialogRef.current?.close()}
                className="flex size-12 items-center justify-center rounded-lg text-on-surface hover:bg-surface-container-high"
              >
                <Icon name="close" size={28} />
              </button>
            </div>
            <nav aria-label="Główna">
              <ul className="flex flex-col gap-1">
                {NAV.map((n) => (
                  <li key={n.label}>
                    {n.href ? (
                      <Link
                        href={n.href}
                        className={item}
                        aria-current={isActive(pathname, n.href) ? "page" : undefined}
                      >
                        {n.label}
                      </Link>
                    ) : (
                      <span className="flex min-h-12 items-center justify-between gap-2 px-space-md text-body-lg text-on-surface-variant">
                        {n.label}
                        <span className="rounded bg-surface-container px-2 py-0.5 text-caption">wkrótce</span>
                      </span>
                    )}
                  </li>
                ))}
              </ul>
            </nav>
          </div>
          <div className="mt-space-md flex flex-col gap-space-xs border-t border-surface-container-highest pt-space-md">
            <div className="flex items-center justify-between px-space-xs">
              <span className="text-label-md font-semibold uppercase tracking-wider text-on-surface-variant">
                Strefa Urzędu
              </span>
              <span className="rounded bg-secondary-fixed px-2 py-0.5 text-caption font-bold text-on-secondary-fixed">
                tylko dla ROPS
              </span>
            </div>
            <nav aria-label="Strefa Urzędu">
              <Link
                href="/admin"
                className={item}
                aria-current={isActive(pathname, "/admin") ? "page" : undefined}
              >
                Panel administratora
              </Link>
            </nav>
          </div>
        </div>
      </dialog>
    </header>
  );
}
