export function SiteFooter() {
  return (
    <footer className="mt-space-xl w-full border-t border-surface-container-highest bg-surface-container-low hc-edge">
      <div className="mx-auto flex max-w-7xl flex-col justify-between gap-space-lg px-gutter-sm py-space-xl sm:px-gutter md:flex-row">
        <div className="flex flex-col gap-space-xs">
          <h2 className="text-headline-sm font-semibold text-primary">
            Regionalny Ośrodek Polityki Społecznej w Krakowie
          </h2>
          <p className="max-w-md text-body-md text-on-surface-variant">
            Wspieramy i upowszechniamy innowacje społeczne odpowiadające na realne potrzeby mieszkańców
            Województwa Małopolskiego.
          </p>
        </div>
        <div className="flex flex-col gap-space-xs">
          <h2 className="text-headline-sm font-semibold text-primary">Dostępność i kontakt</h2>
          <address className="text-body-md not-italic text-on-surface-variant">
            ul. Piastowska 32, 30-070 Kraków
            <br />
            Infolinia:{" "}
            <a className="underline" href="tel:+48124220636">
              +48 12 422 06 36
            </a>
            <br />
            Email:{" "}
            <a className="underline" href="mailto:biuro@rops.krakow.pl">
              biuro@rops.krakow.pl
            </a>
          </address>
        </div>
      </div>
      <div className="w-full bg-surface-container py-space-sm">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-1 px-gutter-sm text-caption text-on-surface-variant sm:flex-row sm:px-gutter">
          <p>© 2026 Regionalny Ośrodek Polityki Społecznej w Krakowie. Wszelkie prawa zastrzeżone.</p>
          <p>Projektowane zgodnie z WCAG 2.1 AA</p>
        </div>
      </div>
    </footer>
  );
}
