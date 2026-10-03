"use client";

import { useId, useState } from "react";
import type { Thread, ThreadReply } from "@/lib/demo-data";
import { Icon } from "@/components/Icon";

const field =
  "min-h-12 rounded-lg border border-outline bg-surface-container-lowest px-4 text-body-sm text-on-surface";
const primaryBtn =
  "flex min-h-12 items-center gap-2 rounded-lg bg-primary px-5 text-label-md font-semibold text-on-primary shadow-sm hover:bg-primary-hover";
const quietBtn =
  "flex min-h-11 items-center gap-1.5 rounded-lg border border-border-subtle bg-surface-container-lowest px-3.5 text-label-sm font-medium text-primary shadow-sm hover:bg-surface-container hc-edge";

const ROLE_STYLE: Record<ThreadReply["kind"], { icon: string; badge: string }> = {
  expert: { icon: "verified_user", badge: "border-tag-blue-border bg-primary-fixed text-primary font-semibold" },
  mentor: { icon: "school", badge: "border-tag-blue-border bg-primary-fixed text-primary font-semibold" },
  practitioner: { icon: "person", badge: "border-border-subtle bg-surface-container text-on-surface-variant font-normal" },
};

function Reply({ r }: { r: ThreadReply }) {
  const s = ROLE_STYLE[r.kind];
  return (
    <li className="flex flex-col gap-2 rounded-xl border border-border-subtle bg-surface-container-lowest p-4 shadow-sm hc-edge">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="flex flex-wrap items-center gap-2">
          <Icon name={s.icon} className="text-primary" />
          <span className="text-body-sm font-bold text-primary">{r.author}</span>
          <span className={`rounded border px-2.5 py-0.5 text-label-sm ${s.badge}`}>{r.role}</span>
        </p>
        <span className="text-label-sm font-normal text-on-surface-variant">{r.when}</span>
      </div>
      <p className="text-body-sm text-on-surface">{r.body}</p>
    </li>
  );
}

function ThreadItem({ thread, onStatus }: { thread: Thread; onStatus: (s: string) => void }) {
  const [helpful, setHelpful] = useState(false);
  const [replying, setReplying] = useState(false);
  const [replies, setReplies] = useState(thread.replies);
  const [draft, setDraft] = useState("");
  const boxId = `${thread.id}-reply`;
  const n = replies.length;

  return (
    <li>
      <article aria-labelledby={`${thread.id}-title`} className="flex flex-col gap-3 rounded-xl border border-border-subtle bg-surface-container-low p-5 hc-edge">
        <div className="flex flex-col items-start justify-between gap-2 sm:flex-row sm:items-center">
          <div className="flex items-center gap-3">
            <span aria-hidden="true" className="flex size-10 shrink-0 items-center justify-center rounded-full bg-primary text-body-sm font-bold text-on-primary shadow-sm">
              {thread.initials}
            </span>
            <span className="flex flex-col">
              <span className="text-body-sm font-bold text-primary sm:text-body-md">{thread.author}</span>
              <span className="text-label-sm font-normal text-on-surface-variant">{thread.meta}</span>
            </span>
          </div>
          <span className="flex items-center gap-1.5 rounded-full border border-border-subtle bg-surface-container-lowest px-3 py-1 text-label-sm font-semibold text-primary shadow-sm">
            <Icon name="chat_bubble" size={15} />
            {n === 1 ? "1 odpowiedź" : `${n} odpowiedzi`}
          </span>
        </div>
        <h3 id={`${thread.id}-title`} className="pt-1 text-body-md font-bold text-primary sm:text-headline-sm">
          {thread.title}
        </h3>
        <p className="text-body-sm text-on-surface">{thread.body}</p>
        <div className="flex flex-wrap items-center gap-3 pt-2">
          <button type="button" aria-pressed={helpful} onClick={() => setHelpful((v) => !v)} className={`${quietBtn} aria-pressed:border-secondary-border aria-pressed:bg-secondary-fixed`}>
            <Icon name="thumb_up" size={18} className="text-secondary" />
            <span>
              Pomocne (<span className="font-bold">{thread.helpful + (helpful ? 1 : 0)}</span>)
            </span>
          </button>
          <button type="button" aria-expanded={replying} aria-controls={boxId} onClick={() => setReplying((v) => !v)} className={quietBtn}>
            <Icon name="reply" size={18} />
            <span>Odpowiedz na ten wątek</span>
          </button>
        </div>
        <div className="mt-2 flex flex-col gap-3 border-l-2 border-primary/20 pl-3 sm:pl-6">
          {n > 0 && (
            <ul className="flex flex-col gap-3" aria-label="Odpowiedzi">
              {replies.map((r, i) => (
                <Reply key={i} r={r} />
              ))}
            </ul>
          )}
          <form
            id={boxId}
            hidden={!replying}
            className="flex flex-col gap-2 rounded-xl border border-border-subtle bg-surface-container p-3"
            onSubmit={(e) => {
              e.preventDefault();
              if (!draft.trim()) return;
              setReplies((r) => [...r, { author: "Ty", role: "Czeka na moderację ROPS", kind: "practitioner", when: "przed chwilą", body: draft.trim() }]);
              setDraft("");
              setReplying(false);
              onStatus("Odpowiedź dodana. Po weryfikacji przez moderatora ROPS będzie widoczna dla wszystkich.");
            }}
          >
            <label htmlFor={`${boxId}-input`} className="text-label-sm font-semibold text-primary">
              Twoja odpowiedź w wątku „{thread.title}”:
            </label>
            <textarea
              id={`${boxId}-input`}
              rows={2}
              required
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              placeholder="Wpisz treść swojej wskazówki lub zapytania..."
              className={`${field} py-2.5`}
            />
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setReplying(false)} className="min-h-12 rounded-lg px-3 text-label-sm font-semibold text-on-surface-variant hover:bg-surface-container-high">
                Anuluj
              </button>
              <button type="submit" className={primaryBtn}>
                <Icon name="send" size={18} />
                Wyślij odpowiedź
              </button>
            </div>
          </form>
        </div>
      </article>
    </li>
  );
}

export function Community({ threads }: { threads: Thread[] }) {
  const [open, setOpen] = useState(false);
  const [list, setList] = useState(threads);
  const [status, setStatus] = useState("");
  const formId = useId();

  return (
    <section aria-labelledby="community-heading" className="flex flex-col gap-6 rounded-xl border border-border-subtle bg-surface-container-lowest p-6 shadow-sm hc-edge lg:p-8">
      <div className="flex flex-col items-start justify-between gap-4 border-b border-border-subtle pb-4 sm:flex-row sm:items-center">
        <div>
          <h2 id="community-heading" className="flex items-center gap-2.5 text-headline-md font-bold text-primary sm:text-[1.5rem]">
            <Icon name="forum" size={26} />
            Społeczność i wymiana doświadczeń
          </h2>
          <p className="mt-1 text-body-sm text-on-surface-variant">
            Otwarte forum pytań, odpowiedzi i wskazówek od praktyków w Małopolsce ({list.length}{" "}
            {list.length === 1 ? "aktywny wątek" : list.length >= 2 && list.length <= 4 ? "aktywne wątki" : "aktywnych wątków"}).
          </p>
        </div>
        <button type="button" aria-expanded={open} aria-controls={formId} onClick={() => setOpen((v) => !v)} className={`${primaryBtn} whitespace-nowrap`}>
          <Icon name="add_comment" />
          Utwórz nowy wątek
        </button>
      </div>

      <div id={formId} hidden={!open} className="flex flex-col gap-4 rounded-xl border border-border-subtle bg-surface-container-low p-5 hc-edge">
        <h3 className="text-body-md font-bold text-primary">Dodaj nowy wątek dyskusyjny</h3>
        <p className="text-label-sm font-normal text-on-surface-variant">Wszystkie pola są wymagane.</p>
        <form
          className="flex flex-col gap-space-sm"
          onSubmit={(e) => {
            e.preventDefault();
            const f = new FormData(e.currentTarget);
            const author = String(f.get("author"));
            setList((l) => [
              ...l,
              {
                id: `thread-new-${l.length + 1}`,
                author: `${author} (czeka na moderację)`,
                initials: author
                  .split(/\s+/)
                  .map((w) => w[0] ?? "")
                  .join("")
                  .slice(0, 2)
                  .toUpperCase(),
                meta: "Przed chwilą",
                title: String(f.get("title")),
                body: String(f.get("body")),
                helpful: 0,
                replies: [],
              },
            ]);
            e.currentTarget.reset();
            setOpen(false);
            setStatus("Dziękujemy! Wątek został dodany i czeka na weryfikację moderatora ROPS.");
          }}
        >
          <div className="flex flex-col gap-1">
            <label htmlFor="new-thread-title" className="text-body-sm font-semibold text-primary">
              Tytuł problemu lub pytania
            </label>
            <input id="new-thread-title" name="title" required className={field} placeholder="np. Skąd pozyskać środki na materiały plastyczne?" />
          </div>
          <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
            <div className="flex flex-col gap-1">
              <label htmlFor="author-name" className="text-body-sm font-semibold text-primary">
                Imię i nazwisko / rola
              </label>
              <input id="author-name" name="author" required autoComplete="name" className={field} placeholder="np. Jan Kowalski (OPS Zakliczyn)" />
            </div>
            <div className="flex flex-col gap-1">
              <label htmlFor="author-email" className="text-body-sm font-semibold text-primary">
                Adres e-mail (do powiadomień)
              </label>
              <input id="author-email" name="email" type="email" required autoComplete="email" className={field} placeholder="twoj.email@instytucja.pl" />
            </div>
          </div>
          <div className="flex flex-col gap-1">
            <label htmlFor="thread-body" className="text-body-sm font-semibold text-primary">
              Treść pytania lub uwagi z wdrożenia
            </label>
            <textarea id="thread-body" name="body" required rows={4} className={`${field} py-3`} placeholder="Opisz kontekst Twojej gminy, wyzwania z wolontariuszami lub pytania do autorów..." />
          </div>
          <div className="flex justify-end gap-space-xs pt-space-xs">
            <button type="button" onClick={() => setOpen(false)} className="min-h-12 rounded-lg px-4 text-label-md font-semibold text-on-surface-variant hover:bg-surface-container-high">
              Anuluj
            </button>
            <button type="submit" className={primaryBtn}>
              <Icon name="send" />
              Opublikuj wątek
            </button>
          </div>
        </form>
      </div>

      <p role="status" className="text-body-sm font-semibold text-primary">
        {status}
      </p>

      {list.length > 0 ? (
        <ul className="flex flex-col gap-4">
          {list.map((t) => (
            <ThreadItem key={t.id} thread={t} onStatus={setStatus} />
          ))}
        </ul>
      ) : (
        <p className="text-body-md text-on-surface-variant">Nie ma jeszcze wątków. Zadaj pierwsze pytanie autorom innowacji.</p>
      )}
    </section>
  );
}
