"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { adminApi, type AdminReply, type AdminThread, type ModerationStatus } from "@/lib/api";
import { Icon } from "@/components/Icon";
import { card, fmtDate, h2 } from "@/components/admin/styles";

type Filter = ModerationStatus | "all";

const CHOICES: {
  status: ModerationStatus;
  label: string;
  hint: string;
  icon: string;
  on: string;
  off: string;
}[] = [
  {
    status: "pending",
    label: "Nowy",
    hint: "info dla Ciebie",
    icon: "notifications_active",
    on: "bg-secondary text-on-secondary",
    off: "bg-surface-container text-on-surface-variant hover:bg-surface-container-high",
  },
  {
    status: "published",
    label: "Przyjęty",
    hint: "widać na stronie",
    icon: "verified",
    on: "bg-tertiary-fixed text-on-tertiary-fixed",
    off: "bg-surface-container text-on-surface-variant hover:bg-surface-container-high",
  },
  {
    status: "hidden",
    label: "Odmowa",
    hint: "ukryty",
    icon: "close",
    on: "bg-primary text-on-primary",
    off: "bg-surface-container text-on-surface-variant hover:bg-surface-container-high",
  },
];

const FILTERS: { id: Filter; label: string }[] = [
  { id: "pending", label: "Nowe" },
  { id: "published", label: "Przyjęte" },
  { id: "hidden", label: "Odmowa" },
  { id: "all", label: "Wszystkie" },
];

const STRIPE: Record<ModerationStatus, string> = {
  pending: "border-l-secondary",
  published: "border-l-tertiary-strong",
  hidden: "border-l-outline",
};

function needsDecision(t: AdminThread) {
  return t.status === "pending" || t.replies.some((r) => r.status === "pending");
}

function StatusPicker({
  value,
  busy,
  labelledBy,
  onPick,
}: {
  value: ModerationStatus;
  busy: boolean;
  labelledBy: string;
  onPick: (status: ModerationStatus) => void;
}) {
  return (
    <div
      role="radiogroup"
      aria-labelledby={labelledBy}
      className="grid grid-cols-3 gap-1 rounded-xl bg-surface-container p-1 hc-edge"
    >
      {CHOICES.map((c) => {
        const selected = value === c.status;
        return (
          <button
            key={c.status}
            type="button"
            role="radio"
            aria-checked={selected}
            disabled={busy || selected}
            onClick={() => onPick(c.status)}
            className={`flex min-h-12 flex-col items-center justify-center gap-0.5 rounded-lg px-1 py-2 text-center transition-colors disabled:opacity-100 ${
              selected ? c.on : c.off
            }`}
          >
            <span className="flex items-center gap-1 text-label-lg font-bold">
              <Icon name={c.icon} size={18} />
              {c.label}
            </span>
            <span className={`text-caption ${selected ? "opacity-90" : "opacity-80"}`}>{c.hint}</span>
          </button>
        );
      })}
    </div>
  );
}

function ReplyRow({
  reply,
  busy,
  onPick,
}: {
  reply: AdminReply;
  busy: boolean;
  onPick: (id: string, status: ModerationStatus) => void;
}) {
  const labelId = `${reply.id}-h`;
  return (
    <li className={`flex flex-col gap-2 rounded-lg border-l-4 bg-surface-container-lowest p-space-sm hc-edge ${STRIPE[reply.status]}`}>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <p id={labelId} className="text-body-md font-bold text-primary">
          {reply.author_label}
        </p>
        <time dateTime={reply.created_at} className="text-caption text-on-surface-variant">
          {fmtDate(reply.created_at)}
        </time>
      </div>
      <p className="whitespace-pre-line text-body-md text-on-surface">{reply.body}</p>
      <StatusPicker value={reply.status} busy={busy} labelledBy={labelId} onPick={(s) => onPick(reply.id, s)} />
    </li>
  );
}

function ThreadCard({
  thread,
  busyId,
  onThread,
  onReply,
}: {
  thread: AdminThread;
  busyId: string | null;
  onThread: (id: string, status: ModerationStatus) => void;
  onReply: (id: string, status: ModerationStatus) => void;
}) {
  const busy = busyId === thread.id || thread.replies.some((r) => r.id === busyId);
  const titleId = `${thread.id}-h`;

  return (
    <article
      aria-labelledby={titleId}
      className={`flex flex-col gap-space-sm rounded-xl border-l-4 bg-surface-container-low p-space-md hc-edge ${STRIPE[thread.status]} ${
        thread.status === "pending" ? "ring-1 ring-secondary/30" : ""
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <h3 id={titleId} className="text-headline-sm font-semibold text-primary">
            {thread.title}
          </h3>
          <p className="mt-1 text-caption text-on-surface-variant">
            {thread.author_label}
            {thread.email ? ` · ${thread.email}` : ""} · {fmtDate(thread.created_at)}
          </p>
        </div>
        <Link
          href={`/innowacje/${thread.innovation_id}`}
          className="shrink-0 text-label-md font-semibold text-primary underline"
        >
          {thread.innovation_id}
        </Link>
      </div>

      <p className="whitespace-pre-line text-body-md text-on-surface">{thread.body}</p>

      <StatusPicker
        value={thread.status}
        busy={busy}
        labelledBy={titleId}
        onPick={(s) => onThread(thread.id, s)}
      />

      {thread.replies.length > 0 && (
        <ul className="mt-1 flex flex-col gap-space-xs border-t border-outline/20 pt-space-sm">
          {thread.replies.map((r) => (
            <ReplyRow key={r.id} reply={r} busy={busy} onPick={onReply} />
          ))}
        </ul>
      )}
    </article>
  );
}

export function ThreadModeration({
  threads,
  source,
  onChange,
  onNotice,
}: {
  threads: AdminThread[];
  source: "api" | "mock";
  onChange: (next: AdminThread[]) => void;
  onNotice: (msg: string) => void;
}) {
  const [filter, setFilter] = useState<Filter>("pending");
  const [busyId, setBusyId] = useState<string | null>(null);

  const counts = useMemo(() => {
    return {
      pending: threads.filter((t) => t.status === "pending" || t.replies.some((r) => r.status === "pending")).length,
      published: threads.filter((t) => t.status === "published").length,
      hidden: threads.filter((t) => t.status === "hidden").length,
      all: threads.length,
    };
  }, [threads]);

  const visible = useMemo(() => {
    const sorted = [...threads].sort((a, b) => +new Date(b.created_at) - +new Date(a.created_at));
    if (filter === "all") return sorted;
    if (filter === "pending") return sorted.filter(needsDecision);
    return sorted.filter((t) => t.status === filter);
  }, [threads, filter]);

  async function decideThread(id: string, status: ModerationStatus) {
    const current = threads.find((t) => t.id === id);
    if (!current || current.status === status) return;
    setBusyId(id);
    try {
      const updated =
        source === "api" ? await adminApi.setThreadStatus(id, status) : { ...current, status };
      onChange(threads.map((t) => (t.id === id ? updated : t)));
      const c = CHOICES.find((x) => x.status === status)!;
      onNotice(`${c.label} — ${c.hint}.`);
    } catch {
      onNotice("Nie udało się zapisać statusu.");
    } finally {
      setBusyId(null);
    }
  }

  async function decideReply(id: string, status: ModerationStatus) {
    const parent = threads.find((t) => t.replies.some((r) => r.id === id));
    const current = parent?.replies.find((r) => r.id === id);
    if (!parent || !current || current.status === status) return;
    setBusyId(id);
    try {
      const updatedReply =
        source === "api" ? await adminApi.setReplyStatus(id, status) : { ...current, status };
      onChange(
        threads.map((t) =>
          t.id === parent.id
            ? { ...t, replies: t.replies.map((r) => (r.id === id ? updatedReply : r)) }
            : t,
        ),
      );
      const c = CHOICES.find((x) => x.status === status)!;
      onNotice(`Odpowiedź: ${c.label} — ${c.hint}.`);
    } catch {
      onNotice("Nie udało się zapisać statusu odpowiedzi.");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section id="forum" aria-labelledby="forum-h" className={card}>
      <div className="flex flex-col gap-space-sm sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 id="forum-h" className={h2}>
            <Icon name="forum" size={28} />
            Komentarze z forum
          </h2>
          <p className="mt-1 text-body-md text-on-surface-variant">
            Kliknij status — zapisuje się od razu.
          </p>
        </div>
        <ul className="flex flex-wrap gap-space-xs text-caption text-on-surface-variant">
          {CHOICES.map((c) => (
            <li key={c.status} className={`flex items-center gap-1 rounded-lg px-2 py-1 ${c.on}`}>
              <Icon name={c.icon} size={14} />
              <strong>{c.label}</strong>
              <span className="opacity-90">· {c.hint}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-space-md flex flex-wrap gap-space-xs" role="tablist" aria-label="Filtr">
        {FILTERS.map((f) => {
          const n = counts[f.id];
          const selected = filter === f.id;
          return (
            <button
              key={f.id}
              type="button"
              role="tab"
              aria-selected={selected}
              onClick={() => setFilter(f.id)}
              className={`flex min-h-12 items-center gap-2 rounded-lg px-space-md text-label-lg font-semibold hc-edge ${
                selected
                  ? "bg-primary text-on-primary"
                  : "bg-surface-container text-primary hover:bg-surface-container-high"
              }`}
            >
              {f.label}
              <span
                className={`min-w-6 rounded-full px-2 py-0.5 text-center text-caption font-bold ${
                  selected ? "bg-on-primary/20" : "bg-surface-container-highest"
                }`}
              >
                {n}
              </span>
            </button>
          );
        })}
      </div>

      {visible.length === 0 ? (
        <p className="mt-space-md text-body-md text-on-surface-variant">Pusto w tym filtrze.</p>
      ) : (
        <ul className="mt-space-md flex flex-col gap-space-md">
          {visible.map((t) => (
            <li key={t.id}>
              <ThreadCard thread={t} busyId={busyId} onThread={decideThread} onReply={decideReply} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export function pendingThreadCount(threads: AdminThread[]) {
  return threads.filter(needsDecision).length;
}
