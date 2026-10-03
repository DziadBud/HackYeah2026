import Link from "next/link";
import { Icon } from "@/components/Icon";

// what a card shows; built from /match results, /innovations rows or demo data
export interface InnovationCardData {
  id: string;
  title: string;
  summary: string;
  why?: string | null;
  // display labels, not raw tags
  tags?: string[];
  city?: string;
}

export function InnovationCard({
  innovation,
  headingLevel: H = "h3",
}: {
  innovation: InnovationCardData;
  headingLevel?: "h2" | "h3";
}) {
  const { id, title, summary, why, tags, city } = innovation;
  return (
    <article className="flex w-full flex-col justify-between gap-space-md rounded-xl bg-surface-container-low p-space-md shadow-sm hc-edge">
      <div className="flex flex-col gap-space-xs">
        {tags && tags.length > 0 && (
          <ul className="flex flex-wrap gap-2" aria-label="Kategorie">
            {tags.map((t) => (
              <li key={t} className="rounded bg-surface-container-highest px-2 py-0.5 text-caption text-primary">
                {t}
              </li>
            ))}
          </ul>
        )}
        <H className="text-headline-sm font-semibold text-primary">{title}</H>
        <p className="text-body-md text-on-surface-variant">{summary}</p>
        {why && (
          <p className="text-body-md text-on-surface">
            <strong>Dlaczego pasuje: </strong>
            {why}
          </p>
        )}
        {city && (
          <p className="flex items-center gap-2 pt-2 text-caption text-on-surface-variant">
            <Icon name="place" size={18} className="text-primary" />
            <span>Wdrożono: {city}</span>
          </p>
        )}
      </div>
      <Link
        href={`/innowacje/${id}`}
        className="flex min-h-12 w-full items-center justify-center gap-space-xs rounded-lg bg-primary-container px-space-md text-body-md font-bold text-on-primary hover:bg-primary"
      >
        <span>
          Zobacz szczegóły innowacji<span className="sr-only">: {title}</span>
        </span>
        <Icon name="arrow_forward" />
      </Link>
    </article>
  );
}
