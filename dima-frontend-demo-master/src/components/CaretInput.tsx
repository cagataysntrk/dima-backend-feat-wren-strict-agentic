"use client";

import { useRef, useState } from "react";

// Terminal komut satırı: monospace metin + yanıp sönen amber imleç + altında ince
// tarama/kurulma çizgisi. Görünmez textarea tuşları yakalar; imleç her zaman görünür.
// Uzun metin YATAY TAŞMAZ — alta sarar (wrap); belli bir satır sayısından sonra da
// yükseklik SINIRLI kalır ve içeride kaydırılır (cap + scroll). Görünür ayna ile gizli
// textarea grid'de üst üste durur → aynı sarma/hiza → seçim (Cmd+A) ve imleç hizalı.
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
  const scrollRef = useRef<HTMLDivElement>(null);
  const [focused, setFocused] = useState(false);
  const hero = size === "hero";

  const textCls = hero
    ? "font-mono tracking-tight text-[clamp(1.4rem,3.6vw,2rem)] leading-[1.5]"
    : "font-mono tracking-tight text-sm leading-[1.6]";
  const align = hero ? "text-center" : "text-left";
  const wrap = "whitespace-pre-wrap [overflow-wrap:anywhere]";
  // Üst sınır: hero ~4 satır, inline ~6 satır; sonrası içeride kaydırılır.
  const cap = hero ? "max-h-[6.5em]" : "max-h-[9.5em]";

  const keepCaretInView = () => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight; // imleç sonda → en alta kaydır
  };

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
      {/* kaydırılabilir alan: ayna + textarea aynı grid hücresinde üst üste (birlikte kayar) */}
      <div ref={scrollRef} className={`grid ${cap} overflow-y-auto`}>
        <div className={`col-start-1 row-start-1 ${textCls} ${align} ${wrap} text-foreground`}>
          {value}
          <span
            className="dima-caret ml-[2px]"
            style={{ height: "1.05em", verticalAlign: "-0.15em" }}
            aria-hidden
          />
        </div>
        <textarea
          ref={ref}
          value={value}
          rows={1}
          autoFocus={autoFocus}
          onChange={(e) => {
            onChange(e.target.value);
            keepCaretInView();
          }}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              onSubmit();
            }
          }}
          className={`col-start-1 row-start-1 h-full w-full resize-none overflow-hidden border-0 bg-transparent p-0 text-transparent caret-transparent outline-none ${textCls} ${align} ${wrap}`}
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
