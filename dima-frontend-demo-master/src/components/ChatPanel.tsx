"use client";

import { useEffect, useRef, useState } from "react";
import type { Thread } from "@/lib/threads";
import type { CubeQuery } from "@/lib/types";
import { CaretInput } from "@/components/CaretInput";

// SQL provenance — keskin, monospace "sistem readout" rozeti. "vqr" (VQR birebir/yakın
// eşleşme tekrar oynatma) ve "meta"/"catalog" (deterministik, veri sorgusu değil) da
// LLM'siz aile — cube/kpi ile aynı vurguyu taşır ki kullanıcı ne zaman LLM'in atlandığını
// görebilsin (strict-agentic /ask önceden her soruyu LLM'e düşürüyordu, artık düşürmüyor).
// Faz 4.13b (1 Ağustos 2026) — dış yol haritası 2.17 "güven rozeti": `explain.confidence`
// (Faz 3'ten beri backend'de var) görsel bir 🥇/🥈/🥉'e çevrilir. `confidence` prop'u
// VERİLMEZSE (eski çağrı yerleri/explain henüz yoksa) rozet HİÇ gösterilmez — yalnız
// SourceBadge'in metin etiketi (mevcut davranış) görünür, hiçbir şey KIRILMAZ.
function confidenceBadge(
  confidence: number | null | undefined,
): { emoji: string; title: string } | null {
  if (confidence === undefined) return null;
  if (confidence === null) {
    return { emoji: "🥉", title: "Güven ölçülemedi (LLM/kural yolu — deterministik değil)" };
  }
  const pct = Math.round(confidence * 100);
  if (confidence >= 0.9) return { emoji: "🥇", title: `Yüksek güven (${pct}%)` };
  if (confidence >= 0.7) return { emoji: "🥈", title: `Orta güven (${pct}%)` };
  return { emoji: "🥉", title: `Düşük güven (${pct}%) — bir varsayım yapılmış olabilir` };
}

/** FAZ 1 (K1) — AD-HOC (geçici) model rozeti.
 *
 * Discovery cevabı artık `cube_query` taşıyor (chip/kırılım/drill açılıyor) ama o yapı
 * ham LLM SQL'inden TÜRETİLMİŞTİR ve DONDURULMUŞ bir görünüm üzerinde çalışır. Rozet
 * bunu söylemek zorunda: `source` hâlâ `llm:*` ve güven hâlâ ölçülemez — **yapı ≠ güven**
 * (MIMARI §5). Kullanıcı "◆ CUBE" gördüğü an bunu deterministik sanardı; görmüyor.
 *
 * `kirpilmis` ayrı ve daha sert bir uyarıdır: sonuç satır tavanına DEĞDİ, yani üzerindeki
 * her toplama eksik veriden hesaplanır. Backend o durumda chip/drill'i zaten kapatıyor;
 * rozet kullanıcıya SEBEBİNİ söyler.
 */
export function AdhocBadge({ cubeQuery }: { cubeQuery: CubeQuery | null }) {
  const cq = (cubeQuery ?? {}) as Record<string, unknown>;
  if (!cq.adhoc) return null;
  const kirpik = Boolean(cq.kirpilmis);
  return (
    <span
      title={
        kirpik
          ? "Geçici model — ham SQL sonucundan türetilmiş dondurulmuş görünüm. " +
            "Sonuç satır tavanına ULAŞTI: toplama/kırılım önerilmiyor, sayılar eksik " +
            "veriden hesaplanırdı."
          : "Geçici model — bu yapı ham SQL sonucundan TÜRETİLDİ ve dondurulmuş bir " +
            "görünüm üzerinde çalışır. Kırılım/filtre yapılabilir, ama SQL'in seçmediği " +
            "bir kolon eklenemez. Güven rozeti bu yüzden yükselmez."
      }
      className={`inline-flex h-[20px] items-center gap-1 border px-1.5 font-mono text-[10px] tracking-wide ${
        kirpik ? "border-amber-500/40 text-amber-600" : "border-hairline text-neutral-500"
      }`}
    >
      ⚡ {kirpik ? "GEÇİCİ·KIRPIK" : "GEÇİCİ MODEL"}
    </span>
  );
}

export function SourceBadge({
  source,
  confidence,
}: {
  source: string | null;
  confidence?: number | null;
}) {
  if (!source) return null;
  const badge = confidenceBadge(confidence);
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
  } else if (source === "statement") {
    label = "▤ GL";
    cls = "text-accent border-accent/40";
    title = "Yapısal finansal tablo (gelir tablosu/bilanço) — deterministik, LLM kullanılmadı";
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
      title={badge ? `${title} · ${badge.title}` : title}
      className={`inline-flex h-[20px] items-center gap-1 border px-1.5 font-mono text-[10px] tracking-wide ${cls}`}
    >
      {badge && <span aria-hidden>{badge.emoji}</span>}
      {label}
    </span>
  );
}

export function ChatPanel({
  threads,
  activeThreadId,
  pending,
  pendingQuestion,
  liveTrace,
  compact,
  onSelectThread,
  onSubmit,
  yolSiniri = null,
  onYolSiniri,
  onUpload,
  uploading,
}: {
  // §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — bu panel ARTIK bir "sohbet akışı" DEĞİL, DÜZ
  // bir PANEL LİSTESİ: her thread TEK, BAĞIMSIZ bir satır (kullanıcının kendi tarifi: "sol
  // taraf tamamen her yazılan birbirinden bağımsız olacak... eski sol chat sağa geçmiş
  // olacak"). Eski nested/iç-içe gösterim (her thread'in TÜM item'larını alt alta, girintili
  // render eden hâl) TAMAMEN kaldırıldı — o akış artık SAĞ panelde (ReportPanel). Burada
  // yalnız her thread'in KÖK sorusu + kısa bir durum özeti gösterilir; tıklamak o thread'i
  // sağda açar. `threads` ZATEN kronolojik sırada (bkz. lib/threads.ts::groupIntoThreads).
  threads: Thread[];
  activeThreadId: string | null;
  pending: boolean;
  pendingQuestion?: string;
  // Faz 4.12 — Discovery arka-plana kuyruklandığında (ask_async_discovery) biriken canlı
  // adımlar; boş/verilmezse statik "yürütülüyor…" gösterilir (davranış değişmez).
  liveTrace?: string[];
  // §B düzeltmesi (1 Ağustos 2026) — bir thread aktifken TRUE: panel daralır, komposer'ın
  // üstünde "burası her zaman yeni thread açar" ipucu gösterilir (bkz. page.tsx'teki sol
  // <section> genişlik geçişi).
  compact?: boolean;
  // Bir thread satırına tıklamak O THREAD'İ sağda aktive eder (bağlam thread'in KENDİ son
  // item'ından geri yüklenir — "istediği zaman tekrar girebilir" sözünün en doğal okunuşu).
  onSelectThread: (thread: Thread) => void;
  // §B düzeltmesi (1 Ağustos 2026) — KRİTİK: bu komposer HER ZAMAN yeni bir thread açar
  // (aktif thread olsun ya da olmasın) — ASLA bağlamsal/takip yanıtı üretmez, ÖNCEKİYLE
  // HİÇBİR BAĞI OLMAZ. Eski bağlamsal davranışın TAMAMI artık sağ panelin kendi
  // komposer'ına taşındı (bkz. ReportPanel.tsx).
  onSubmit: (q: string) => void;
  // YOL SINIRI (Faz F2) — "yalnız küpün KANITLADIĞI cevapları göster".
  // Sayısal bir güven eşiği DEĞİL: merdivenin kendisine bağlı üç ayrık seviye.
  // Rakiplerin veremeyeceği ayar budur — onların yolu yok, tek kutu var.
  yolSiniri?: "deterministik" | "llm" | null;
  onYolSiniri?: (s: "deterministik" | "llm" | null) => void;
  // Chat-scoped Excel/CSV yükleme (base modu) — bu sohbete özel veri kaynağı.
  onUpload?: (file: File) => void;
  uploading?: boolean;
}) {
  const [value, setValue] = useState("");
  const fileRef = useRef<HTMLInputElement>(null);
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [threads.length, pending]);

  const send = () => {
    const t = value.trim();
    if (!t) return;
    onSubmit(t);
    setValue("");
  };

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div ref={listRef} className="flex-1 overflow-auto px-3 py-4">
        <div className="space-y-1.5">
          {threads.map((t) => {
            const isActiveThread = t.id === activeThreadId;
            const root = t.items[0];
            const last = t.items[t.items.length - 1];
            let reportable: Thread["items"][number] | null = null;
            for (let i = t.items.length - 1; i >= 0; i--) {
              if (t.items[i].result || t.items[i].kpi) { reportable = t.items[i]; break; }
            }
            return (
              <button
                key={t.id}
                onClick={() => onSelectThread(t)}
                className={`flex w-full flex-col items-start gap-1 border-l-2 px-3 py-2 text-left transition-colors ${
                  isActiveThread
                    ? "border-accent bg-accent/[0.04]"
                    : "border-transparent hover:bg-neutral-500/[0.04]"
                }`}
              >
                <span className="line-clamp-2 font-mono text-[13px] leading-snug text-foreground">
                  {root.question}
                </span>
                <span className="flex w-full items-center gap-2 font-mono text-[11px] text-neutral-500">
                  {reportable ? (
                    <>
                      <span>
                        {reportable.result
                          ? `${reportable.result.row_count} satır`
                          : reportable.kpi ? "KPI kartı" : "sql"}
                      </span>
                      <SourceBadge source={reportable.source} confidence={reportable.explain?.confidence} />
                    </>
                  ) : last.note ? (
                    <span className="truncate text-amber-600">{last.note}</span>
                  ) : null}
                  {t.items.length > 1 && (
                    <span className="ml-auto shrink-0 text-neutral-400">{t.items.length} mesaj</span>
                  )}
                </span>
              </button>
            );
          })}

          {pendingQuestion && (
            <div className="space-y-1.5 border-l-2 border-hairline px-3 py-2">
              <span className="block font-mono text-[13px] leading-snug text-foreground">
                {pendingQuestion}
              </span>
              <div className="flex items-center gap-2 font-mono text-[11px] text-neutral-400">
                <span className="dima-caret" style={{ height: "0.9em" }} />
                {liveTrace && liveTrace.length > 0 ? liveTrace[liveTrace.length - 1] : "yürütülüyor…"}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* alt komut satırı — §B düzeltmesi: bu komposer ARTIK bağlam TAŞIMIYOR (bkz. onSubmit
          prop yorumu). "bağlam: X · ×" göstergesi ARTIK burada DEĞİL — sağ panele taşındı
          (bkz. ReportPanel.tsx başlık çubuğu). `compact` iken bunun YERİNE her zaman görünen
          bir İPUCU var: bu komposer'a yazmanın HER ZAMAN yeni bir thread açacağını netleştiriyor. */}
      <div className="shrink-0 border-t border-hairline px-4 py-3">
        {compact && (
          <p className="mb-2 font-mono text-[10px] leading-snug text-neutral-400">
            ⓘ buraya yazmak her zaman <span className="text-accent">yeni bir thread</span>{" "}
            başlatır — devam etmek için sağdaki paneli kullan.
          </p>
        )}
        {/* YOL SINIRI (Faz F2) — soru BAŞINA tercih, o yüzden kompozerde durur.
            Üç seviye MERDİVENİN kendisidir: küp → +LLM seçimi → +keşif. Sayısal bir
            güven eşiği DEĞİL; MIMARI'nin kararı gereği kalibre edilmemiş bir sayı
            "güven değil süstür". Varsayılan (sınırsız) HİÇBİR ŞEYİ değiştirmez. */}
        {onYolSiniri && (
          <div className="mb-2 flex items-center gap-1.5">
            <span className="select-none font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              yol
            </span>
            {([
              [null, "hepsi", "Küp → LLM seçimi → keşif (varsayılan)"],
              ["llm", "küp + llm", "Ham SQL YOK — yalnız katalogdan seçim"],
              ["deterministik", "yalnız küp", "LLM'e HİÇ gidilmez — yalnız kanıtlanmış yol"],
            ] as const).map(([deger, etiket, ipucu]) => (
              <button
                key={etiket}
                type="button"
                onClick={() => onYolSiniri(deger)}
                title={ipucu}
                className={`border px-1.5 py-0.5 font-mono text-[10px] transition-colors ${
                  yolSiniri === deger
                    ? "border-accent/50 text-accent"
                    : "border-hairline text-neutral-500 hover:text-foreground"
                }`}
              >
                {etiket}
              </button>
            ))}
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
