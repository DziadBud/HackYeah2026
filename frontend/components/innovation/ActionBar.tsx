"use client";

import { useEffect, useId, useRef, useState } from "react";
import { api, ApiError, type LikeState } from "@/lib/api";
import { Icon } from "@/components/Icon";

const CLIENT_KEY = "hubmi-client-id";

// one anonymous id per browser, so a like can be taken back; null when storage is blocked
function clientId(): string | null {
  try {
    let id = localStorage.getItem(CLIENT_KEY);
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem(CLIENT_KEY, id);
    }
    return id;
  } catch {
    return null;
  }
}

function likesLabel(n: number): string {
  if (n === 1) return "1 polubienie";
  const tens = n % 100;
  const ones = n % 10;
  if (ones >= 2 && ones <= 4 && (tens < 12 || tens > 14)) return `${n} polubienia`;
  return `${n} polubień`;
}

const field =
  "min-h-12 w-full rounded-lg border-[1.5px] border-outline bg-surface p-space-sm text-body-md text-on-surface";

export function ActionBar({
  innovationId,
  pdfUrl,
  title,
  filmAnchor,
}: {
  innovationId: string;
  // null: no pdf for this innovation, so no download tile
  pdfUrl: string | null;
  title: string;
  // id of the film section on the page; no tile when the innovation has no film
  filmAnchor?: string;
}) {
  const [copied, setCopied] = useState(false);
  const [like, setLike] = useState<LikeState>({ like_count: 0, liked: false });
  const [likeBusy, setLikeBusy] = useState(false);
  const [likeStatus, setLikeStatus] = useState("");
  const [formOpen, setFormOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState("");
  const [error, setError] = useState("");
  const emailRef = useRef<HTMLInputElement>(null);
  const formId = useId();

  useEffect(() => {
    if (!formOpen) return;
    emailRef.current?.focus();
  }, [formOpen]);

  useEffect(() => {
    const id = clientId();
    if (!id) return;
    let live = true;
    api
      .likes(innovationId, id)
      .then((s) => live && setLike(s))
      .catch(() => {
        // the count is a nice-to-have; the button still works when the api comes back
      });
    return () => {
      live = false;
    };
  }, [innovationId]);

  async function toggleLike() {
    const next = !like.liked;
    const id = clientId();
    setLikeStatus("");
    if (!id) {
      setLikeStatus("Przeglądarka blokuje zapis danych strony, więc nie można polubić.");
      return;
    }
    setLikeBusy(true);
    try {
      // no success message: aria-pressed and the count already say it
      setLike(await api.setLike(innovationId, id, next));
    } catch {
      setLikeStatus("Nie udało się zapisać polubienia. Spróbuj ponownie.");
    } finally {
      setLikeBusy(false);
    }
  }

  async function copyLink() {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
    } catch {
      setCopied(false);
    }
  }

  return (
    <div className="flex flex-col gap-space-sm rounded-xl bg-surface-container-low p-space-md hc-edge">
      <div className="flex flex-col items-stretch gap-space-sm sm:flex-row sm:flex-wrap sm:items-center">
        <button
          type="button"
          aria-expanded={formOpen}
          aria-controls={formId}
          onClick={() => {
            setFormOpen((v) => !v);
            setError("");
            setStatus("");
          }}
          className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-secondary px-space-md py-2 text-center text-label-lg font-semibold text-on-secondary shadow-sm hover:bg-secondary-hover"
        >
          <Icon name="how_to_reg" size={22} />
          <span>Zgłoś się do testowania</span>
        </button>
        {pdfUrl && (
          <a
            href={pdfUrl}
            download
            className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-surface-container-lowest px-space-md py-2 text-center text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge"
          >
            <Icon name="download" size={22} />
            <span>
              Więcej informacji (PDF)
              <span className="sr-only">, pobiera plik</span>
            </span>
          </a>
        )}
        {filmAnchor && (
          <a
            href={`#${filmAnchor}`}
            className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-surface-container-lowest px-space-md py-2 text-center text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge"
          >
            <Icon name="play_circle" size={22} />
            <span>Zobacz film</span>
          </a>
        )}
        <button
          type="button"
          onClick={copyLink}
          className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-surface-container-lowest px-space-md py-2 text-label-lg font-semibold text-primary shadow-sm hover:bg-surface-container-high hc-edge"
        >
          <Icon name="content_copy" size={22} />
          <span>Skopiuj link do tej strony</span>
        </button>
        <span role="status" className="text-body-md font-semibold text-primary">
          {copied ? "Skopiowano link." : likeStatus}
        </span>
        <button
          type="button"
          aria-pressed={like.liked}
          disabled={likeBusy}
          onClick={toggleLike}
          className={`flex min-h-12 items-center justify-center gap-2 rounded-lg px-space-md py-2 text-label-lg font-semibold shadow-sm disabled:cursor-wait disabled:opacity-80 hc-edge sm:ml-auto ${
            like.liked
              ? "bg-primary text-on-primary hover:bg-primary-container"
              : "bg-surface-container-lowest text-primary hover:bg-surface-container-high"
          }`}
        >
          <Icon name="thumb_up" size={22} fill={like.liked} />
          <span>{like.liked ? "Lubisz to" : "Lubię to"}</span>
          <span className="text-body-md font-normal">({likesLabel(like.like_count)})</span>
        </button>
      </div>

      {formOpen && (
        <form
          id={formId}
          className="flex flex-col gap-space-sm rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge"
          onSubmit={async (e) => {
            e.preventDefault();
            const mail = email.trim();
            if (!mail) {
              setError("Podaj adres e-mail, na który ROPS ma się odezwać.");
              return;
            }
            setBusy(true);
            setError("");
            setStatus("");
            try {
              await api.signUpForTest(innovationId, { email: mail, consent: true });
              setStatus(
                "Dziękujemy! ROPS przejrzy zgłoszenie i napisze na podany e-mail, czy możesz przetestować tę innowację.",
              );
              setEmail("");
              setFormOpen(false);
            } catch (err) {
              setError(
                err instanceof ApiError && err.status === 404
                  ? "Ta innowacja nie przyjmuje teraz zgłoszeń do testów."
                  : "Nie udało się wysłać zgłoszenia. Sprawdź połączenie i spróbuj ponownie.",
              );
            } finally {
              setBusy(false);
            }
          }}
        >
          <h2 className="flex items-center gap-2 text-headline-sm font-semibold text-primary">
            <Icon name="mail" size={22} />
            Zostaw e-mail do kontaktu
          </h2>
          <p className="text-body-md text-on-surface-variant">
            Koordynator ROPS przejrzy zgłoszenie. O decyzji w sprawie testów innowacji „{title}” dowiesz się
            mailowo.
          </p>
          <div className="flex flex-col gap-1">
            <label htmlFor={`${formId}-email`} className="text-label-lg font-semibold text-primary">
              Adres e-mail
            </label>
            <input
              ref={emailRef}
              id={`${formId}-email`}
              type="email"
              required
              maxLength={254}
              autoComplete="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={field}
              placeholder="twoj.email@instytucja.pl"
            />
          </div>
          <label className="flex min-h-12 items-start gap-space-sm text-body-md text-on-surface">
            <input type="checkbox" required className="mt-0.5 size-6 shrink-0 accent-primary-container" />
            <span>Zgadzam się na kontakt ROPS w sprawie testowania tej innowacji.</span>
          </label>
          <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
            {error || status}
          </p>
          <div className="flex flex-wrap justify-end gap-space-xs">
            <button
              type="button"
              onClick={() => {
                setFormOpen(false);
                setError("");
              }}
              className="min-h-12 rounded-lg px-space-md text-body-md font-bold text-on-surface-variant hover:bg-surface-container-high"
            >
              Anuluj
            </button>
            <button
              type="submit"
              disabled={busy}
              className="flex min-h-12 items-center justify-center gap-2 rounded-lg bg-secondary px-space-md text-label-lg font-semibold text-on-secondary hover:bg-secondary-hover disabled:cursor-wait disabled:opacity-80"
            >
              <Icon name="send" />
              Wyślij zgłoszenie
            </button>
          </div>
        </form>
      )}

      {!formOpen && status && (
        <p role="status" className="text-body-md font-semibold text-primary">
          {status}
        </p>
      )}
    </div>
  );
}
