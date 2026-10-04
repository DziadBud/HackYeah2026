"use client";

import { useState } from "react";
import { adminApi, type InnovationRating } from "@/lib/api";
import { mockInnovationStats } from "@/lib/admin-mock";
import { Icon } from "@/components/Icon";
import { fmtDate } from "@/components/admin/styles";
import type { Source } from "@/components/admin/useApiOrMock";

// loads on first open, so the innovation list doesn't fetch ratings for every card
export function RatingsDropdown({
  innovationId,
  title,
  count,
  source,
}: {
  innovationId: string;
  title: string;
  count: number;
  source: Source;
}) {
  const [ratings, setRatings] = useState<InnovationRating[] | null>(null);
  const [error, setError] = useState(false);

  async function load() {
    if (ratings) return;
    setError(false);
    try {
      setRatings(
        source === "api"
          ? await adminApi.innovationRatings(innovationId)
          : mockInnovationStats(innovationId).recent_comments.map((c) => ({ ...c, kind: "rating" as const })),
      );
    } catch {
      setError(true);
    }
  }

  return (
    <details
      className="group rounded-xl bg-surface-container-lowest hc-edge"
      onToggle={(e) => {
        if (e.currentTarget.open) void load();
      }}
    >
      <summary className="flex min-h-12 cursor-pointer items-center gap-space-xs px-space-sm text-label-lg font-semibold text-primary">
        <Icon name="chevron_right" className="transition-transform group-open:rotate-90" />
        Oceny ({count})<span className="sr-only">: {title}</span>
      </summary>
      <div className="px-space-sm pb-space-sm">
        {error ? (
          <p role="status" className="text-body-md text-on-surface-variant">
            Nie udało się wczytać ocen. Zamknij i otwórz ponownie.
          </p>
        ) : !ratings ? (
          <p role="status" className="text-body-md text-on-surface-variant">
            Wczytuję oceny…
          </p>
        ) : ratings.length === 0 ? (
          <p className="text-body-md text-on-surface-variant">Brak ocen.</p>
        ) : (
          <ul aria-label={`Oceny: ${title}`} tabIndex={0} className="flex max-h-80 flex-col gap-space-xs overflow-y-auto">
            {ratings.map((r, n) => (
              <li key={r.created_at + n} className="flex flex-col gap-1 rounded-lg bg-surface-container-low p-space-sm">
                <span className="flex flex-wrap items-center gap-2 text-caption text-on-surface-variant">
                  <span className="inline-flex items-center gap-1 font-semibold text-on-surface">
                    <Icon name="star" fill size={16} className="text-primary" />
                    {r.rating} / 5
                  </span>
                  {r.kind === "test_signup" && (
                    <span className="rounded bg-surface-container-high px-2 py-0.5 text-primary">Tester</span>
                  )}
                  • {fmtDate(r.created_at)}
                </span>
                {r.comment ? (
                  <p className="text-body-md text-on-surface">{r.comment}</p>
                ) : (
                  <p className="text-body-md italic text-on-surface-variant">Bez komentarza</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </details>
  );
}
