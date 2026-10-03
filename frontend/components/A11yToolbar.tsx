"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Icon } from "@/components/Icon";

type TextScale = "100" | "115" | "130";
type Contrast = "normal" | "high";

export const PREFS_KEY = "a11y-prefs";

// runs before hydration (see layout.tsx) so saved preferences apply without a flash
export const PREFS_BOOTSTRAP = `try{var p=JSON.parse(localStorage.getItem("${PREFS_KEY}")||"{}");var d=document.documentElement;if(p.textScale)d.dataset.textScale=p.textScale;if(p.contrast)d.dataset.contrast=p.contrast;}catch(e){}`;

// one A+ button steps through the sizes and wraps back to standard
const NEXT_SCALE: Record<TextScale, TextScale> = { "100": "115", "115": "130", "130": "100" };

function savePrefs(textScale: TextScale, contrast: Contrast) {
  try {
    localStorage.setItem(PREFS_KEY, JSON.stringify({ textScale, contrast }));
  } catch {
    // private mode or blocked storage: the setting still applies to this page view
  }
}

// chrome stops long utterances after ~15 s, so speak paragraph-sized chunks
function chunks(text: string): string[] {
  return text
    .split(/\n+|(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function A11yToolbar() {
  const [textScale, setTextScale] = useState<TextScale>("100");
  const [contrast, setContrast] = useState<Contrast>("normal");
  const [speaking, setSpeaking] = useState(false);
  const [canSpeak, setCanSpeak] = useState(true);
  const pathname = usePathname();
  const speakingRef = useRef(false);

  useEffect(() => {
    const d = document.documentElement;
    setTextScale((d.dataset.textScale as TextScale) ?? "100");
    setContrast((d.dataset.contrast as Contrast) ?? "normal");
    setCanSpeak("speechSynthesis" in window);
  }, []);

  // stop reading when the user navigates away
  useEffect(() => {
    if (speakingRef.current) {
      window.speechSynthesis.cancel();
      speakingRef.current = false;
      setSpeaking(false);
    }
  }, [pathname]);

  function applyScale(value: TextScale) {
    setTextScale(value);
    document.documentElement.dataset.textScale = value;
    savePrefs(value, contrast);
  }

  function toggleContrast() {
    const next: Contrast = contrast === "high" ? "normal" : "high";
    setContrast(next);
    document.documentElement.dataset.contrast = next;
    savePrefs(textScale, next);
  }

  function toggleSpeech() {
    const synth = window.speechSynthesis;
    if (speakingRef.current) {
      synth.cancel();
      speakingRef.current = false;
      setSpeaking(false);
      return;
    }
    const selected = window.getSelection()?.toString().trim();
    const source = selected || document.getElementById("main-content")?.innerText || "";
    const parts = chunks(source);
    if (parts.length === 0) return;
    synth.cancel();
    const voice = synth.getVoices().find((v) => v.lang.toLowerCase().startsWith("pl"));
    parts.forEach((part, i) => {
      const u = new SpeechSynthesisUtterance(part);
      u.lang = "pl-PL";
      if (voice) u.voice = voice;
      if (i === parts.length - 1) {
        u.onend = () => {
          speakingRef.current = false;
          setSpeaking(false);
        };
      }
      synth.speak(u);
    });
    speakingRef.current = true;
    setSpeaking(true);
  }

  const btn =
    "min-h-11 px-2 flex items-center gap-1.5 rounded text-body-sm font-semibold text-white hover:bg-white/10 aria-pressed:bg-white/15 aria-pressed:underline aria-pressed:underline-offset-4";
  const square = "flex size-10 items-center justify-center rounded";

  return (
    <div className="w-full border-b border-black/30 bg-toolbar text-white">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-x-space-sm gap-y-1 px-gutter-sm py-1 sm:px-gutter">
        <div className="flex flex-wrap items-center gap-space-sm">
          <a className="rounded border border-white/40 px-2.5 py-1.5 text-label-sm font-semibold text-white hover:bg-white hover:text-toolbar" href="#main-content">
            Przejdź do treści
          </a>
          <span aria-hidden="true" className="hidden text-white/40 sm:inline">
            |
          </span>
          <Link className="hidden rounded px-1 py-1.5 text-label-sm text-white/90 hover:text-white hover:underline sm:inline" href="/deklaracja-dostepnosci">
            Dla osób z niepełnosprawnościami
          </Link>
        </div>
        <div className="flex flex-wrap items-center gap-1 sm:gap-3" role="group" aria-label="Ustawienia dostępności">
          <button
            type="button"
            className={btn}
            aria-label={`A+, rozmiar tekstu ${textScale}%`}
            title="Zmień rozmiar tekstu"
            onClick={() => applyScale(NEXT_SCALE[textScale])}
          >
            <Icon name="format_size" />
            <span>A+</span>
            {textScale !== "100" && <span className="text-label-sm text-white/90">{textScale}%</span>}
          </button>
          <button type="button" className={btn} aria-pressed={contrast === "high"} onClick={toggleContrast}>
            <Icon name="contrast" />
            <span className="sr-only sm:not-sr-only">Kontrast</span>
          </button>
          <button
            type="button"
            className={`${btn} disabled:opacity-70`}
            aria-pressed={speaking}
            onClick={toggleSpeech}
            disabled={!canSpeak}
            title={canSpeak ? "Czyta zaznaczony tekst albo całą treść strony" : "Przeglądarka nie obsługuje syntezy mowy"}
          >
            <Icon name={speaking ? "stop_circle" : "volume_up"} />
            <span className="sr-only sm:not-sr-only">{speaking ? "Zatrzymaj czytanie" : "Czytaj na głos"}</span>
          </button>
          <span aria-hidden="true" className="mx-1 hidden h-4 w-px bg-white/25 md:block" />
          <Link
            href="/deklaracja-dostepnosci"
            aria-label="Udogodnienia dla osób z niepełnosprawnościami"
            title="Udogodnienia dla osób z niepełnosprawnościami"
            className={`${square} bg-secondary text-on-secondary hover:bg-secondary-hover`}
          >
            <Icon name="accessible" />
          </Link>
          <Link
            href="/innowacje#szukaj"
            aria-label="Szukaj innowacji"
            title="Szukaj innowacji"
            className={`${square} bg-white/10 text-white hover:bg-white/20`}
          >
            <Icon name="search" />
          </Link>
        </div>
      </div>
    </div>
  );
}
