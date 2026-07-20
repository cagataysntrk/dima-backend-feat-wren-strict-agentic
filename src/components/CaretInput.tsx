"use client";

import { useRef, useState } from "react";

// Terminal komut satırı: monospace metin + yanıp sönen amber imleç + altında ince
// tarama/kurulma çizgisi. Görünmez native input tuşları yakalar; imleç her zaman görünür.
// Seçim (Cmd+A) görünür metinle hizalı olsun diye input tipografisi + hizası birebir eşlenir
// ve input yalnız METİN SATIRINI kaplar (alt çizgiyi değil).
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
  const ref = useRef<HTMLInputElement>(null);
  const [focused, setFocused] = useState(false);
  const hero = size === "hero";

  // Görünür span ile gizli input AYNI tipografiyi kullanır → seçim kutusu hizalı çıkar.
  const textCls = hero
    ? "font-mono tracking-tight text-[clamp(1.4rem,3.6vw,2rem)] leading-[1.5]"
    : "font-mono tracking-tight text-sm leading-[1.6]";

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
      {/* metin satırı — input yalnız burayı kaplar (dikey hiza doğru) */}
      <div className="relative">
        <div className={`flex items-center overflow-hidden ${hero ? "justify-center" : "justify-start"} ${textCls}`}>
          <span className="whitespace-pre text-foreground">{value}</span>
          <span className="dima-caret ml-[2px]" style={{ height: "1.05em" }} aria-hidden />
        </div>
        <input
          ref={ref}
          value={value}
          autoFocus={autoFocus}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              onSubmit();
            }
          }}
          // görünmez katman: metin şeffaf (seçim görünür), native imleç gizli
          className={`absolute inset-0 h-full w-full cursor-text bg-transparent text-transparent caret-transparent outline-none ${textCls} ${
            hero ? "text-center" : "text-left"
          }`}
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
