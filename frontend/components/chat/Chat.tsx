"use client";

import { useEffect, useRef, useState } from "react";
import { api, type Innovation } from "@/lib/api";
import { demoMatch } from "@/lib/demo-data";
import { Icon } from "@/components/Icon";
import { InnovationCard } from "@/components/InnovationCard";

type Message =
  | { id: number; role: "user"; text: string }
  | { id: number; role: "assistant"; time: string; innovations: Innovation[]; demo: boolean };

const QUICK_ACTIONS = [
  {
    icon: "search_check",
    title: "Szukam rozwiązania",
    desc: "Znajdź innowację pasującą do problemu w gminie",
    prompt: "Szukam sprawdzonego rozwiązania problemu: ",
  },
  {
    icon: "lightbulb",
    title: "Mam pomysł",
    desc: "Zgłoś autorski pomysł i uzyskaj dofinansowanie",
    prompt: "Chcę zgłosić pomysł na nową innowację społeczną: ",
  },
  {
    icon: "apartment",
    title: "Jestem z instytucji",
    desc: "Dopasuj model do potrzeb Ośrodka Pomocy lub Gminy",
    prompt: "Reprezentuję jednostkę samorządu terytorialnego lub OPS. Potrzebujemy: ",
  },
  {
    icon: "flaky",
    title: "Chcę testować",
    desc: "Sprawdź nowe prototypy i weź udział w testach",
    prompt: "Chciałbym przystąpić do testowania innowacji społecznej: ",
  },
];

const FOLLOW_UP = "\n\nGmina lub miejscowość: \nKogo dotyczy problem: \nCo już próbowaliście: ";

// minimal shape of the web speech recognition api (not in lib.dom yet)
interface Recognition {
  lang: string;
  interimResults: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onend: (() => void) | null;
  onerror: (() => void) | null;
  start(): void;
  stop(): void;
}
type RecognitionCtor = new () => Recognition;

function innovationsPhrase(n: number) {
  if (n === 1) return "1 sprawdzoną innowację społeczną";
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${n} sprawdzone innowacje społeczne`;
  return `${n} sprawdzonych innowacji społecznych`;
}

function now() {
  return new Date().toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" });
}

export function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [pending, setPending] = useState(false);
  const [status, setStatus] = useState("");
  const [recording, setRecording] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<Recognition | null>(null);
  const nextId = useRef(1);

  useEffect(() => () => recognitionRef.current?.stop(), []);

  function fillPrompt(text: string, note: string) {
    setInput(text);
    setStatus(note);
    requestAnimationFrame(() => {
      const ta = textareaRef.current;
      if (!ta) return;
      ta.focus();
      ta.setSelectionRange(text.length, text.length);
    });
  }

  async function send() {
    const text = input.trim();
    if (!text) {
      setStatus("Wpisz wiadomość lub skorzystaj z przycisku Dopełnij tekst z AI.");
      textareaRef.current?.focus();
      return;
    }
    setMessages((m) => [...m, { id: nextId.current++, role: "user", text }]);
    setInput("");
    setStatus("");
    setPending(true);
    let innovations: Innovation[];
    let demo = false;
    try {
      innovations = (await api.match(text)).innovations;
    } catch {
      // match-api not up yet: answer from the bundled demo data instead of failing
      innovations = demoMatch(text);
      demo = true;
    }
    setMessages((m) => [...m, { id: nextId.current++, role: "assistant", time: now(), innovations, demo }]);
    setPending(false);
  }

  function completeWithAi() {
    if (!input.trim()) {
      setStatus("Najpierw opisz problem kilkoma słowami, a podpowiem, co warto dodać.");
      textareaRef.current?.focus();
      return;
    }
    if (input.includes("Gmina lub miejscowość:")) {
      setStatus("Pytania pomocnicze są już w treści. Uzupełnij je i wyślij.");
      return;
    }
    fillPrompt(input + FOLLOW_UP, "Dodano pytania pomocnicze. Uzupełnij je, żeby wyniki były trafniejsze.");
  }

  function toggleRecording() {
    if (recording) {
      recognitionRef.current?.stop();
      return;
    }
    const w = window as unknown as { SpeechRecognition?: RecognitionCtor; webkitSpeechRecognition?: RecognitionCtor };
    const Ctor = w.SpeechRecognition ?? w.webkitSpeechRecognition;
    if (!Ctor) {
      setStatus("Ta przeglądarka nie obsługuje dyktowania. Spróbuj w Chrome lub Edge albo wpisz tekst.");
      return;
    }
    const rec = new Ctor();
    rec.lang = "pl-PL";
    rec.interimResults = false;
    rec.onresult = (e) => {
      const said = Array.from(e.results)
        .map((r) => r[0].transcript)
        .join(" ");
      setInput((prev) => (prev ? `${prev} ${said}` : said));
    };
    rec.onerror = () => setStatus("Nie udało się rozpoznać mowy. Sprawdź uprawnienia do mikrofonu.");
    rec.onend = () => {
      setRecording(false);
      recognitionRef.current = null;
      textareaRef.current?.focus();
    };
    recognitionRef.current = rec;
    rec.start();
    setRecording(true);
    setStatus("Nasłuchuję. Powiedz swoje pytanie, potem kliknij Zatrzymaj nagrywanie.");
  }

  const secondaryBtn =
    "flex min-h-12 items-center gap-space-xs rounded-lg px-space-md text-body-md font-bold text-primary";

  return (
    <div className="mx-auto flex w-full max-w-[820px] flex-col gap-space-lg py-space-md">
      <section
        aria-labelledby="chat-welcome-heading"
        className="relative flex flex-col gap-space-sm overflow-hidden rounded-xl bg-surface-container-low p-space-md shadow-sm hc-edge md:p-space-lg"
      >
        <div aria-hidden="true" className="pointer-events-none absolute -right-12 -top-12 size-48 rounded-full bg-primary/5" />
        <p className="flex items-center gap-space-xs text-label-md font-semibold uppercase tracking-wider text-primary">
          <Icon name="smart_toy" fill />
          <span>Inteligentny Asystent Społeczny • ROPS Kraków</span>
        </p>
        <h1 id="chat-welcome-heading" className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">
          Dzień dobry! W czym mogę pomóc?
        </h1>
        <p className="max-w-2xl text-body-lg text-on-surface-variant">
          Opisz problem w swojej okolicy, zapytaj o innowacje albo podziel się pomysłem. System pomoże Ci dobrać
          przetestowane modele wsparcia z Małopolski.
        </p>
        <div className="flex items-center gap-space-sm pt-space-xs">
          <a
            href="#o-hubie"
            className="inline-flex min-h-11 items-center gap-space-xs rounded-lg bg-surface-container px-space-md text-label-md font-semibold text-primary hover:bg-surface-container-high"
          >
            <Icon name="info" />
            <span>O nas / Czym jest Hub</span>
            <Icon name="arrow_forward" size={18} />
          </a>
        </div>
        <h2 className="sr-only">Szybkie akcje</h2>
        <ul className="mt-space-xs grid grid-cols-1 gap-space-sm sm:grid-cols-2">
          {QUICK_ACTIONS.map((a) => (
            <li key={a.title}>
              <button
                type="button"
                onClick={() => fillPrompt(a.prompt, `Wstawiono szablon: ${a.title}. Dokończ opis i wyślij.`)}
                className="group flex h-full w-full items-start gap-space-sm rounded-xl bg-surface-container-lowest p-space-md text-left shadow-sm hover:bg-surface-container-high hc-edge"
              >
                <span className="flex size-12 shrink-0 items-center justify-center rounded-lg bg-surface-container text-primary group-hover:bg-primary group-hover:text-on-primary">
                  <Icon name={a.icon} size={28} />
                </span>
                <span className="flex min-w-0 flex-col">
                  <span className="text-body-lg font-bold text-primary">{a.title}</span>
                  <span className="mt-0.5 text-caption text-on-surface-variant">{a.desc}</span>
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <section aria-labelledby="chat-log-heading" className="flex flex-col gap-space-lg" hidden={messages.length === 0 && !pending}>
        <h2 id="chat-log-heading" className="sr-only">
          Rozmowa z asystentem
        </h2>
        <div role="log" aria-busy={pending} className="flex flex-col gap-space-lg">
          {messages.map((m) =>
            m.role === "user" ? (
              <div key={m.id} className="flex max-w-[92%] flex-col items-end self-end sm:max-w-[85%]">
                <p className="sr-only">Ty napisałeś(-aś):</p>
                <div className="whitespace-pre-line rounded-xl rounded-tr-none bg-primary p-space-md text-body-lg text-on-primary shadow-md">
                  {m.text}
                </div>
              </div>
            ) : (
              <div key={m.id} className="flex w-full max-w-[95%] flex-col items-start gap-space-xs self-start sm:max-w-[90%]">
                <p className="flex items-center gap-space-xs px-space-xs">
                  <span aria-hidden="true" className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary-container text-on-primary shadow-sm">
                    <Icon name="support_agent" size={18} />
                  </span>
                  <span className="text-body-md font-bold text-primary">Asystent Małopolskiego Hubu</span>
                  <span className="text-caption text-on-surface-variant">
                    • <time>{m.time}</time>
                  </span>
                </p>
                <div className="flex w-full flex-col gap-space-md rounded-xl rounded-tl-none bg-surface-container-lowest p-space-md text-on-surface shadow-sm hc-edge md:p-space-lg">
                  {m.innovations.length > 0 ? (
                    <p className="text-body-lg">
                      Znalazłem <strong>{innovationsPhrase(m.innovations.length)}</strong> z Małopolski, które pasują
                      do opisanego problemu:
                    </p>
                  ) : (
                    <p className="text-body-lg">
                      Nie znalazłem jeszcze innowacji pasującej do tego opisu. Doprecyzuj problem (kogo dotyczy, gdzie
                      występuje) albo zgłoś własny pomysł, a przekażemy go do ROPS.
                    </p>
                  )}
                  {m.innovations.length > 0 && (
                    <div className="grid grid-cols-1 gap-space-md md:grid-cols-2">
                      {m.innovations.map((i) => (
                        <InnovationCard key={i.id} innovation={i} />
                      ))}
                    </div>
                  )}
                  {m.demo && (
                    <p className="flex items-start gap-2 rounded-lg bg-surface-container p-space-sm text-caption text-on-surface-variant">
                      <Icon name="info" size={18} className="mt-0.5 text-primary" />
                      <span>Tryb demonstracyjny: serwer dopasowań jest niedostępny, wyniki pochodzą z przykładowej bazy innowacji.</span>
                    </p>
                  )}
                </div>
              </div>
            ),
          )}
          {pending && (
            <p className="flex items-center gap-space-xs self-start px-space-xs text-body-md text-on-surface-variant">
              <Icon name="support_agent" className="text-primary" />
              Asystent szuka pasujących innowacji…
            </p>
          )}
        </div>
      </section>

      <section
        aria-labelledby="chat-input-heading"
        className="z-30 mt-space-md flex flex-col gap-space-sm rounded-xl bg-surface-container-lowest p-space-md shadow-xl hc-edge md:sticky md:bottom-4"
      >
        <h2 id="chat-input-heading" className="sr-only">
          Napisz wiadomość
        </h2>
        <form
          className="flex flex-col gap-space-sm"
          onSubmit={(e) => {
            e.preventDefault();
            void send();
          }}
        >
          <div className="flex flex-col gap-1">
            <label htmlFor="chat-message-input" className="text-body-md font-bold text-primary">
              Twoje pytanie lub opis wyzwania społecznego:
            </label>
            <textarea
              ref={textareaRef}
              id="chat-message-input"
              rows={3}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                  e.preventDefault();
                  void send();
                }
              }}
              aria-describedby="chat-input-hint"
              placeholder="Opisz problem, aby wyszukać innowację lub zgłosić własny pomysł..."
              className="w-full resize-y rounded-lg border-[1.5px] border-outline bg-surface p-space-sm text-body-lg text-on-surface md:p-space-md"
            />
            <p id="chat-input-hint" className="text-caption text-on-surface-variant">
              Enter dodaje nową linię, Ctrl + Enter wysyła wiadomość.
            </p>
          </div>
          <div className="flex flex-col items-stretch justify-between gap-space-sm pt-space-xs sm:flex-row sm:items-center">
            <div className="flex flex-wrap items-center gap-space-xs">
              <button
                type="button"
                onClick={completeWithAi}
                className={`${secondaryBtn} bg-surface-container-high shadow-sm hover:bg-surface-variant hc-edge`}
              >
                <Icon name="auto_awesome" size={22} fill className="text-secondary" />
                <span>Dopełnij tekst z AI</span>
              </button>
              <button
                type="button"
                onClick={toggleRecording}
                aria-pressed={recording}
                className="flex min-h-12 items-center gap-space-xs rounded-lg bg-surface-container-low px-space-sm text-body-md text-on-surface hover:bg-surface-container-high aria-pressed:bg-secondary-fixed aria-pressed:text-on-secondary-fixed hc-edge"
              >
                <Icon name={recording ? "stop_circle" : "mic"} size={22} className="text-primary" />
                <span>{recording ? "Zatrzymaj nagrywanie" : "Nagraj"}</span>
              </button>
            </div>
            <div className="flex shrink-0 flex-wrap items-center gap-space-xs">
              <button
                type="button"
                onClick={() =>
                  fillPrompt(
                    input.trim() ? input : "Zgłaszam propozycję nowej innowacji społecznej: ",
                    "Opisz swój pomysł: na czym polega, dla kogo jest i na jakim jest etapie.",
                  )
                }
                className={`${secondaryBtn} justify-center bg-surface-container-high hover:bg-surface-container-highest hc-edge`}
              >
                <Icon name="add_circle" className="text-secondary" />
                <span>Zgłoś własną innowację</span>
              </button>
              <button
                type="submit"
                disabled={pending}
                className="flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-primary px-space-lg text-body-lg font-bold text-on-primary shadow-md hover:bg-primary-container disabled:cursor-wait disabled:opacity-80"
              >
                <span>{pending ? "Szukam…" : "Wyszukaj innowację"}</span>
                <Icon name="search" size={22} />
              </button>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2 rounded-lg bg-surface-container p-2 text-caption text-primary">
            <input
              id="chat-attachment"
              type="file"
              accept=".pdf,.docx,image/*"
              className="peer sr-only"
              onChange={(e) => {
                const f = e.target.files?.[0];
                setFileName(f ? f.name : null);
                if (f) setStatus(`Dołączono plik: ${f.name}.`);
              }}
            />
            <label
              htmlFor="chat-attachment"
              className="flex min-h-11 cursor-pointer items-center gap-2 rounded px-2 underline peer-focus-visible:outline-3 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-focus"
            >
              <Icon name="attach_file" size={18} className="text-secondary" />
              Dołącz dokumentację, diagnozę lokalną lub zdjęcie (PDF, DOCX, JPG)
            </label>
            {fileName && <span className="text-on-surface-variant">Wybrano: {fileName}</span>}
          </div>
        </form>
        <p role="status" className="min-h-6 text-caption font-semibold text-primary">
          {status}
        </p>
      </section>

      <section id="o-hubie" aria-labelledby="o-hubie-heading" className="flex flex-col gap-space-xs rounded-xl bg-surface-container-low p-space-md hc-edge md:p-space-lg">
        <h2 id="o-hubie-heading" className="text-headline-sm font-semibold text-primary">
          Czym jest Małopolski Hub Innowacji Społecznych?
        </h2>
        <p className="text-body-md text-on-surface-variant">
          Hub to cyfrowe miejsce spotkań mieszkańców, organizacji pozarządowych, gmin i ekspertów. Regionalny Ośrodek
          Polityki Społecznej w Krakowie od 10 lat szuka, testuje i wdraża innowacje społeczne. W bazie jest blisko 200
          rozwiązań: od przedmiotów codziennego użytku, przez nowe metody pracy, po aplikacje. Asystent łączy opisany
          przez Ciebie problem z rozwiązaniami, które już działają.
        </p>
      </section>
    </div>
  );
}
