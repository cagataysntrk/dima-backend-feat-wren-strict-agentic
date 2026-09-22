"use client";

import { useMemo, useRef, useState } from "react";
import { tokenizeSql } from "@dima/domain";
import { TOKEN_CLASS } from "./SqlBlock";
import { cn } from "../utils";

/**
 * SQL editor: a transparent textarea over a highlighted mirror of the same
 * text. No editor dependency — the mirror is the tokenizer we already use in
 * SqlBlock, so colours match the read-only blocks exactly.
 *
 * The two layers must share every metric that affects wrapping (font, size,
 * leading, padding, width); METRICS below is applied to both, and nothing
 * layout-affecting belongs in `className`.
 */
const METRICS = "px-3 py-2 font-mono text-base leading-relaxed md:text-[13px]";

export function SqlEditor({
  value,
  onChange,
  onCaret,
  className,
  ...props
}: {
  value: string;
  onChange: (next: string) => void;
  /** Caret moved (typing, clicking, arrows) — drives completions. */
  onCaret?: (caret: number) => void;
  className?: string;
  ref?: React.Ref<HTMLTextAreaElement>;
} & Omit<React.ComponentProps<"textarea">, "value" | "onChange" | "className">) {
  const mirror = useRef<HTMLPreElement>(null);
  const [focused, setFocused] = useState(false);
  // A trailing newline has no line box, so the mirror would come up one line
  // short and the last line would scroll out of sync.
  const lines = useMemo(() => `${value}\n`.split("\n").map((l) => tokenizeSql(l)), [value]);

  return (
    <div
      className={cn(
        "surface-inset relative overflow-hidden rounded-xl transition-shadow",
        focused && "ring-2 ring-ring/40",
        className,
      )}
    >
      <pre
        ref={mirror}
        aria-hidden
        className={cn(METRICS, "pointer-events-none min-h-56 overflow-hidden whitespace-pre-wrap break-words")}
      >
        {lines.map((line, i) => (
          <span key={i}>
            {line.map((t, j) => (
              <span key={j} className={TOKEN_CLASS[t.type]}>
                {t.text}
              </span>
            ))}
            {"\n"}
          </span>
        ))}
      </pre>
      <textarea
        {...props}
        value={value}
        spellCheck={false}
        onChange={(e) => {
          onChange(e.target.value);
          onCaret?.(e.target.selectionStart);
        }}
        onKeyUp={(e) => onCaret?.(e.currentTarget.selectionStart)}
        onClick={(e) => onCaret?.(e.currentTarget.selectionStart)}
        onFocus={(e) => {
          setFocused(true);
          props.onFocus?.(e);
        }}
        onBlur={(e) => {
          setFocused(false);
          props.onBlur?.(e);
        }}
        onScroll={(e) => {
          if (mirror.current) mirror.current.scrollTop = e.currentTarget.scrollTop;
        }}
        className={cn(
          METRICS,
          "absolute inset-0 size-full resize-none overflow-auto whitespace-pre-wrap break-words bg-transparent",
          // The mirror underneath carries the colour; only the caret shows here.
          "text-transparent caret-foreground outline-none selection:bg-brand/25 selection:text-transparent",
        )}
      />
    </div>
  );
}
