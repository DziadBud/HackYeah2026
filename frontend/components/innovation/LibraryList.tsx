"use client";

import { useEffect, useState } from "react";
import { api, type LibraryInnovation } from "@/lib/api";
import { INNOVATIONS, toInnovation } from "@/lib/demo-data";
import { AREA_LABEL } from "@/lib/labels";
import { Icon } from "@/components/Icon";
import { InnovationCard, type InnovationCardData } from "@/components/InnovationCard";

const PAGE = 24;

function toCard(i: LibraryInnovation): InnovationCardData {
  return {
    id: i.id,
    title: i.title,
    summary: i.tagline ?? i.summary,
    tags: i.challenge_areas.map((a) => AREA_LABEL[a]),
    city: i.city,
    imageUrl: i.photos[0] ? api.innovationPhotoUrl(i.id, i.photos[0]) : undefined,
  };
}

// GET /innovations (published only); the demo list only when the api is unreachable
export function LibraryList() {
  const [items, setItems] = useState<InnovationCardData[] | null>(null);
  const [total, setTotal] = useState(0);
  const [demo, setDemo] = useState(false);
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    let live = true;
    api
      .innovations(PAGE, 0)
      .then((p) => {
        if (!live) return;
        setItems(p.items.map(toCard));
        setTotal(p.total);
      })
      .catch(() => {
        if (!live) return;
        setItems(INNOVATIONS.map(toInnovation));
        setTotal(INNOVATIONS.length);
        setDemo(true);
      });
    return () => {
      live = false;
    };
  }, []);

  async function loadMore() {
    if (!items) return;
    setBusy(true);
    try {
      const p = await api.innovations(PAGE, items.length);
      setItems([...items, ...p.items.map(toCard)]);
      setTotal(p.total);
      setStatus(`Wczytano kolejne innowacje: ${p.items.length}.`);
    } catch {
      setStatus("Nie udało się wczytać kolejnych innowacji. Spróbuj ponownie.");
    } finally {
      setBusy(false);
    }
  }

  if (!items) {
    return (
      <p role="status" className="text-body-lg text-on-surface-variant">
        Wczytuję innowacje…
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-space-md">
      {demo && (
        <p className="flex items-start gap-2 rounded-lg bg-surface-container p-space-sm text-caption text-on-surface-variant">
          <Icon name="info" size={18} className="mt-0.5 text-primary" />
          <span>Tryb demonstracyjny: serwer jest niedostępny, pokazujemy przykładową bazę innowacji.</span>
        </p>
      )}
      {items.length === 0 ? (
        <p className="text-body-lg text-on-surface-variant">W bibliotece nie ma jeszcze opublikowanych innowacji.</p>
      ) : (
        <ul className="grid grid-cols-1 gap-space-md md:grid-cols-2 lg:grid-cols-3">
          {items.map((i) => (
            <li key={i.id} className="flex">
              <div className="flex w-full">
                <InnovationCard innovation={i} headingLevel="h2" />
              </div>
            </li>
          ))}
        </ul>
      )}
      {!demo && items.length < total && (
        <button
          type="button"
          onClick={loadMore}
          disabled={busy}
          className="flex min-h-12 items-center justify-center gap-space-xs self-center rounded-lg bg-surface-container-high px-space-lg text-body-md font-bold text-primary hover:bg-surface-container-highest disabled:cursor-wait hc-edge"
        >
          {busy ? "Wczytuję…" : `Pokaż więcej (${items.length} z ${total})`}
        </button>
      )}
      <p role="status" className="text-body-md text-on-surface-variant">
        {status}
      </p>
    </div>
  );
}
