"use client";

import { useEffect, useState } from "react";
import { ApiError, adminApi, type AdminMe } from "@/lib/api";
import { Icon } from "@/components/Icon";
import { AdminNav } from "@/components/admin/AdminNav";
import { card, field, ghostBtn, primaryBtn } from "@/components/admin/styles";

// principal the backend returns when ADMIN_AUTH_DISABLED=true (backend/app/auth.py DEMO_ADMIN)
const DEMO_ADMIN_ID = "demo-admin";

type Session = { kind: "checking" } | { kind: "in"; me: AdminMe } | { kind: "out" } | { kind: "offline" };

// GET /admin/auth/me decides: 200 shows the panel, 401 the login form. if the api is down the
// panel still renders and each screen falls back to its offline mock (useApiOrMock)
export function AdminGate({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session>({ kind: "checking" });
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let live = true;
    adminApi
      .me()
      .then((me) => live && setSession({ kind: "in", me }))
      .catch((err: unknown) => {
        if (!live) return;
        setSession(err instanceof ApiError && err.status === 401 ? { kind: "out" } : { kind: "offline" });
      });
    return () => {
      live = false;
    };
  }, []);

  async function login(username: string, password: string) {
    setBusy(true);
    setStatus("");
    try {
      await adminApi.login({ username, password });
      setSession({ kind: "in", me: await adminApi.me() });
    } catch (err) {
      setStatus(
        err instanceof ApiError && err.status === 401
          ? "Nieprawidłowy login lub hasło."
          : err instanceof ApiError && err.status === 429
            ? "Zbyt wiele nieudanych prób. Spróbuj ponownie za 15 minut."
            : "Nie udało się połączyć z serwerem. Spróbuj ponownie.",
      );
    } finally {
      setBusy(false);
    }
  }

  async function logout() {
    try {
      await adminApi.logout();
      setSession({ kind: "out" });
      setStatus("Wylogowano.");
    } catch {
      setStatus("Nie udało się wylogować. Spróbuj ponownie.");
    }
  }

  const showPanel = session.kind === "in" || session.kind === "offline";

  return (
    <>
      <header className="flex flex-col gap-space-sm rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge lg:p-space-lg">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="flex flex-wrap items-center gap-2">
            <span className="rounded bg-secondary-fixed px-2 py-0.5 text-caption font-bold text-on-secondary-fixed">tylko dla ROPS</span>
            <span className="text-caption text-on-surface-variant">
              {session.kind === "checking" && "Sprawdzam logowanie…"}
              {session.kind === "in" &&
                (session.me.id === DEMO_ADMIN_ID ? "Logowanie wyłączone na czas demonstracji" : `Zalogowano jako ${session.me.username}`)}
              {session.kind === "out" && "Zaloguj się, aby zobaczyć panel"}
              {session.kind === "offline" && "Brak połączenia z serwerem"}
            </span>
          </p>
          {session.kind === "in" && session.me.id !== DEMO_ADMIN_ID && (
            <button type="button" onClick={logout} className={ghostBtn}>
              <Icon name="logout" />
              Wyloguj
            </button>
          )}
        </div>
        <h1 className="text-headline-lg-mobile font-bold tracking-tight text-primary sm:text-headline-lg">Panel administratora</h1>
        {showPanel && <AdminNav />}
        {session.kind !== "out" && status && (
          <p role="status" className="text-body-md font-semibold text-primary">
            {status}
          </p>
        )}
      </header>

      {showPanel && children}

      {session.kind === "out" && (
        <section aria-labelledby="login-h" className={`${card} flex max-w-xl flex-col gap-space-sm`}>
          <h2 id="login-h" className="flex items-center gap-2 text-headline-md font-semibold text-primary">
            <Icon name="login" size={28} />
            Logowanie
          </h2>
          <form
            className="flex flex-col gap-space-sm"
            onSubmit={(e) => {
              e.preventDefault();
              const f = new FormData(e.currentTarget);
              void login(String(f.get("username")), String(f.get("password")));
            }}
          >
            <div className="flex flex-col gap-1">
              <label htmlFor="admin-username" className="text-label-lg font-semibold text-primary">
                Login
              </label>
              <input id="admin-username" name="username" required maxLength={100} autoComplete="username" className={field} />
            </div>
            <div className="flex flex-col gap-1">
              <label htmlFor="admin-password" className="text-label-lg font-semibold text-primary">
                Hasło
              </label>
              <input id="admin-password" name="password" type="password" required maxLength={1024} autoComplete="current-password" className={field} />
            </div>
            <button type="submit" disabled={busy} className={`${primaryBtn} self-start`}>
              <Icon name="login" />
              {busy ? "Loguję…" : "Zaloguj się"}
            </button>
          </form>
          <p role="status" className="min-h-6 text-body-md font-semibold text-primary">
            {status}
          </p>
        </section>
      )}
    </>
  );
}
