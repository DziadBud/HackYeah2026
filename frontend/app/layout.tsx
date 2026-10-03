import type { Metadata } from "next";
import Link from "next/link";
import "./globals.css";

export const metadata: Metadata = {
  title: "HackYeah – Innowacje społeczne",
  description: "Matchmaking problemów społecznych z innowacjami ROPS",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pl">
      <body className="min-h-screen antialiased">
        <header className="border-b border-black/10 dark:border-white/10">
          <nav className="mx-auto flex max-w-4xl items-center justify-between px-6 py-4">
            <Link href="/" className="font-semibold">
              HackYeah
            </Link>
            <div className="flex gap-4 text-sm">
              <Link href="/" className="hover:underline">
                Szukaj innowacji
              </Link>
              <Link href="/admin" className="hover:underline">
                Panel admina
              </Link>
            </div>
          </nav>
        </header>
        <main className="mx-auto max-w-4xl px-6 py-10">{children}</main>
      </body>
    </html>
  );
}
