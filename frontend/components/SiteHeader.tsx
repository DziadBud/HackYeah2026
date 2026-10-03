"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "@/components/Icon";

// only two sections, so a segmented switch instead of a drawer
const NAV: { label: string; short: string; icon: string; href: string }[] = [
  { label: "Zapytaj asystenta", short: "Asystent", icon: "smart_toy", href: "/" },
  { label: "Biblioteka innowacji", short: "Biblioteka", icon: "lightbulb", href: "/innowacje" },
];

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

export function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 w-full bg-surface/95 shadow-sm backdrop-blur-xl hc-edge">
      <div className="mx-auto flex min-h-20 max-w-7xl flex-wrap items-center justify-between gap-x-space-md gap-y-space-xs px-gutter-sm py-2 sm:flex-nowrap sm:px-gutter">
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
        <nav aria-label="Główna" className="w-full shrink-0 sm:w-auto">
          <ul className="flex rounded-full bg-surface-container p-1 hc-edge">
            {NAV.map((n) => (
              <li key={n.href} className="flex-1 sm:flex-none">
                <Link
                  href={n.href}
                  aria-current={isActive(pathname, n.href) ? "page" : undefined}
                  className="flex min-h-12 items-center justify-center gap-2 whitespace-nowrap rounded-full px-space-md text-label-lg font-semibold text-on-surface-variant hover:bg-surface-container-highest hover:text-primary aria-[current=page]:bg-primary-container aria-[current=page]:text-on-primary aria-[current=page]:shadow-sm"
                >
                  <Icon name={n.icon} size={22} />
                  <span className="lg:hidden">{n.short}</span>
                  <span className="hidden lg:inline">{n.label}</span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>
    </header>
  );
}
