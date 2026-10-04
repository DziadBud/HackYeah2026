// format rules for Zał. 3 §2 fields; the backend stores drafts as typed, so checks live here

export type FieldKind = "text" | "email" | "phone" | "postal" | "nip" | "regon" | "krs";

type InputAttrs = {
  type: "text" | "email" | "tel";
  inputMode?: "text" | "email" | "tel" | "numeric";
  autoComplete?: string;
  maxLength: number;
  placeholder?: string;
};

const ATTRS: Record<FieldKind, InputAttrs> = {
  text: { type: "text", maxLength: 200 },
  email: { type: "email", inputMode: "email", autoComplete: "email", maxLength: 254 },
  phone: { type: "tel", inputMode: "tel", autoComplete: "tel", maxLength: 20, placeholder: "np. 600 100 200" },
  postal: { type: "text", inputMode: "numeric", autoComplete: "postal-code", maxLength: 6, placeholder: "00-000" },
  nip: { type: "text", inputMode: "numeric", maxLength: 10, placeholder: "10 cyfr" },
  regon: { type: "text", inputMode: "numeric", maxLength: 14, placeholder: "9 lub 14 cyfr" },
  krs: { type: "text", inputMode: "numeric", maxLength: 10, placeholder: "10 cyfr" },
};

const AUTOCOMPLETE: Record<string, string> = {
  first_name: "given-name",
  last_name: "family-name",
  full_name: "name",
  representative_full_name: "name",
  name: "organization",
  address: "street-address",
  city: "address-level2",
};

export function fieldKind(key: string): FieldKind {
  if (key.endsWith("email")) return "email";
  if (key.endsWith("phone")) return "phone";
  if (key === "postal_code") return "postal";
  if (key === "nip" || key === "regon" || key === "krs") return key;
  return "text";
}

export function inputAttrs(key: string): InputAttrs {
  const kind = fieldKind(key);
  const attrs = ATTRS[kind];
  return kind === "text" && AUTOCOMPLETE[key] ? { ...attrs, autoComplete: AUTOCOMPLETE[key] } : attrs;
}

const digits = (v: string) => v.replace(/\D/g, "");

// drops what can't belong to the field while typing, so the user sees the restriction at once
export function sanitize(kind: FieldKind, value: string): string {
  switch (kind) {
    case "phone":
      return value.replace(/[^\d+\s()-]/g, "");
    case "postal": {
      const d = digits(value).slice(0, 5);
      return d.length > 2 ? `${d.slice(0, 2)}-${d.slice(2)}` : d;
    }
    case "nip":
    case "krs":
      return digits(value).slice(0, 10);
    case "regon":
      return digits(value).slice(0, 14);
    default:
      return value;
  }
}

function checksum(d: string, weights: number[]) {
  const sum = weights.reduce((acc, w, i) => acc + w * Number(d[i]), 0);
  return (sum % 11) % 10;
}

function isNip(d: string) {
  if (d.length !== 10) return false;
  const sum = [6, 5, 7, 2, 3, 4, 5, 6, 7].reduce((acc, w, i) => acc + w * Number(d[i]), 0);
  // a remainder of 10 means no valid control digit exists
  return sum % 11 !== 10 && sum % 11 === Number(d[9]);
}

function isRegon(d: string) {
  if (d.length === 9) return checksum(d, [8, 9, 2, 3, 4, 5, 6, 7]) === Number(d[8]);
  if (d.length === 14) return checksum(d, [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]) === Number(d[13]);
  return false;
}

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

/** polish message for a filled field with a bad format, "" when it is fine */
export function formatError(kind: FieldKind, raw: string): string {
  const v = raw.trim();
  if (!v) return "";
  switch (kind) {
    case "email":
      return EMAIL_RE.test(v) ? "" : "Wpisz poprawny adres e-mail, np. jan@przyklad.pl.";
    case "phone": {
      const d = digits(v);
      return d.length === 9 || (d.length === 11 && d.startsWith("48"))
        ? ""
        : "Wpisz 9-cyfrowy numer telefonu, np. 600 100 200 lub +48 600 100 200.";
    }
    case "postal":
      return /^\d{2}-\d{3}$/.test(v) ? "" : "Wpisz kod pocztowy w formacie 00-000.";
    case "nip":
      return isNip(digits(v)) ? "" : "NIP ma 10 cyfr. Sprawdź, czy nie ma literówki.";
    case "regon":
      return isRegon(digits(v)) ? "" : "REGON ma 9 lub 14 cyfr. Sprawdź, czy nie ma literówki.";
    case "krs":
      return /^\d{10}$/.test(v) ? "" : "KRS ma 10 cyfr, np. 0000123456.";
    default:
      return "";
  }
}
