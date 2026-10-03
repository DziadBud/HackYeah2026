"use client";

import { useState } from "react";
import { Icon } from "@/components/Icon";

export function ActionBar({ pdfUrl }: { pdfUrl: string }) {
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
    <div className="flex flex-col items-stretch gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge sm:flex-row sm:flex-wrap sm:items-center">
      <a
        href="#zglos-do-testow"
        className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-secondary px-space-md py-2 text-center text-label-lg font-semibold text-on-secondary shadow-sm hover:bg-secondary-hover"
      >
        <Icon name="how_to_reg" size={22} />
        <span>Zgłoś się do testowania</span>
      </a>
      <a
        href={pdfUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-surface-container-lowest px-space-md py-2 text-center text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge"
      >
        <Icon name="info" size={22} />
        <span>
          Więcej informacji (PDF)
          <span className="sr-only">, otwiera się w nowej karcie</span>
        </span>
      </a>
      <button
        type="button"
        onClick={copyLink}
        className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-surface-container-lowest px-space-md py-2 text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge"
      >
        <Icon name="content_copy" size={22} />
        <span>Skopiuj link do tej strony</span>
      </button>
      <span role="status" className="text-body-md font-semibold text-primary">
        {copied ? "Skopiowano link." : ""}
      </span>
    </div>
  );
}
