"use client";

import { useEffect, useState } from "react";
import { ApiError } from "@/lib/api";

export type Source = "loading" | "api" | "mock";

// loads from match-api; if it is down or wants a login, falls back to the offline mock and says why
export function useApiOrMock<T>(load: () => Promise<T>, mock: () => T) {
  const [data, setData] = useState<T | null>(null);
  const [source, setSource] = useState<Source>("loading");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    let live = true;
    load()
      .then((d) => {
        if (!live) return;
        setData(d);
        setSource("api");
      })
      .catch((err: unknown) => {
        if (!live) return;
        setData(mock());
        setSource("mock");
        setNotice(
          err instanceof ApiError && err.status === 401
            ? "Sesja wygasła: odśwież stronę i zaloguj się ponownie. Pokazuję lokalne dane testowe."
            : "Nie udało się połączyć z API. Pokazuję lokalne dane testowe.",
        );
      });
    return () => {
      live = false;
    };
    // load and mock are recreated each render; fetch once per mount
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { data, setData, source, notice, setNotice };
}
