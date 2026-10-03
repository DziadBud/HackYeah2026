export function SiteFooter() {
  return (
    <footer className="mt-space-xl w-full border-t border-border-subtle bg-surface-container-lowest hc-edge">
      <div className="mx-auto flex max-w-7xl flex-col justify-between gap-8 px-gutter-sm py-10 sm:px-gutter md:flex-row">
        <div className="flex flex-col gap-2">
          <h2 className="flex items-center gap-2 text-body-lg font-bold text-primary">
            <span aria-hidden="true" className="size-2.5 shrink-0 rounded-full bg-secondary" />
            Regionalny Ośrodek Polityki Społecznej w Krakowie
          </h2>
          <p className="max-w-md text-body-sm text-on-surface-variant">
            Wspieramy i upowszechniamy innowacje społeczne odpowiadające na realne potrzeby mieszkańców
            Województwa Małopolskiego.
          </p>
        </div>
        <div className="flex flex-col gap-2">
          <h2 className="text-body-md font-bold text-primary">Dostępność i kontakt</h2>
          <address className="text-body-sm not-italic text-on-surface-variant">
            ul. Piastowska 32, 30-070 Kraków
            <br />
            Infolinia:{" "}
            <a className="text-primary hover:underline" href="tel:+48124220636">
              +48 12 422 06 36
            </a>
            <br />
            Email:{" "}
            <a className="text-primary underline" href="mailto:biuro@rops.krakow.pl">
              biuro@rops.krakow.pl
            </a>
          </address>
        </div>
      </div>
      <div className="w-full border-t border-border-subtle bg-surface py-3.5">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-gutter-sm text-label-sm text-on-surface-variant sm:flex-row sm:px-gutter">
          <p>© 2026 Regionalny Ośrodek Polityki Społecznej w Krakowie. Wszelkie prawa zastrzeżone.</p>
          <p className="font-semibold text-primary">Projektowane zgodnie z WCAG 2.1 AA</p>
        </div>
      </div>
    </footer>
  );
}
