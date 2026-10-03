"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, api, type MatchedInnovation, type SimilarProblemReport } from "@/lib/api";
import { demoMatch } from "@/lib/demo-data";
import { areaLabelsFromTags } from "@/lib/labels";
import { Icon } from "@/components/Icon";
import { InnovationCard, type InnovationCardData } from "@/components/InnovationCard";
import { IdeaForm } from "@/components/chat/IdeaForm";
import { SimilarReports } from "@/components/chat/SimilarReports";

type Message =
  | { id: number; role: "user"; text: string }
  | {
      id: number;
      role: "assistant";
      time: string;
      answer: string;
      innovations: InnovationCardData[];
      similar: SimilarProblemReport[];
      demo: boolean;
    };

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
    desc: "Opisz swój pomysł i przekaż go do ROPS",
    prompt: "Chcę zgłosić pomysł na nową innowację społeczną: ",
  },
  {
    icon: "apartment",
    title: "Jestem z instytucji",
    desc: "Dopasuj model do potrzeb Ośrodka Pomocy lub Gminy",
    prompt: "Reprezentuję jednostkę samorządu terytorialnego lub OPS. Potrzebujemy: ",
  },
  {
    icon: "send",
    title: "Złóż wniosek",
    desc: "Wyślij swój pomysł lub innowację do zespołu ROPS",
    // opens the idea form instead of filling the chat
    prompt: "",
  },
];
const APPLY_ACTION = "Złóż wniosek";
const HERO_ACTIONS = QUICK_ACTIONS.filter((a) => a.title !== "Jestem z instytucji");

// minimal shape of the web speech recognition api (not in lib.dom yet)
interface Recognition {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null;
  onend: (() => void) | null;
  onerror: ((e: { error: string }) => void) | null;
  start(): void;
  stop(): void;
}
type RecognitionCtor = new () => Recognition;

// web speech api error codes -> what the user can do about it
const SPEECH_ERRORS: Record<string, string> = {
  "not-allowed": "Brak dostępu do mikrofonu. Zezwól na mikrofon w ustawieniach przeglądarki i spróbuj ponownie.",
  "service-not-allowed": "Brak dostępu do mikrofonu. Zezwól na mikrofon w ustawieniach przeglądarki i spróbuj ponownie.",
  "audio-capture": "Nie znaleziono mikrofonu. Podłącz mikrofon albo wpisz tekst.",
  "no-speech": "Nic nie usłyszałem. Kliknij Nagraj i mów bliżej mikrofonu.",
  network: "Dyktowanie wymaga połączenia z internetem. Sprawdź połączenie albo wpisz tekst.",
};

function innovationsPhrase(n: number) {
  if (n === 1) return "1 sprawdzoną innowację społeczną";
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return `${n} sprawdzone innowacje społeczne`;
  return `${n} sprawdzonych innowacji społecznych`;
}

function toCard(i: MatchedInnovation): InnovationCardData {
  return { id: i.id, title: i.title, summary: i.summary, tags: areaLabelsFromTags(i.tags), city: i.city };
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
  // the hero tiles are single choice; "Złóż wniosek" is the only one that shows the form
  const [action, setAction] = useState<string | null>(null);
  const ideaOpen = action === APPLY_ACTION;
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const recognitionRef = useRef<Recognition | null>(null);
  const nextId = useRef(1);

  useEffect(() => () => recognitionRef.current?.stop(), []);

  // /?wniosek=1 comes from the "Zgłoś się do testowania" box on an innovation page
  useEffect(() => {
    if (new URLSearchParams(window.location.search).has("wniosek")) setAction(APPLY_ACTION);
  }, []);

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
    if (pending) return;
    const text = input.trim();
    if (text.length < 3) {
      setStatus("Opisz problem kilkoma słowami.");
      textareaRef.current?.focus();
      return;
    }
    const userId = nextId.current++;
    setMessages((m) => [...m, { id: userId, role: "user", text }]);
    // bring the question to the top; the answer appears right under it
    requestAnimationFrame(() => document.getElementById(`msg-${userId}`)?.scrollIntoView({ block: "start" }));
    setInput("");
    setStatus("");
    setPending(true);
    let reply: Omit<Extract<Message, { role: "assistant" }>, "id" | "time" | "role">;
    try {
      const res = await api.match({ text });
      reply = {
        answer: res.answer,
        innovations: res.innovations.map(toCard),
        similar: res.similar_reports,
        demo: false,
      };
    } catch (err) {
      if (err instanceof ApiError && err.status >= 400 && err.status < 500 && err.status !== 404) {
        // the request itself was rejected: give the text back instead of faking an answer
        setMessages((m) => m.filter((x) => x.id !== userId));
        setInput(text);
        setPending(false);
        setStatus(
          err.status === 429
            ? "Wysłano zbyt wiele zapytań. Odczekaj chwilę i spróbuj ponownie."
            : "Nie udało się wysłać: sprawdź opis (do 2000 znaków).",
        );
        return;
      }
      // match-api unreachable: answer from the bundled demo data, clearly marked
      reply = { answer: "", innovations: demoMatch(text), similar: [], demo: true };
    }
    setMessages((m) => [...m, { id: nextId.current++, role: "assistant", time: now(), ...reply }]);
    setPending(false);
  }

  function chooseAction(title: string, prompt: string) {
    setAction(title);
    if (title !== APPLY_ACTION) return fillPrompt(prompt, "Wstawiono szablon zapytania do pola tekstowego");
    // the chat is hidden while the form is open
    recognitionRef.current?.stop();
    // a chat template is not an idea summary, so it does not go into the form
    if (QUICK_ACTIONS.some((a) => a.prompt && input.startsWith(a.prompt.trim()))) setInput("");
    setStatus("");
  }

  function closeIdeaForm(msg = "") {
    setAction(null);
    setStatus(msg);
    // the chat is shown again on the next render
    requestAnimationFrame(() => textareaRef.current?.focus());
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
    // keep listening through pauses and show words as they come; stops on the button
    rec.continuous = true;
    rec.interimResults = true;
    // dictation appends to whatever was typed before pressing the button
    const before = input.trimEnd();
    let failed = false;
    rec.onresult = (e) => {
      // results hold the whole session (final + the current guess), so rebuild from scratch
      const said = Array.from(e.results)
        .map((r) => r[0].transcript.trim())
        .filter(Boolean)
        .join(" ");
      setInput((before ? `${before} ${said}` : said).slice(0, 2000));
    };
    rec.onerror = (e) => {
      if (e.error === "aborted") return;
      failed = true;
      setStatus(SPEECH_ERRORS[e.error] ?? "Nie udało się rozpoznać mowy. Spróbuj ponownie albo wpisz tekst.");
    };
    rec.onend = () => {
      setRecording(false);
      recognitionRef.current = null;
      if (!failed) setStatus("Nagrywanie zakończone. Sprawdź tekst w polu i wyślij.");
      textareaRef.current?.focus();
    };
    recognitionRef.current = rec;
    rec.start();
    setRecording(true);
    setStatus("Nasłuchuję. Powiedz swoje pytanie, potem kliknij Zatrzymaj nagrywanie.");
  }

  const secondaryBtn =
    "flex min-h-12 grow items-center justify-center gap-space-xs rounded-full border border-outline bg-surface-container-low px-space-md py-2 text-center text-body-md font-bold text-primary hover:bg-surface-container-high sm:grow-0 hc-edge";

  return (
    <div className="mx-auto flex w-full max-w-[820px] flex-col gap-space-md py-space-md">
      <section
        aria-labelledby="chat-welcome-heading"
        className="flex flex-col gap-space-md rounded-xl bg-surface-container-low p-space-md shadow-sm hc-edge md:p-space-lg"
      >
        <div className="flex flex-col gap-space-sm">
          <p className="flex items-center gap-space-xs text-label-lg font-semibold uppercase tracking-wide text-primary">
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
          <a
            href="#o-hubie"
            hidden={ideaOpen}
            className="inline-flex min-h-12 w-fit items-center gap-space-xs rounded-lg border border-outline bg-surface-container-lowest px-space-md text-body-md font-bold text-primary hover:bg-surface-container-high hc-edge"
          >
            O nas / Czym jest Hub
            <Icon name="arrow_forward" size={20} />
          </a>
        </div>

        {messages.length === 0 && (
          <ul className="grid grid-cols-1 gap-space-sm sm:grid-cols-3">
            {HERO_ACTIONS.map((a) => {
              const selected = action === a.title;
              return (
                <li key={a.title}>
                  <button
                    type="button"
                    aria-pressed={selected}
                    onClick={() => chooseAction(a.title, a.prompt)}
                    className={`group flex h-full w-full flex-col items-start gap-space-xs rounded-xl bg-surface-container-lowest p-space-md text-left shadow-sm hover:bg-surface-container-high hc-edge ${
                      selected ? "border-2 border-primary" : "border border-transparent"
                    }`}
                  >
                    <span className="flex size-12 items-center justify-center rounded-lg bg-surface-container text-primary group-hover:bg-primary group-hover:text-on-primary">
                      <Icon name={a.icon} size={28} />
                    </span>
                    <span className="text-body-lg font-bold text-primary">{a.title}</span>
                    <span className="text-caption text-on-surface-variant">{a.desc}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section aria-labelledby="chat-log-heading" className="flex flex-col gap-space-lg" hidden={ideaOpen || (messages.length === 0 && !pending)}>
        <h2 id="chat-log-heading" className="sr-only">
          Rozmowa z asystentem
        </h2>
        <div role="log" aria-busy={pending} className="flex flex-col gap-space-lg">
          {messages.map((m) =>
            m.role === "user" ? (
              <div key={m.id} id={`msg-${m.id}`} className="flex max-w-[92%] scroll-mt-28 flex-col items-end self-end sm:max-w-[85%]">
                <p className="sr-only">Twoja wiadomość:</p>
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
                  {m.answer && m.innovations.length > 0 && <p className="text-body-lg">{m.answer}</p>}
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
                  {m.similar.length > 0 && <SimilarReports reports={m.similar} />}
                  {m.demo && (
                    <p className="flex items-start gap-2 rounded-lg bg-surface-container p-space-sm text-caption text-on-surface-variant">
                      <Icon name="info" size={18} className="mt-0.5 text-primary" />
                      <span>
                        Tryb demonstracyjny: wyszukiwarka jest chwilowo niedostępna, to przykładowe wyniki z bazy innowacji.
                      </span>
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
        hidden={ideaOpen}
        className="flex flex-col overflow-hidden rounded-xl bg-surface-container-lowest shadow-xl hc-edge"
      >
        <h2 id="chat-input-heading" className="sr-only">
          Napisz wiadomość
        </h2>
        <form
          className="flex flex-col gap-space-sm p-space-md"
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
              maxLength={2000}
              onKeyDown={(e) => {
                if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
                  e.preventDefault();
                  e.currentTarget.form?.requestSubmit();
                }
              }}
              aria-describedby="chat-input-hint"
              placeholder="Opisz problem, aby wyszukać innowację lub zgłosić własny pomysł..."
              className="w-full resize-y rounded-lg border-[1.5px] border-outline bg-surface p-space-sm text-body-lg text-on-surface md:p-space-md"
            />
            <p id="chat-input-hint" className="hidden text-caption text-on-surface-variant sm:block">
              Enter dodaje nową linię, Ctrl + Enter wysyła wiadomość.
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-space-xs pt-space-xs">
            <button
              type="button"
              onClick={toggleRecording}
              aria-pressed={recording}
              className={`${secondaryBtn} aria-pressed:bg-secondary-fixed aria-pressed:text-on-secondary-fixed`}
            >
              <Icon name={recording ? "stop_circle" : "mic"} size={22} className="text-secondary" />
              <span>{recording ? "Zatrzymaj nagrywanie" : "Nagraj"}</span>
            </button>
            <button
              type="submit"
              aria-disabled={pending}
              className="flex min-h-12 w-full items-center justify-center gap-space-xs rounded-lg bg-primary px-space-md py-2 text-center text-body-lg font-bold text-on-primary shadow-md hover:bg-primary-container aria-disabled:cursor-wait aria-disabled:opacity-80 sm:ml-auto sm:w-auto sm:px-space-lg"
            >
              <Icon name="search" size={22} />
              <span>{pending ? "Szukam…" : "Wyszukaj innowację"}</span>
            </button>
          </div>
        </form>
        <p
          role="status"
          className={
            status
              ? "flex min-h-12 items-center gap-space-xs border-t border-surface-container bg-surface-container-low px-space-md text-body-md font-semibold text-primary"
              : "sr-only"
          }
        >
          {status ? (
            <>
              <Icon name="place" size={18} className="shrink-0 text-secondary" />
              <span>{status}</span>
            </>
          ) : (
            "\u00a0"
          )}
        </p>
      </section>

      {ideaOpen && (
        <div id="idea-form">
          <IdeaForm
            initialSummary={input.trim()}
            onCancel={() => closeIdeaForm()}
            onDone={closeIdeaForm}
          />
        </div>
      )}

      <section id="o-hubie" aria-labelledby="o-hubie-heading" hidden={ideaOpen} className="scroll-mt-28 flex flex-col gap-space-xs py-space-sm">
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
