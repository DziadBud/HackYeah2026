// polish display labels for backend enum values

import type { ChallengeArea, CostLevel, Readiness } from "@/lib/api";

export const AREA_LABEL: Record<ChallengeArea, string> = {
  "Rodzina i piecza zastepcza": "Rodzina i piecza zastępcza",
  Bezdomnosc: "Bezdomność",
  Niepelnosprawnosc: "Niepełnosprawność",
  Ubostwo: "Ubóstwo",
  "Integracja cudzoziemcow": "Integracja cudzoziemców",
  Zdrowie: "Zdrowie",
  "Zdrowie psychiczne": "Zdrowie psychiczne",
  Seniorzy: "Seniorzy",
};

export const READINESS: Record<Readiness, string> = {
  concept: "Koncepcja",
  prototype: "Prototyp",
  pilot: "Pilotaż",
  running: "Wdrożona",
};

export const COST: Record<CostLevel, string> = { low: "niski", medium: "średni", high: "wysoki" };

// /match returns raw tags; only the "area:*" mirrors are meant for people
export function areaLabelsFromTags(tags: string[]): string[] {
  return tags
    .filter((t) => t.startsWith("area:"))
    .map((t) => {
      const area = t.slice("area:".length);
      return area in AREA_LABEL ? AREA_LABEL[area as ChallengeArea] : area;
    });
}
