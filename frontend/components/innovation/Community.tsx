"use client";

import { useEffect, useId, useState } from "react";
import { api, type ReplyKind, type Thread, type ThreadReply } from "@/lib/api";
import { Icon } from "@/components/Icon";

const field =
  "min-h-12 rounded-lg border-[1.5px] border-outline bg-surface-container-lowest px-4 text-body-md text-on-surface";
const primaryBtn =
  "flex min-h-12 items-center gap-2 rounded-xl bg-primary px-space-md text-label-lg font-semibold text-on-primary hover:bg-primary-container disabled:cursor-wait disabled:opacity-80";
const quietBtn =
  "flex min-h-12 items-center gap-1.5 rounded-lg bg-surface-container-lowest px-3 text-caption text-primary hover:bg-surface-container hc-edge";

const ROLE: Record<ReplyKind, { label: string; icon: string; badge: string }> = {
  expert: { label: "Ekspert", icon: "verified_user", badge: "bg-tertiary-fixed text-on-tertiary-fixed" },
  mentor: { label: "Mentor innowacji", icon: "school", badge: "bg-primary-fixed text-on-primary-fixed" },
  admin: { label: "ROPS Kraków", icon: "support_agent", badge: "bg-primary-fixed text-on-primary-fixed" },
  practitioner: { label: "Praktyk", icon: "person", badge: "bg-surface-container text-on-surface-variant" },
};

const SEND_FAILED = "Nie udało się wysłać. Sprawdź połączenie z serwerem i spróbuj ponownie.";

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString("pl-PL", { dateStyle: "long" });
}

function initials(label: string) {
  return label
    .split(/\s+/)
    .map((w) => w[0] ?? "")
    .join("")
    .slice(0, 2)
    .toUpperCase();
}

function Reply({ r }: { r: ThreadReply }) {
  const s = ROLE[r.kind];
  return (
    <li className="flex flex-col gap-2 rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="flex flex-wrap items-center gap-2">
          <Icon name={s.icon} size={22} className="text-tertiary-strong" />
          <span className="text-body-md font-bold text-primary">{r.author_label}</span>
          <span className={`rounded px-2 py-0.5 text-caption font-semibold ${s.badge}`}>{s.label}</span>
        </p>
        <time dateTime={r.created_at} className="text-caption text-on-surface-variant">
          {fmtDate(r.created_at)}
        </time>
      </div>
      <p className="whitespace-pre-line text-body-md text-on-surface">{r.body}</p>
    </li>
  );
}

function ThreadItem({ thread, onStatus }: { thread: Thread; onStatus: (s: string) => void }) {
  const [replying, setReplying] = useState(false);
  const [busy, setBusy] = useState(false);
  const boxId = `${thread.id}-reply`;
  const n = thread.replies.length;

  return (
    <li>
      <article aria-labelledby={`${thread.id}-title`} className="flex flex-col gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
        <div className="flex flex-col items-start justify-between gap-2 sm:flex-row sm:items-center">
          <div className="flex items-center gap-2">
            <span aria-hidden="true" className="flex size-10 items-center justify-center rounded-full bg-primary-container text-body-lg font-bold text-on-primary">
              {initials(thread.author_label)}
            </span>
            <span className="flex flex-col">
              <span className="text-body-md font-bold text-primary">{thread.author_label}</span>
              <span className="text-caption text-on-surface-variant">
                Zadano <time dateTime={thread.created_at}>{fmtDate(thread.created_at)}</time>
              </span>
            </span>
          </div>
          <span className="flex items-center gap-1 rounded-full bg-surface-container-high px-3 py-1 text-caption font-semibold text-primary">
            <Icon name="chat_bubble" size={16} />
            {n === 1 ? "1 odpowiedź" : `${n} odpowiedzi`}
          </span>
        </div>
        <h3 id={`${thread.id}-title`} className="pt-1 text-headline-sm font-semibold text-primary">
          {thread.title}
        </h3>
        <p className="whitespace-pre-line text-body-md text-on-surface">{thread.body}</p>
        <div className="flex flex-wrap items-center gap-space-sm pt-space-xs">
          <button type="button" aria-expanded={replying} aria-controls={boxId} onClick={() => setReplying((v) => !v)} className={quietBtn}>
            <Icon name="reply" size={18} />
            <span>Odpowiedz na ten wątek</span>
          </button>
        </div>
        <div className="mt-space-sm flex flex-col gap-space-sm pl-4 sm:pl-8">
          {n > 0 && (
            <ul className="flex flex-col gap-space-sm" aria-label="Odpowiedzi">
              {thread.replies.map((r) => (
                <Reply key={r.id} r={r} />
              ))}
            </ul>
          )}
          <form
            id={boxId}
            hidden={!replying}
            className="flex flex-col gap-2 rounded-xl bg-surface-container p-space-sm"
            onSubmit={async (e) => {
              e.preventDefault();
              const form = e.currentTarget;
              const f = new FormData(form);
              setBusy(true);
              try {
                await api.replyToThread(thread.id, {
                  body: String(f.get("body")).trim(),
                  author_label: String(f.get("author")).trim(),
                });
                form.reset();
                setReplying(false);
                onStatus("Dziękujemy! Odpowiedź czeka na weryfikację moderatora ROPS, potem pojawi się w wątku.");
              } catch {
                onStatus(SEND_FAILED);
              } finally {
                setBusy(false);
              }
            }}
          >
            <label htmlFor={`${boxId}-author`} className="text-label-md font-semibold text-primary">
              Imię i nazwisko / rola
            </label>
            <input id={`${boxId}-author`} name="author" required maxLength={100} autoComplete="name" className={field} placeholder="np. Jan Kowalski (OPS Zakliczyn)" />
            <label htmlFor={`${boxId}-input`} className="text-label-md font-semibold text-primary">
              Twoja odpowiedź w wątku „{thread.title}”:
            </label>
            <textarea
              id={`${boxId}-input`}
              name="body"
              rows={2}
              required
              maxLength={5000}
              placeholder="Wpisz treść swojej wskazówki lub zapytania..."
              className={`${field} py-2.5`}
            />
            <div className="flex justify-end gap-2">
              <button type="button" onClick={() => setReplying(false)} className="min-h-12 rounded-lg px-3 text-label-md font-semibold text-on-surface-variant hover:bg-surface-container-high">
                Anuluj
              </button>
              <button type="submit" disabled={busy} className={primaryBtn}>
                <Icon name="send" size={18} />
                {busy ? "Wysyłam…" : "Wyślij odpowiedź"}
              </button>
            </div>
          </form>
        </div>
      </article>
    </li>
  );
}

// published threads from GET /innovations/{id}/threads; new threads and replies wait for ROPS moderation.
// demoThreads: shown instead when the page itself runs on demo data (api unreachable)
export function Community({ innovationId, demoThreads }: { innovationId: string; demoThreads?: Thread[] }) {
  const [list, setList] = useState<Thread[] | null>(demoThreads ?? null);
  const [loadError, setLoadError] = useState(false);
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("");
  const formId = useId();

  useEffect(() => {
    if (demoThreads) return;
    let live = true;
    api
      .threads(innovationId)
      .then((t) => live && setList(t))
      .catch(() => live && setLoadError(true));
    return () => {
      live = false;
    };
  }, [innovationId, demoThreads]);

  const count = list?.length ?? 0;

  return (
    <section aria-labelledby="community-heading" className="flex flex-col gap-space-lg rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge lg:p-space-lg">
      <div className="flex flex-col items-start justify-between gap-space-sm sm:flex-row sm:items-center">
        <div>
          <h2 id="community-heading" className="flex items-center gap-2 text-headline-md font-semibold text-primary">
            <Icon name="forum" size={28} />
            Społeczność i wymiana doświadczeń
          </h2>
          <p className="text-body-md text-on-surface-variant">
            Otwarte forum pytań, odpowiedzi i wskazówek od praktyków w Małopolsce
            {list && (
              <>
                {" "}
                ({count} {count === 1 ? "aktywny wątek" : count >= 2 && count <= 4 ? "aktywne wątki" : "aktywnych wątków"})
              </>
            )}
            .
          </p>
        </div>
        <button type="button" aria-expanded={open} aria-controls={formId} onClick={() => setOpen((v) => !v)} className={primaryBtn}>
          <Icon name="add_comment" size={22} />
          Utwórz nowy wątek
        </button>
      </div>

      <div id={formId} hidden={!open} className="flex flex-col gap-space-md rounded-xl bg-surface-container-low p-space-md hc-edge">
        <h3 className="text-headline-sm font-semibold text-primary">Dodaj nowy wątek dyskusyjny</h3>
        <p className="text-caption text-on-surface-variant">Pola bez dopisku „opcjonalnie” są wymagane. Wątek pojawi się po weryfikacji przez ROPS.</p>
        <form
          className="flex flex-col gap-space-sm"
          onSubmit={async (e) => {
            e.preventDefault();
            const form = e.currentTarget;
            const f = new FormData(form);
            const mail = email.trim();
            setBusy(true);
            try {
              await api.createThread(innovationId, {
                title: String(f.get("title")).trim(),
                body: String(f.get("body")).trim(),
                author_label: String(f.get("author")).trim(),
                ...(mail ? { email: mail, consent: true } : {}),
              });
              form.reset();
              setEmail("");
              setOpen(false);
              setStatus("Dziękujemy! Wątek czeka na weryfikację moderatora ROPS, potem pojawi się na tej stronie.");
            } catch {
              setStatus(SEND_FAILED);
            } finally {
              setBusy(false);
            }
          }}
        >
          <div className="flex flex-col gap-1">
            <label htmlFor="new-thread-title" className="text-label-lg font-semibold text-primary">
              Tytuł problemu lub pytania
            </label>
            <input id="new-thread-title" name="title" required maxLength={200} className={field} placeholder="np. Skąd pozyskać środki na materiały plastyczne?" />
          </div>
          <div className="grid grid-cols-1 gap-space-sm sm:grid-cols-2">
            <div className="flex flex-col gap-1">
              <label htmlFor="author-name" className="text-label-lg font-semibold text-primary">
                Imię i nazwisko / rola
              </label>
              <input id="author-name" name="author" required maxLength={100} autoComplete="name" className={field} placeholder="np. Jan Kowalski (OPS Zakliczyn)" />
            </div>
            <div className="flex flex-col gap-1">
              <label htmlFor="author-email" className="text-label-lg font-semibold text-primary">
                Adres e-mail do powiadomień (opcjonalnie)
              </label>
              <input
                id="author-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                maxLength={254}
                autoComplete="email"
                className={field}
                placeholder="twoj.email@instytucja.pl"
              />
            </div>
          </div>
          {email.trim() && (
            <label className="flex min-h-12 items-start gap-space-sm text-body-md text-on-surface">
              <input type="checkbox" required className="mt-0.5 size-6 shrink-0 accent-primary-container" />
              <span>Zgadzam się na powiadomienia e-mail o tym wątku (wymagane, gdy podajesz adres).</span>
            </label>
          )}
          <div className="flex flex-col gap-1">
            <label htmlFor="thread-body" className="text-label-lg font-semibold text-primary">
              Treść pytania lub uwagi z wdrożenia
            </label>
            <textarea id="thread-body" name="body" required maxLength={5000} rows={4} className={`${field} py-3`} placeholder="Opisz kontekst Twojej gminy, wyzwania z wolontariuszami lub pytania do autorów..." />
          </div>
          <div className="flex justify-end gap-space-xs pt-space-xs">
            <button type="button" onClick={() => setOpen(false)} className="min-h-12 rounded-xl px-space-md text-label-lg font-semibold text-on-surface-variant hover:bg-surface-container">
              Anuluj
            </button>
            <button type="submit" disabled={busy} className={primaryBtn}>
              <Icon name="send" />
              {busy ? "Wysyłam…" : "Wyślij do moderacji"}
            </button>
          </div>
        </form>
      </div>

      <p role="status" className="text-body-md font-semibold text-primary">
        {status}
      </p>

      {demoThreads && (
        <p className="flex items-start gap-2 rounded-lg bg-surface-container p-space-sm text-caption text-on-surface-variant">
          <Icon name="info" size={18} className="mt-0.5 text-primary" />
          <span>Tryb demonstracyjny: serwer jest niedostępny, pokazujemy przykładowe wątki.</span>
        </p>
      )}

      {list === null ? (
        <p role="status" className="text-body-md text-on-surface-variant">
          {loadError ? "Nie udało się wczytać wątków. Odśwież stronę, aby spróbować ponownie." : "Wczytuję wątki…"}
        </p>
      ) : list.length > 0 ? (
        <ul className="flex flex-col gap-space-md">
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
