"use client";

import { useState } from "react";

// UI ile uyumlu keskin/mono dropdown (native select değil — tarayıcı listesi görünmez).
export function Select({
  value,
  options,
  onChange,
  ariaLabel,
}: {
  value: string;
  options: { value: string; label: string }[];
  onChange: (v: string) => void;
  ariaLabel?: string;
}) {
  const [open, setOpen] = useState(false);
  const current = options.find((o) => o.value === value)?.label ?? value;

  return (
    <div className="relative">
      <button
        type="button"
        aria-label={ariaLabel}
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1.5 border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-600 transition-colors hover:border-neutral-400 dark:text-neutral-300 dark:hover:border-neutral-600"
      >
        <span>{current}</span>
        <svg width="9" height="9" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" className={`transition-transform ${open ? "rotate-180" : ""}`}>
          <path d="M6 9l6 6 6-6" />
        </svg>
      </button>

      {open && (
        <>
          {/* dışarı tıkla → kapat */}
          <button
            type="button"
            aria-hidden
            tabIndex={-1}
            onClick={() => setOpen(false)}
            className="fixed inset-0 z-20 cursor-default"
          />
          <div className="absolute right-0 z-30 mt-1 min-w-full border border-hairline bg-background shadow-lg">
            {options.map((o) => {
              const sel = o.value === value;
              return (
                <button
                  key={o.value}
                  type="button"
                  onClick={() => {
                    onChange(o.value);
                    setOpen(false);
                  }}
                  className={`flex w-full items-center gap-1.5 whitespace-nowrap px-2.5 py-1.5 text-left font-mono text-[11px] transition-colors hover:bg-neutral-500/[0.06] ${
                    sel ? "text-accent" : "text-neutral-600 dark:text-neutral-300"
                  }`}
                >
                  <span className="w-2 text-accent">{sel ? "›" : ""}</span>
                  {o.label}
                </button>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
