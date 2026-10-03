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

const SCALES: { value: TextScale; label: string; name: string }[] = [
  { value: "100", label: "A", name: "Standardowy rozmiar tekstu" },
  { value: "115", label: "A+", name: "Większy tekst" },
  { value: "130", label: "A++", name: "Największy tekst" },
];

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
    "min-h-12 px-space-sm flex items-center gap-1 rounded text-on-primary hover:bg-primary aria-pressed:bg-primary aria-pressed:underline aria-pressed:underline-offset-4";

  return (
    <div className="w-full bg-primary-container text-on-primary">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-x-space-sm px-gutter-sm text-label-md font-semibold sm:px-gutter">
        <div className="flex flex-wrap items-center gap-x-space-sm">
          {/* on phones the skip link shows only on focus, so the toolbar keeps to two rows */}
          <a
            className="sr-only flex min-h-12 items-center rounded px-space-xs underline focus:not-sr-only sm:not-sr-only"
            href="#main-content"
          >
            Przejdź do treści głównej
          </a>
          <span aria-hidden="true" className="hidden opacity-60 sm:inline">
            |
          </span>
          <Link className="flex min-h-12 items-center rounded px-space-xs hover:underline" href="/deklaracja-dostepnosci">
            Deklaracja dostępności
          </Link>
        </div>
        <div className="flex flex-wrap items-center gap-space-xs" role="group" aria-label="Ustawienia dostępności">
          <div className="flex items-center" role="group" aria-label="Rozmiar tekstu">
            <Icon name="format_size" className="mx-1 hidden sm:inline-block" />
            {SCALES.map((s) => (
              <button
                key={s.value}
                type="button"
                className={`${btn} font-bold`}
                aria-pressed={textScale === s.value}
                aria-label={`${s.label}, ${s.name.toLowerCase()}`}
                onClick={() => applyScale(s.value)}
              >
                {s.label}
              </button>
            ))}
          </div>
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
        </div>
      </div>
    </div>
  );
}
