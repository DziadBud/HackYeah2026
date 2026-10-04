"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "@/components/Icon";

const TABS = [
  { href: "/admin", label: "Innowacje i statystyki", icon: "bar_chart" },
  { href: "/admin/zgloszenia#forum", label: "Zgłoszenia i forum", icon: "forum" },
  { href: "/admin/testerzy", label: "Zgłoszenia do testów", icon: "how_to_reg" },
  { href: "/admin/wnioski", label: "Wnioski o grant", icon: "description" },
];

function isActive(pathname: string, href: string) {
  const path = href.split("#")[0] ?? href;
  return path === "/admin" ? pathname === "/admin" || pathname.startsWith("/admin/innowacje") : pathname.startsWith(path);
}

export function AdminNav() {
  const pathname = usePathname();
  return (
    <nav aria-label="Panel administratora">
      <ul className="flex flex-wrap gap-space-xs">
        {TABS.map((t) => (
          <li key={t.href}>
            <Link
              href={t.href}
              aria-current={isActive(pathname, t.href) ? "page" : undefined}
              className="flex min-h-12 items-center gap-space-xs rounded-lg bg-surface-container px-space-md text-label-lg font-semibold text-primary hover:bg-surface-container-high aria-[current=page]:bg-primary-container aria-[current=page]:text-on-primary hc-edge"
            >
              <Icon name={t.icon} />
              {t.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
