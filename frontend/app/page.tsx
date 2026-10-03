"use client";

import { useState } from "react";
import { api, ApiError, type Innovation } from "@/lib/api";

export default function HomePage() {
  const [text, setText] = useState("");
  const [results, setResults] = useState<Innovation[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    setResults(null);
    try {
      const res = await api.match(text);
      setResults(res.innovations);
    } catch (err) {
      // the /match endpoint may not exist yet in this skeleton — show a hint.
      if (err instanceof ApiError && err.status === 404) {
        setError("Endpoint /match nie jest jeszcze zaimplementowany w backendzie.");
      } else {
        setError("Nie udało się połączyć z API. Czy backend jest uruchomiony?");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col gap-8">
      <section className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold">Opisz problem społeczny</h1>
        <p className="text-sm text-black/60 dark:text-white/60">
          Znajdziemy innowacje społeczne z bazy ROPS, które mogą pomóc.
        </p>
      </section>

      <form onSubmit={onSubmit} className="flex flex-col gap-3">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={4}
          placeholder="np. Seniorzy w mojej gminie są samotni i nie mają dostępu do opieki..."
          className="w-full rounded-lg border border-black/15 bg-transparent p-3 text-sm outline-none focus:border-black/40 dark:border-white/15 dark:focus:border-white/40"
        />
        <button
          type="submit"
          disabled={loading}
          className="self-start rounded-lg bg-foreground px-4 py-2 text-sm font-medium text-background disabled:opacity-50"
        >
          {loading ? "Szukam…" : "Szukaj innowacji"}
        </button>
      </form>

      {error && (
        <p className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-sm text-amber-700 dark:text-amber-300">
          {error}
        </p>
      )}

      {results && (
        <section className="flex flex-col gap-3">
          <h2 className="text-lg font-medium">Dopasowane innowacje</h2>
          {results.length === 0 && (
            <p className="text-sm text-black/60 dark:text-white/60">Brak wyników.</p>
          )}
          {results.map((it) => (
            <article
              key={it.id}
              className="rounded-lg border border-black/10 p-4 dark:border-white/10"
            >
              <h3 className="font-medium">{it.title}</h3>
              <p className="mt-1 text-sm text-black/70 dark:text-white/70">{it.summary}</p>
              {it.why && <p className="mt-2 text-sm italic">{it.why}</p>}
            </article>
          ))}
        </section>
      )}
    </div>
  );
}
