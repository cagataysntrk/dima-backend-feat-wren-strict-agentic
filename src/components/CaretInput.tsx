"use client";

import { useRef, useState } from "react";

// Terminal komut satırı: monospace metin + yanıp sönen amber imleç + altında ince
// tarama/kurulma çizgisi. Görünmez textarea tuşları yakalar; imleç her zaman görünür.
// Uzun metin YATAY TAŞMAZ — alta sarar (wrap). Seçim (Cmd+A) görünür metinle hizalı olsun
// diye görünür ayna ile gizli textarea aynı tipografi/hiza/sarmayı kullanır.
export function CaretInput({
  value,
  onChange,
  onSubmit,
  autoFocus,
  busy = false,
  size = "hero",
}: {
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  autoFocus?: boolean;
  busy?: boolean;
  size?: "hero" | "inline";
}) {
  const ref = useRef<HTMLTextAreaElement>(null);
  const [focused, setFocused] = useState(false);
  const hero = size === "hero";

  const textCls = hero
    ? "font-mono tracking-tight text-[clamp(1.4rem,3.6vw,2rem)] leading-[1.5]"
    : "font-mono tracking-tight text-sm leading-[1.6]";
  const align = hero ? "text-center" : "text-left";
  const wrap = "whitespace-pre-wrap [overflow-wrap:anywhere]";

  return (
    <div
      className={`relative cursor-text ${hero ? "w-[min(600px,84vw)]" : "w-full"}`}
      onMouseDown={(e) => {
        if (e.target !== ref.current) {
          e.preventDefault();
          ref.current?.focus();
        }
      }}
    >
      <div className="relative">
        {/* görünür ayna — uzun metin alta sarar; imleç metnin sonunda */}
        <div className={`${textCls} ${align} ${wrap} text-foreground`}>
          {value}
          <span
            className="dima-caret ml-[2px]"
            style={{ height: "1.05em", verticalAlign: "-0.15em" }}
            aria-hidden
          />
        </div>
        {/* görünmez katman: metin şeffaf (seçim görünür), native imleç gizli, AYNI sarma */}
        <textarea
          ref={ref}
          value={value}
          rows={1}
          autoFocus={autoFocus}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSubmit();
            }
          }}
          className={`absolute inset-0 h-full w-full resize-none overflow-hidden border-0 bg-transparent p-0 text-transparent caret-transparent outline-none ${textCls} ${align} ${wrap}`}
          spellCheck={false}
          autoComplete="off"
        />
      </div>

      {/* input alanı çizgisi: odakta amber'a kurulur, işlemde tarar */}
      <div
        className={`relative mt-3 h-px w-full overflow-hidden bg-hairline ${
          busy ? "dima-scanline" : focused ? "dima-line-armed" : ""
        }`}
      />
    </div>
  );
}
