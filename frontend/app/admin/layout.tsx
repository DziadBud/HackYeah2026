import type { Metadata } from "next";
import { AdminNav } from "@/components/admin/AdminNav";

export const metadata: Metadata = {
  title: { default: "Panel administratora", template: "%s – Panel administratora" },
  robots: { index: false },
};

// login is off for the demo; the backend honours ADMIN_AUTH_DISABLED only in debug
export default function AdminLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="flex flex-col gap-space-lg py-space-md">
      <header className="flex flex-col gap-space-sm rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge lg:p-space-lg">
        <p className="flex flex-wrap items-center gap-2">
          <span className="rounded bg-secondary-fixed px-2 py-0.5 text-caption font-bold text-on-secondary-fixed">tylko dla ROPS</span>
          <span className="text-caption text-on-surface-variant">Logowanie wyłączone na czas demonstracji</span>
        </p>
        <h1 className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">Panel administratora</h1>
        <AdminNav />
      </header>
      {children}
    </div>
  );
}
