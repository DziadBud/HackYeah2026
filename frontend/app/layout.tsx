import type { Metadata, Viewport } from "next";
import { Atkinson_Hyperlegible_Next } from "next/font/google";
import localFont from "next/font/local";
import { PREFS_BOOTSTRAP } from "@/components/A11yToolbar";
import { CookieConsent } from "@/components/CookieConsent";
import { SiteFooter } from "@/components/SiteFooter";
import { TopBar } from "@/components/TopBar";
import "./globals.css";

// typeface from the design system: disambiguates I / l / 1, full polish diacritics
const atkinson = Atkinson_Hyperlegible_Next({
  subsets: ["latin", "latin-ext"],
  variable: "--font-atkinson",
  display: "swap",
});

// material symbols, self-hosted subset (no request to google on page load).
// to add a glyph: list it in scripts/fetch-icons.sh and run it
const icons = localFont({
  src: "./fonts/material-symbols-outlined.woff2",
  variable: "--font-icons",
  display: "block",
  preload: true,
});

export const metadata: Metadata = {
  title: {
    default: "Małopolski Hub Innowacji Społecznych",
    template: "%s – Małopolski Hub Innowacji Społecznych",
  },
  description:
    "Opisz problem w swojej okolicy, a asystent ROPS Kraków dobierze przetestowane innowacje społeczne z Małopolski.",
};

export const viewport: Viewport = {
  themeColor: "#0f2d59",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html
      lang="pl"
      className={`${atkinson.variable} ${icons.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: PREFS_BOOTSTRAP }} />
      </head>
      <body className="flex min-h-screen flex-col antialiased">
        <TopBar />
        <main
          id="main-content"
          tabIndex={-1}
          className="mx-auto w-full max-w-7xl flex-1 px-gutter-sm sm:px-gutter"
        >
          {children}
        </main>
        <SiteFooter />
        <CookieConsent />
      </body>
    </html>
  );
}
