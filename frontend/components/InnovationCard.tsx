import Link from "next/link";
import type { Innovation } from "@/lib/api";
import { Icon } from "@/components/Icon";

export function InnovationCard({
  innovation,
  headingLevel: H = "h3",
}: {
  innovation: Innovation;
  headingLevel?: "h2" | "h3";
}) {
  const { id, title, summary, why, tags, location } = innovation;
  return (
    <article className="flex w-full flex-col justify-between gap-4 rounded-xl border border-border-subtle bg-surface-container-low p-4 shadow-sm transition-shadow hover:border-primary/50 hover:shadow hc-edge">
      <div className="flex flex-col gap-2">
        {tags && tags.length > 0 && (
          <ul className="flex flex-wrap gap-1.5" aria-label="Kategorie">
            {tags.map((t) => (
              <li
                key={t}
                className="rounded border border-tag-blue-border bg-primary-fixed px-2.5 py-0.5 text-label-sm font-semibold text-on-primary-fixed"
              >
                {t}
              </li>
            ))}
          </ul>
        )}
        <H className="text-headline-sm font-bold leading-snug text-primary">{title}</H>
        <p className="text-body-sm text-on-surface-variant">{summary}</p>
        {why && (
          <p className="text-body-sm text-on-surface">
            <strong>Dlaczego pasuje: </strong>
            {why}
          </p>
        )}
        {location && (
          <p className="flex items-center gap-1.5 pt-1 text-label-sm font-normal text-on-surface-variant">
            <Icon name="place" size={16} className="text-primary" />
            <span>Wdrożono: {location}</span>
          </p>
        )}
      </div>
      <Link
        href={`/innowacje/${id}`}
        className="flex min-h-11 w-full items-center justify-center gap-2 rounded-lg bg-primary px-4 text-label-md font-semibold text-on-primary shadow-sm hover:bg-primary-hover"
      >
        <span>
          Zobacz szczegóły innowacji<span className="sr-only">: {title}</span>
        </span>
        <Icon name="arrow_forward" size={18} />
      </Link>
    </article>
  );
}
