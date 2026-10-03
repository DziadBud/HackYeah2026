import type { Metadata } from "next";

export const metadata: Metadata = { title: "Deklaracja dostępności" };

const FEATURES = [
  "Pasek dostępności na każdej stronie: powiększanie tekstu (przycisk A+, trzy stopnie), tryb wysokiego kontrastu (czarny, żółty, biały) i czytanie treści na głos.",
  "Link „Przejdź do treści głównej” jako pierwszy element strony.",
  "Pełna obsługa z klawiatury z wyraźnym wskaźnikiem fokusu (niebieska ramka z białym odstępem).",
  "Kontrast tekstu co najmniej 4,5:1, kontrast pól formularzy i kontrolek co najmniej 3:1.",
  "Krój Public Sans o dużej wysokości małych liter, tekst podstawowy 16 px, treść skalowana razem z całym interfejsem.",
  "Pola formularzy z widocznymi etykietami; komunikaty o stanie ogłaszane czytnikom ekranu.",
  "Duże obszary klikalne przycisków i pól formularzy i ograniczenie animacji przy ustawieniu „ogranicz ruch”.",
  "Dyktowanie wiadomości w czacie dla osób, którym trudno pisać.",
];

export default function AccessibilityStatementPage() {
  return (
    <article className="mx-auto flex max-w-3xl flex-col gap-space-md py-space-lg text-body-lg">
      <h1 className="text-headline-lg-mobile font-bold text-primary sm:text-headline-lg">Deklaracja dostępności</h1>
      <p>
        Regionalny Ośrodek Polityki Społecznej w Krakowie zobowiązuje się zapewnić dostępność serwisu Małopolski Hub
        Innowacji Społecznych zgodnie z ustawą z dnia 4 kwietnia 2019 r. o dostępności cyfrowej stron internetowych i
        aplikacji mobilnych podmiotów publicznych.
      </p>
      <h2 className="text-headline-md font-semibold text-primary">Status pod względem zgodności</h2>
      <p>
        Serwis jest prototypem przygotowanym podczas HackYeah 2026 i jest projektowany zgodnie ze standardem WCAG 2.1 na
        poziomie AA. Pełny audyt dostępności zostanie przeprowadzony przed udostępnieniem produkcyjnym.
      </p>
      <h2 className="text-headline-md font-semibold text-primary">Udogodnienia</h2>
      <ul className="flex list-disc flex-col gap-2 pl-6">
        {FEATURES.map((f) => (
          <li key={f}>{f}</li>
        ))}
      </ul>
      <h2 className="text-headline-md font-semibold text-primary">Informacje zwrotne i kontakt</h2>
      <p>
        Jeśli zauważysz problem z dostępnością, napisz na{" "}
        <a className="font-bold text-primary underline" href="mailto:biuro@rops.krakow.pl">
          biuro@rops.krakow.pl
        </a>{" "}
        lub zadzwoń pod numer{" "}
        <a className="font-bold text-primary underline" href="tel:+48124220636">
          +48 12 422 06 36
        </a>
        .
      </p>
    </article>
  );
}
