"use client";

import { useEffect, useRef, useState } from "react";
import type { AskResponse } from "@/lib/types";
import { CaretInput } from "@/components/CaretInput";

// SQL provenance — keskin, monospace "sistem readout" rozeti. "vqr" (VQR birebir/yakın
// eşleşme tekrar oynatma) ve "meta"/"catalog" (deterministik, veri sorgusu değil) da
// LLM'siz aile — cube/kpi ile aynı vurguyu taşır ki kullanıcı ne zaman LLM'in atlandığını
// görebilsin (strict-agentic /ask önceden her soruyu LLM'e düşürüyordu, artık düşürmüyor).
export function SourceBadge({ source }: { source: string | null }) {
  if (!source) return null;
  let label: string, cls: string, title: string;
  if (source === "cube") {
    label = "◆ CUBE";
    cls = "text-accent border-accent/40";
    title = "Deterministik cube motoru — LLM kullanılmadı";
  } else if (source === "kpi") {
    label = "◆ KPI";
    cls = "text-accent border-accent/40";
    title = "Deterministik KPI kartı — LLM kullanılmadı";
  } else if (source === "cube+llm") {
    label = "◆ CUBE·LLM";
    cls = "text-accent border-accent/40";
    title = "SQL bu yolla üretildi (deterministik-önce)";
  } else if (source === "vqr") {
    label = "◆ VQR";
    cls = "text-accent border-accent/40";
    title = "Daha önce doğrulanmış/onaylanmış SQL tekrar oynatıldı — LLM'e gidilmedi";
  } else if (source === "meta") {
    label = "· META";
    cls = "text-neutral-400 border-hairline";
    title = "Veri sorgusu değil — deterministik yanıt (LLM kullanılmadı)";
  } else if (source === "catalog") {
    label = "☰ KATALOG";
    cls = "text-neutral-400 border-hairline";
    title = "Katalog keşfi — deterministik yanıt (LLM kullanılmadı)";
  } else if (source.startsWith("llm:")) {
    label = `▚ LLM·${source.slice(4)}`;
    cls = "text-neutral-500 border-hairline";
    title = "SQL bu yolla üretildi (deterministik-önce)";
  } else {
    label = "⚙ KURAL";
    cls = "text-neutral-400 border-hairline";
    title = "SQL bu yolla üretildi (deterministik-önce)";
  }
  return (
    <span
      title={title}
      className={`inline-flex h-[20px] items-center border px-1.5 font-mono text-[10px] tracking-wide ${cls}`}
    >
      {label}
    </span>
  );
}

export function ChatPanel({
  items,
  active,
  pending,
  pendingQuestion,
  contextLabel,
  onClearContext,
  onSelect,
  onSubmit,
  onUpload,
  uploading,
}: {
  items: AskResponse[];
  active: AskResponse | null;
  pending: boolean;
  pendingQuestion?: string;
  // Aktif konuşma bağlamı (takip mesajları bu raporu düzenler) — görünür + sıfırlanabilir,
  // böylece kasıtlı konu değişimi tahmine kalmaz (ADR-0007).
  contextLabel?: string | null;
  onClearContext?: () => void;
  onSelect: (item: AskResponse) => void;
  onSubmit: (q: string) => void;
  // Chat-scoped Excel/CSV yükleme (base modu) — bu sohbete özel veri kaynağı.
  onUpload?: (file: File) => void;
  uploading?: boolean;
}) {
  const [value, setValue] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const threadRef = useRef<HTMLDivElement>(null);
  const thread = [...items].reverse(); // eski üstte, yeni altta

  useEffect(() => {
    threadRef.current?.scrollTo({ top: threadRef.current.scrollHeight, behavior: "smooth" });
  }, [items.length, pending]);

  const send = () => {
    const t = value.trim();
    if (!t) return;
    onSubmit(t);
    setValue("");
  };

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div ref={threadRef} className="flex-1 overflow-auto px-4 py-5">
        <div className="space-y-5">
          {thread.map((item, i) => {
            const isActive = active === item;
            return (
              <div key={`${item.question}-${i}`} className="space-y-1.5">
                {/* kullanıcı komutu */}
                <div className="flex items-start gap-2">
                  <span className="mt-0.5 select-none font-mono text-xs text-accent">›</span>
                  <span className="font-mono text-[13px] leading-snug text-foreground">
                    {item.question}
                  </span>
                </div>
                {/* not bandı VE tıklanır sonuç satırı ARTIK BİRBİRİNİ DIŞLAMAZ (Faz 1.5):
                    konu-değişimi cevapları hem `note` ("Konu değişti: X → Y") hem gerçek
                    `result` taşıyabilir — KPI'nın NOT taşısa da bir RAPOR olması (canlı
                    2026-07-25) ile AYNI desen, şimdi source="cube" için de geçerli. İkisi
                    de varsa İKİSİ DE render edilir (not üstte, tıklanır satır altta). */}
                {item.note && !item.kpi && (
                  <div className="border-l-2 border-amber-500/50 py-1 pl-3">
                    <div className="font-mono text-[12px] leading-snug text-neutral-500">
                      {item.note}
                    </div>
                    {item.suggestions && item.suggestions.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1.5">
                        {item.suggestions.map((s) => (
                          <button
                            key={s.label}
                            onClick={() => onSubmit(s.query)}
                            className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-600 transition-colors hover:border-accent/50 hover:text-foreground dark:text-neutral-300"
                          >
                            {s.label}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                {(!item.note || item.kpi || item.result) && (
                  /* sistem çıktısı satırı — tıklanınca o rapora döner. Salt-netleştirme
                     (note var, result/kpi yok) TEK istisna — o durumda gösterilecek rapor yok. */
                  <button
                    onClick={() => onSelect(item)}
                    className={`flex w-full items-center gap-2 border-l-2 py-1 pl-3 text-left transition-colors ${
                      isActive
                        ? "border-accent bg-accent/[0.06]"
                        : "border-hairline hover:bg-neutral-500/[0.04]"
                    }`}
                  >
                    <span className="font-mono text-[11px] text-neutral-500">
                      {item.result ? `${item.result.row_count} satır` : item.kpi ? "KPI kartı" : "sql"}
                    </span>
                    <span className="ml-auto">
                      <SourceBadge source={item.source} />
                    </span>
                  </button>
                )}
              </div>
            );
          })}

          {pendingQuestion && (
            <div className="space-y-1.5">
              <div className="flex items-start gap-2">
                <span className="mt-0.5 select-none font-mono text-xs text-accent">›</span>
                <span className="font-mono text-[13px] leading-snug text-foreground">
                  {pendingQuestion}
                </span>
              </div>
              <div className="flex items-center gap-2 border-l-2 border-hairline py-1 pl-3 font-mono text-[11px] text-neutral-400">
                <span className="dima-caret" style={{ height: "0.9em" }} />
                yürütülüyor…
              </div>
            </div>
          )}
        </div>
      </div>

      {/* alt komut satırı */}
      <div className="shrink-0 border-t border-hairline px-4 py-3">
        {contextLabel && (
          <div className="mb-2 flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wide text-neutral-400">
            <span className="text-accent">◆</span>
            <span>bağlam: {contextLabel}</span>
            <button
              onClick={onClearContext}
              title="Bağlamı sıfırla — sonraki soru yeni konu olarak işlenir"
              className="border border-hairline px-1 leading-tight transition-colors hover:border-accent/50 hover:text-foreground"
            >
              ×
            </button>
          </div>
        )}
        <div className="flex items-center gap-2">
          {onUpload && (
            <>
              <input
                ref={fileRef}
                type="file"
                accept=".csv,.xlsx,.xls,.txt,.tsv"
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) onUpload(f);
                  e.target.value = "";
                }}
              />
              <button
                type="button"
                onClick={() => fileRef.current?.click()}
                disabled={uploading}
                title="Excel/CSV yükle — bu sohbete özel veri kaynağı (geçici)"
                className="select-none font-mono text-sm text-neutral-500 transition-colors hover:text-accent disabled:opacity-50"
              >
                {uploading ? "⋯" : "📎"}
              </button>
            </>
          )}
          <span className="select-none font-mono text-sm text-accent">›</span>
          <div className="flex-1">
            <CaretInput value={value} onChange={setValue} onSubmit={send} busy={pending} size="inline" />
          </div>
        </div>
      </div>
    </div>
  );
}
