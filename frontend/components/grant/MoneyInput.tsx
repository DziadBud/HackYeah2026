"use client";

import { useState } from "react";

type Props = {
  id: string;
  value: number | null;
  onChange: (value: number | null) => void;
  className: string;
  invalid?: boolean;
  describedBy?: string;
};

export function fmtZl(value: number) {
  return `${value.toLocaleString("pl-PL")} zł`;
}

// text + numeric keypad instead of type=number: no wheel changes while scrolling, no "e"/"-",
// and spaces typed as thousand separators are simply dropped
export function MoneyInput({ id, value, onChange, className, invalid, describedBy }: Props) {
  // raw digits while focused, so formatting never moves the caret mid-typing
  const [editing, setEditing] = useState<string | null>(null);
  const shown = editing ?? (value == null ? "" : value.toLocaleString("pl-PL"));

  return (
    <div className="relative">
      <input
        id={id}
        type="text"
        inputMode="numeric"
        autoComplete="off"
        className={`${className} pr-12`}
        value={shown}
        aria-invalid={invalid || undefined}
        aria-describedby={describedBy}
        onFocus={() => setEditing(value == null ? "" : String(value))}
        onBlur={() => setEditing(null)}
        onChange={(e) => {
          const digits = e.target.value.replace(/\D/g, "").replace(/^0+(?=\d)/, "").slice(0, 10);
          setEditing(digits);
          onChange(digits ? Number(digits) : null);
        }}
      />
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-y-0 right-space-sm flex items-center text-body-md text-on-surface-variant"
      >
        zł
      </span>
    </div>
  );
}
