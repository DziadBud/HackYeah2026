"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";

const btn =
  "flex min-h-12 items-center gap-2 rounded-xl bg-surface-container-lowest px-space-md text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge";

export function ActionBar({ likes }: { likes: number }) {
  const [liked, setLiked] = useState(false);
  const [notify, setNotify] = useState(false);
  const [copied, setCopied] = useState(false);

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="flex flex-col items-stretch justify-between gap-space-md rounded-xl bg-surface-container-low p-space-md xl:flex-row xl:items-center">
      <div className="flex flex-col items-start gap-space-xs sm:flex-row sm:items-center">
        <span className="text-label-md font-semibold text-on-surface-variant">Bezpośredni link:</span>
        <button type="button" onClick={copyLink} className="flex min-h-11 items-center gap-1 rounded px-1 text-label-md font-semibold text-primary underline">
          Skopiuj link
        </button>
        <span role="status" className="text-caption text-on-surface-variant">
          {copied ? "Skopiowano!" : ""}
        </span>
      </div>
      <div className="flex flex-wrap items-center gap-space-xs">
        <button
          type="button"
          aria-pressed={liked}
          onClick={() => setLiked((v) => !v)}
          className={`${btn} aria-pressed:bg-secondary-fixed aria-pressed:text-on-secondary-fixed`}
        >
          <Icon name="favorite" size={22} fill className="text-secondary" />
          <span>Polub innowację ({likes + (liked ? 1 : 0)})</span>
        </button>
        <button
          type="button"
          aria-pressed={notify}
          onClick={() => setNotify((v) => !v)}
          className={`${btn} aria-pressed:bg-primary aria-pressed:text-on-primary`}
        >
          <Icon name={notify ? "notifications_active" : "notifications"} size={22} />
          <span>{notify ? "Powiadomienia aktywne" : "Włącz powiadomienia"}</span>
        </button>
        <a
          href="#zglos-do-testow"
          className="flex min-h-12 items-center gap-2 rounded-xl bg-secondary px-space-md text-label-lg font-semibold text-on-secondary shadow-sm hover:bg-secondary-hover"
        >
          <Icon name="how_to_reg" size={22} />
          <span>Zgłoś się do testowania</span>
          <span className="rounded-full bg-surface-container-lowest px-2 py-0.5 text-label-md text-secondary">Wolne miejsca</span>
        </a>
      </div>
    </div>
  );
}
