"use client";

import Link from "next/link";
import { adminApi, ApiError, type GrantApplication, type GrantCall, type PlanStep } from "@/lib/api";
import { ADMIN_MOCK } from "@/lib/admin-mock";
import { Icon } from "@/components/Icon";
import {
  APPLICANT_LABELS,
  CONTACT_FIELDS,
  INFORMAL_FIELDS,
  NARRATIVE_SECTIONS,
  ORG_DECL,
  ORG_FIELDS,
  PERSON_DECL,
  PERSON_FIELDS,
} from "@/components/grant/labels";
import { APPLICATION_STATUS, fmtPln } from "@/components/admin/GrantApplicationList";
import { card, fmtDate, ghostBtn, td, th } from "@/components/admin/styles";
import { useApiOrMock } from "@/components/admin/useApiOrMock";

const h3 = "text-title-md font-semibold text-primary";
const empty = <span className="italic text-on-surface-variant">nie wypełniono</span>;

const SOURCE: Record<string, string> = {
  gemini: "szkic z AI",
  template: "szkic z szablonu (bez AI)",
};

type Data = { application: GrantApplication | null; calls: GrantCall[] };
type Fields = readonly (readonly [string, string])[];

function text(v: unknown) {
  return typeof v === "string" ? v.trim() : "";
}

function FieldList({ fields, values }: { fields: Fields; values: Record<string, unknown> }) {
  return (
    <dl className="grid grid-cols-1 gap-x-space-md gap-y-1 text-body-md sm:grid-cols-[max-content_1fr]">
      {fields.map(([key, label]) => (
        <div key={key} className="contents">
          <dt className="font-semibold text-primary">{label}</dt>
          <dd className="break-words">{text(values[key]) || empty}</dd>
        </div>
      ))}
    </dl>
  );
}

function asRecord(v: unknown): Record<string, unknown> {
  return v && typeof v === "object" ? (v as Record<string, unknown>) : {};
}

function Applicant({ a }: { a: GrantApplication }) {
  if (a.applicant_type === "person") return <FieldList fields={PERSON_FIELDS} values={a.applicant} />;
  if (a.applicant_type === "organization") {
    return (
      <div className="flex flex-col gap-space-sm">
        <FieldList fields={ORG_FIELDS} values={a.applicant} />
        {(
          [
            ["representative", "Osoba upoważniona do reprezentowania"],
            ["working_contact", "Kontakt roboczy"],
          ] as const
        ).map(([key, title]) => (
          <div key={key} className="flex flex-col gap-1">
            <h4 className="text-body-md font-bold text-primary">{title}</h4>
            <FieldList fields={CONTACT_FIELDS} values={asRecord(a.applicant[key])} />
          </div>
        ))}
      </div>
    );
  }
  const partners = Array.isArray(a.applicant.partners) ? a.applicant.partners.map(asRecord) : [];
  return (
    <div className="flex flex-col gap-space-sm">
      <FieldList fields={INFORMAL_FIELDS} values={a.applicant} />
      <h4 className="text-body-md font-bold text-primary">Partnerzy ({partners.length})</h4>
      {partners.length === 0 ? (
        <p className="text-body-md">{empty}</p>
      ) : (
        <ol className="flex list-decimal flex-col gap-space-sm pl-space-md">
          {partners.map((p, i) => (
            <li key={i}>
              {p.kind === "organization" ? (
                <FieldList fields={ORG_FIELDS} values={asRecord(p.organization)} />
              ) : (
                <FieldList fields={PERSON_FIELDS} values={asRecord(p.person)} />
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}

function Steps({ title, steps }: { title: string; steps: PlanStep[] }) {
  const total = steps.reduce((sum, s) => sum + (s.cost_pln ?? 0), 0);
  return (
    <div className="flex flex-col gap-1">
      <h4 className="text-body-md font-bold text-primary">{title}</h4>
      {steps.length === 0 ? (
        <p className="text-body-md">{empty}</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th scope="col" className={th}>Działanie</th>
                <th scope="col" className={th}>Termin</th>
                <th scope="col" className={th}>Koszt</th>
                <th scope="col" className={th}>Uwagi</th>
              </tr>
            </thead>
            <tbody>
              {steps.map((s, i) => (
                <tr key={i}>
                  <td className={td}>{s.action || "—"}</td>
                  <td className={td}>{s.timeline || "—"}</td>
                  <td className={`${td} whitespace-nowrap`}>{fmtPln(s.cost_pln)}</td>
                  <td className={td}>{s.note || "—"}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <th scope="row" colSpan={2} className={th}>Razem</th>
                <td className={`${td} whitespace-nowrap font-semibold`}>{fmtPln(total)}</td>
                <td className={td} />
              </tr>
            </tfoot>
          </table>
        </div>
      )}
    </div>
  );
}

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section aria-labelledby={id} className={`${card} flex flex-col gap-space-sm`}>
      <h3 id={id} className={h3}>
        {title}
      </h3>
      {children}
    </section>
  );
}

export function GrantApplicationView({ id }: { id: string }) {
  const { data, notice } = useApiOrMock<Data>(
    async () => {
      try {
        const [application, calls] = await Promise.all([adminApi.grantApplication(id), adminApi.grantCalls()]);
        return { application, calls };
      } catch (err) {
        // a real 404 is an answer, not an outage
        if (err instanceof ApiError && err.status === 404) return { application: null, calls: [] };
        throw err;
      }
    },
    () => ({
      application: structuredClone(ADMIN_MOCK.grantApplications.find((a) => a.id === id) ?? null),
      calls: structuredClone(ADMIN_MOCK.grantCalls),
    }),
  );

  const back = (
    <Link href="/admin/wnioski" className={`${ghostBtn} self-start`}>
      <Icon name="arrow_back" />
      Wróć do listy wniosków
    </Link>
  );

  if (!data) {
    return (
      <p role="status" className="py-space-lg text-body-lg text-on-surface-variant">
        Wczytuję wniosek…
      </p>
    );
  }

  const a = data.application;
  if (!a) {
    return (
      <section className={`${card} flex flex-col gap-space-sm`}>
        <h2 className="text-headline-lg-mobile font-bold text-primary">Nie znaleziono wniosku</h2>
        <p className="text-body-lg text-on-surface-variant">Wniosek o tym identyfikatorze nie istnieje w bazie.</p>
        {back}
      </section>
    );
  }

  const call = data.calls.find((c) => c.id === a.grant_call_id);
  const declLabels = a.applicant_type === "organization" ? ORG_DECL : PERSON_DECL;
  const declKeys = Object.keys(declLabels);
  const ticked = declKeys.filter((k) => a.declarations[k]).length;
  const plan = a.action_plan;

  return (
    <div className="flex flex-col gap-space-md">
      {back}
      <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
        {notice}
      </p>

      <header className={`${card} flex flex-col gap-space-sm`}>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded bg-tertiary-fixed px-2 py-0.5 text-caption font-semibold text-on-tertiary-fixed">
            {APPLICATION_STATUS[a.status]}
          </span>
          <span className="rounded bg-surface-container-high px-2 py-0.5 text-caption text-primary">
            {(a.generated_by && SOURCE[a.generated_by]) || "wypełniony ręcznie"}
          </span>
        </div>
        <h2 className="text-headline-md font-semibold text-primary">{a.title || "Bez tytułu"}</h2>
        <dl className="grid grid-cols-1 gap-x-space-md gap-y-1 text-body-md sm:grid-cols-[max-content_1fr]">
          <dt className="font-semibold text-primary">Nabór</dt>
          <dd>{call?.name ?? "—"}</dd>
          <dt className="font-semibold text-primary">E-mail kontaktowy</dt>
          <dd>
            {a.email ? (
              <a href={`mailto:${a.email}`} className="break-all underline hover:text-primary">
                {a.email}
              </a>
            ) : (
              "nie podano"
            )}
          </dd>
          <dt className="font-semibold text-primary">Utworzony</dt>
          <dd>{fmtDate(a.created_at)}</dd>
          <dt className="font-semibold text-primary">Ostatnia zmiana</dt>
          <dd>{fmtDate(a.updated_at)}</dd>
        </dl>
      </header>

      <Section id="sec-1" title="1. Tytuł innowacji">
        <p className="text-body-md">{a.title.trim() || empty}</p>
      </Section>

      <Section id="sec-2" title={`2. Dane pomysłodawcy: ${APPLICANT_LABELS[a.applicant_type]}`}>
        <Applicant a={a} />
      </Section>

      {NARRATIVE_SECTIONS.map(([key, title]) => (
        <Section key={key} id={`sec-${key}`} title={title}>
          <p className="whitespace-pre-line text-body-md">{a[key].trim() || empty}</p>
        </Section>
      ))}

      <Section id="sec-9" title="9. Plan działania i koszty">
        <h4 className="text-body-md font-bold text-primary">Przygotowanie</h4>
        <p className="whitespace-pre-line text-body-md">{plan.preparation_summary.trim() || empty}</p>
        <Steps title="Przygotowanie — kroki" steps={plan.preparation} />
        <h4 className="text-body-md font-bold text-primary">Testowanie</h4>
        <p className="whitespace-pre-line text-body-md">{plan.testing_summary.trim() || empty}</p>
        <Steps title="Faza I testu" steps={plan.testing_phase_1} />
        <Steps title="Faza II testu" steps={plan.testing_phase_2} />
      </Section>

      <Section id="sec-10" title="10. Wnioskowana kwota grantu">
        <p className="text-body-lg font-semibold">{a.grant_amount_pln == null ? empty : fmtPln(a.grant_amount_pln)}</p>
      </Section>

      <Section id="sec-11" title="11. Zespół projektowy i doświadczenie">
        <p className="whitespace-pre-line text-body-md">{a.team.trim() || empty}</p>
      </Section>

      <Section id="sec-12" title="12. Oświadczenia">
        <p className="text-body-md font-semibold">
          Zaznaczono {ticked} z {declKeys.length}
        </p>
        <ul className="flex flex-col gap-1">
          {declKeys.map((k) => {
            const on = Boolean(a.declarations[k]);
            return (
              <li key={k} className={`flex items-start gap-space-xs text-body-md ${on ? "" : "font-semibold text-error"}`}>
                <Icon name={on ? "check" : "close"} />
                <span>
                  <span className="sr-only">{on ? "Zaznaczone: " : "Brak: "}</span>
                  {declLabels[k]}
                </span>
              </li>
            );
          })}
        </ul>
      </Section>
    </div>
  );
}
