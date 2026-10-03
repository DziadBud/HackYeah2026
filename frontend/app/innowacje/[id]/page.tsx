import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { Icon } from "@/components/Icon";
import { ActionBar } from "@/components/innovation/ActionBar";
import { Community } from "@/components/innovation/Community";
import { TestSignup } from "@/components/innovation/TestSignup";
import { CARETAKER, INNOVATIONS, findInnovation } from "@/lib/demo-data";

type Props = { params: Promise<{ id: string }> };

export function generateStaticParams() {
  return INNOVATIONS.map((i) => ({ id: i.id }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const innovation = findInnovation((await params).id);
  return { title: innovation?.title ?? "Nie znaleziono innowacji", description: innovation?.summary };
}

const card = "flex flex-col gap-6 rounded-xl border border-border-subtle bg-surface-container-lowest p-6 shadow-sm hc-edge lg:p-8";
const sectionTitle = "flex items-center gap-2.5 border-b border-border-subtle pb-3 text-headline-md font-bold text-primary sm:text-[1.5rem]";

export default async function InnovationPage({ params }: Props) {
  const innovation = findInnovation((await params).id);
  if (!innovation) notFound();
  const i = innovation;

  const facts = [
    { icon: "report_problem", tone: "text-on-secondary-fixed", label: "Zdiagnozowany problem", text: i.problem },
    { icon: "lightbulb", tone: "text-primary", label: "Wypracowane rozwiązanie", text: i.solution },
    ...(i.results
      ? [{ icon: "sentiment_very_satisfied", tone: "text-tertiary-strong", label: "Rezultaty i korzyści", text: i.results }]
      : []),
  ];

  return (
    <div className="flex flex-col">
      <nav aria-label="Ścieżka powrotu" className="pb-3">
        <ol className="flex flex-wrap items-center gap-1.5 text-body-sm text-on-surface-variant">
          <li>
            <Link href="/" className="flex min-h-10 items-center gap-1 rounded px-1.5 underline hover:text-primary">
              <Icon name="home" size={18} className="text-primary" />
              Strona główna
            </Link>
          </li>
          <li aria-hidden="true" className="flex items-center">
            <Icon name="chevron_right" size={18} />
          </li>
          <li>
            <Link href="/innowacje" className="flex min-h-10 items-center rounded px-1.5 underline hover:text-primary">
              Biblioteka innowacji
            </Link>
          </li>
          <li aria-hidden="true" className="flex items-center">
            <Icon name="chevron_right" size={18} />
          </li>
          <li aria-current="page" className="flex min-h-10 items-center font-bold text-primary">
            {i.title}
          </li>
        </ol>
      </nav>

      <header className={`${card} mb-space-lg gap-5`}>
        <ul className="flex flex-wrap items-center gap-2" aria-label="Oznaczenia">
          {i.recommended && (
            <li className="flex items-center gap-1.5 rounded-lg border border-tertiary-border bg-tertiary-fixed px-3 py-1.5 text-label-sm font-semibold text-on-tertiary-fixed">
              <Icon name="verified" size={17} className="text-tertiary-strong" />
              Innowacja przetestowana i rekomendowana
            </li>
          )}
          {i.tags.map((t, n) => (
            <li
              key={t}
              className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-label-sm font-semibold ${
                n === 0
                  ? "border-tag-blue-border bg-primary-fixed text-primary"
                  : "border-border-subtle bg-surface-container text-on-surface-variant"
              }`}
            >
              <Icon name={n === 0 ? "groups" : "holiday_village"} size={17} className="text-primary" />
              {t}
            </li>
          ))}
        </ul>
        <div className="flex flex-col gap-2.5">
          <h1 className="text-headline-lg-mobile font-bold leading-tight tracking-tight text-primary sm:text-headline-lg lg:text-[2rem]">
            {i.fullTitle}
          </h1>
          <p className="flex items-start gap-2 text-body-md text-on-surface-variant">
            <Icon name="account_balance" size={22} className="mt-0.5 text-primary" />
            <span>
              Autorstwo: <strong className="font-semibold text-on-surface">{i.author}</strong>
              {i.partner && (
                <>
                  {" "}
                  we współpracy z <strong className="font-semibold text-primary">{i.partner}</strong>
                </>
              )}
            </span>
          </p>
        </div>
        <ActionBar likes={i.likes} />
      </header>

      <div className="grid grid-cols-1 items-start gap-space-lg lg:grid-cols-12">
        <div className="flex flex-col gap-space-lg lg:col-span-8">
          <section aria-labelledby="opis-heading" className={card}>
            <h2 id="opis-heading" className={sectionTitle}>
              <Icon name="info" size={26} />
              Opis innowacji i założenia społeczne
            </h2>
            <div className={`grid grid-cols-1 gap-4 ${facts.length === 3 ? "md:grid-cols-3" : "md:grid-cols-2"}`}>
              {facts.map((f) => (
                <div key={f.label} className="flex flex-col gap-2 rounded-xl border border-border-subtle bg-surface-container-low p-5 hc-edge">
                  <h3 className={`flex items-center gap-1.5 text-body-sm font-bold uppercase tracking-wide ${f.tone}`}>
                    <Icon name={f.icon} />
                    {f.label}
                  </h3>
                  <p className="text-body-sm text-on-surface-variant">{f.text}</p>
                </div>
              ))}
            </div>
            {i.photoCaption && (
              // photo slot from the mockup; the real photo comes with the innovation record
              <figure className="relative flex h-64 items-end overflow-hidden rounded-xl border border-border-subtle bg-gradient-to-br from-primary via-[#1b477f] to-[#0b62a4] shadow-sm md:h-80">
                <Icon name="photo_camera" size={96} className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-white/25" />
                <figcaption className="relative z-10 m-3 max-w-xl rounded-lg border border-white/20 bg-primary/95 p-4 text-body-sm font-medium text-on-primary shadow-md sm:m-4">
                  {i.photoCaption}
                </figcaption>
              </figure>
            )}
            {i.deployedIn && (
              <p className="flex items-center gap-2 text-body-sm text-on-surface-variant">
                <Icon name="place" className="text-primary" />
                Dotychczasowe wdrożenia: {i.deployedIn}
              </p>
            )}
          </section>

          <Community threads={i.threads} />
        </div>

        <aside aria-label="Kontakt i zgłoszenia" className="flex flex-col gap-space-lg lg:col-span-4">
          <section aria-labelledby="opiekun-heading" className={`${card} gap-5 lg:p-6`}>
            <h2 id="opiekun-heading" className="flex items-center gap-2 border-b border-border-subtle pb-3 text-headline-sm font-bold text-primary sm:text-[1.25rem]">
              <Icon name="support_agent" size={24} />
              Dedykowany opiekun w ROPS
            </h2>
            <div className="flex items-center gap-3">
              <span aria-hidden="true" className="flex size-14 shrink-0 items-center justify-center rounded-full border border-tag-blue-border bg-primary-fixed">
                <Icon name="face_6" size={32} className="text-primary" />
              </span>
              <span className="flex flex-col">
                <span className="text-body-md font-bold text-primary">{CARETAKER.name}</span>
                <span className="text-label-sm font-medium text-on-surface-variant">{CARETAKER.role}</span>
              </span>
            </div>
            <ul className="flex flex-col gap-2.5 text-body-sm">
              <li>
                <a href={CARETAKER.phoneHref} className="flex min-h-12 items-center gap-3 rounded-lg border border-border-subtle bg-surface-container-low px-3.5 font-semibold text-primary hover:bg-surface-container hc-edge">
                  <Icon name="call" />
                  <span>
                    <span className="sr-only">Telefon: </span>
                    {CARETAKER.phone}
                  </span>
                </a>
              </li>
              <li>
                <a href={`mailto:${CARETAKER.email}`} className="flex min-h-12 items-center gap-3 rounded-lg border border-border-subtle bg-surface-container-low px-3.5 font-semibold text-primary hover:bg-surface-container hc-edge">
                  <Icon name="mail" />
                  <span>
                    <span className="sr-only">E-mail: </span>
                    {CARETAKER.email}
                  </span>
                </a>
              </li>
              <li className="flex items-start gap-3 rounded-lg border border-border-subtle bg-surface-container-low p-3.5 text-on-surface-variant hc-edge">
                <Icon name="schedule" className="mt-0.5 text-primary" />
                <span className="flex flex-col">
                  <span className="text-label-sm font-bold uppercase tracking-wide text-primary">Dyżur konsultacyjny stacjonarny:</span>
                  <span className="mt-0.5 text-label-sm font-normal">
                    {CARETAKER.hours}
                    <br />
                    {CARETAKER.place}
                  </span>
                </span>
              </li>
            </ul>
          </section>
          <TestSignup title={i.title} />
        </aside>
      </div>
    </div>
  );
}
