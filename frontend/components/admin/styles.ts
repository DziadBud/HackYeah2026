// class strings shared by the admin screens

export const card = "rounded-xl bg-surface-container-lowest p-space-md shadow-sm hc-edge lg:p-space-lg";
export const h2 = "flex items-center gap-2 text-headline-md font-semibold text-primary";
export const primaryBtn =
  "flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-primary px-space-md text-label-lg font-semibold text-on-primary hover:bg-primary-container disabled:opacity-70";
export const ghostBtn =
  "flex min-h-12 items-center justify-center gap-space-xs rounded-lg bg-surface-container-high px-space-md text-label-lg font-semibold text-primary hover:bg-surface-container-highest hc-edge";
export const th = "border-b-2 border-outline px-3 py-2 text-left text-label-md font-semibold text-primary";
export const td = "border-b border-surface-container-highest px-3 py-2 align-top text-body-md";
export const field =
  "min-h-12 rounded-lg border-[1.5px] border-outline bg-surface-container-lowest px-space-sm text-body-md text-on-surface";

export function fmtDate(iso: string) {
  return new Date(iso).toLocaleString("pl-PL", { dateStyle: "medium", timeStyle: "short" });
}
