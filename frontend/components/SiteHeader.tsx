"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";
import { Icon } from "@/components/Icon";

const NAV: { label: string; href: string }[] = [
  { label: "Strona główna – zapytaj asystenta", href: "/" },
  { label: "Biblioteka innowacji", href: "/innowacje" },
];

// planned sections, listed so the drawer shows where the hub is going
const SOON = ["Mapa wyzwań Małopolski", "Moje zgłoszenia"];

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
    "min-h-12 px-space-md flex items-center rounded-lg text-body-lg font-semibold text-on-surface hover:bg-surface-container-high aria-[current=page]:bg-primary-container aria-[current=page]:font-bold aria-[current=page]:text-on-primary";

  return (
    <header className="sticky top-0 z-40 w-full bg-surface/95 shadow-sm backdrop-blur-xl hc-edge">
      <div className="mx-auto flex min-h-20 max-w-7xl items-center justify-between gap-space-sm px-gutter-sm sm:px-gutter">
        <Link href="/" className="flex min-w-0 items-center gap-space-sm rounded-lg py-2 sm:gap-space-md">
          {/* eslint-disable-next-line @next/next/no-img-element -- static svg logo; only the mark is shown, the name is real text */}
          <img src="/logo.svg" alt="" width={40} height={40} className="size-10 shrink-0 object-cover object-left" />
          <span className="flex min-w-0 flex-col">
            <span className="text-label-lg font-bold leading-tight text-primary md:text-headline-sm md:font-semibold">
              Małopolski Hub Innowacji Społecznych
            </span>
            <span className="hidden text-label-md font-semibold leading-tight text-on-surface-variant md:block">
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
        <div className="flex h-full flex-col">
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
                  <li key={n.href}>
                    <Link href={n.href} className={item} aria-current={isActive(pathname, n.href) ? "page" : undefined}>
                      {n.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
            <h3 className="mt-space-lg px-space-md text-label-md font-semibold text-on-surface-variant">Wkrótce</h3>
            <ul className="flex flex-col gap-1">
              {SOON.map((label) => (
                <li key={label} className="flex min-h-12 items-center px-space-md text-body-md text-on-surface-variant">
                  {label}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </dialog>
    </header>
  );
}
