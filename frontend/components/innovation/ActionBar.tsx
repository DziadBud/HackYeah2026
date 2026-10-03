"use client";

import { useEffect, useState } from "react";
import { Icon } from "@/components/Icon";

const btn =
  "flex min-h-11 items-center gap-1.5 rounded-lg border border-border-subtle bg-surface-container-lowest px-3 text-label-md font-semibold text-primary shadow-sm hover:bg-surface-container hc-edge";

export function ActionBar({ likes }: { likes: number }) {
  const [liked, setLiked] = useState(false);
  const [notify, setNotify] = useState(false);
  const [copied, setCopied] = useState(false);
  const [url, setUrl] = useState("");

  useEffect(() => setUrl(window.location.href.split("#")[0]), []);

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(url);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="flex flex-col justify-between gap-4 rounded-xl border border-border-subtle bg-surface-container-low p-4 shadow-sm hc-edge sm:p-5 lg:flex-row lg:items-center">
      <div className="flex min-w-0 max-w-full grow flex-col gap-2 sm:flex-row sm:items-center sm:gap-3 lg:max-w-md">
        <span className="flex shrink-0 items-center gap-1.5 whitespace-nowrap text-label-sm font-bold uppercase tracking-wider text-on-surface-variant">
          <Icon name="link" size={17} className="text-primary" />
          Bezpośredni link:
        </span>
        <div className="flex min-w-0 grow items-center justify-between gap-2 rounded-lg border border-border-subtle bg-surface-container-lowest px-3 py-1 shadow-sm">
          <span className="truncate font-mono text-label-sm font-normal text-on-surface">{url || "…"}</span>
          <button
            type="button"
            onClick={copyLink}
            aria-label="Skopiuj bezpośredni link do innowacji"
            title="Kopiuj link"
            className="flex size-9 shrink-0 items-center justify-center rounded text-primary hover:bg-surface-container-high"
          >
            <Icon name="content_copy" size={18} />
          </button>
        </div>
        <span role="status" className="text-label-sm font-semibold text-primary">
          {copied ? "Skopiowano!" : ""}
        </span>
      </div>
      <div className="flex shrink-0 flex-wrap items-center gap-2.5">
        <button
          type="button"
          aria-pressed={liked}
          onClick={() => setLiked((v) => !v)}
          className={`${btn} aria-pressed:border-secondary-border aria-pressed:bg-secondary-fixed`}
        >
          <Icon name="favorite" size={18} fill className="text-secondary" />
          <span>Polub innowację</span>
          <span className="rounded-full bg-surface-container px-2 py-0.5 text-label-sm font-bold text-primary">
            <span className="sr-only">liczba polubień: </span>
            {likes + (liked ? 1 : 0)}
          </span>
        </button>
        <button
          type="button"
          aria-pressed={notify}
          onClick={() => setNotify((v) => !v)}
          className={`${btn} aria-pressed:bg-primary aria-pressed:text-on-primary`}
        >
          <Icon name={notify ? "notifications_active" : "notifications"} size={18} />
          <span>{notify ? "Powiadomienia aktywne" : "Włącz powiadomienia"}</span>
        </button>
        <a
          href="#zglos-do-testow"
          className="flex min-h-11 items-center gap-2 whitespace-nowrap rounded-lg bg-secondary px-3.5 text-label-md font-semibold text-on-secondary shadow-md hover:bg-secondary-hover"
        >
          <Icon name="how_to_reg" size={18} />
          <span>Zgłoś się do testowania</span>
          <span className="rounded-full bg-surface-container-lowest px-1.5 py-0.5 text-label-sm font-bold uppercase tracking-wide text-on-secondary-fixed">
            Wolne
          </span>
        </a>
      </div>
    </div>
  );
}
