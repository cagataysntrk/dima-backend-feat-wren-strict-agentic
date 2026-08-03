"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import type { AskResponse, CubeQuery } from "@/lib/types";
import type { Thread } from "@/lib/threads";
import { BrandMark } from "@/components/BrandMark";
import { CaretInput } from "@/components/CaretInput";
import { ReportCard } from "@/components/ReportCard";

// ⚠️ FAZ 0.23 — RAPORLANABİLİRLİK TEK SAHİPTE.
//
// Bu kapı eskiden `it.result || it.kpi` idi ve **İKİ YERDE ayrı ayrı** yazılıydı
// (`lastReportableIdx` hesabı + render dalı). Ama `ask.py`'nin *"cevap üstünde konuş"*
// dalı **`result` DÖNDÜRMEZ**: gövdeyi `contribution` (+ `prescription`) taşır — kodun
// kendi yorumu: *"Bulgular CEVABIN GÖVDESİDİR — `next_steps` DEĞİL … UI'da farklı
// görünmelidir."* Render edici (`ReportCard`) **zaten yazılmış ve doğruydu**
// (`item.cube_query && (item.result || item.contribution)`); **sırası hiç gelmiyordu.**
// Sonuç: Faz D2/G1/G3'te ödenmiş üç özellik (katkı ayrıştırması · reçete · chip'ler)
// ekranda YOKTU; geriye sarı bir not kalıyordu.
//
// Tek fonksiyon: *"aynı kuralın iki sahibi"* bu deponun 1 numaralı kusur sınıfı.
// **Yeni yetenek SIFIR** — çalışan, testli, makbuzlu bir motor görünmezden görünüre geçer.
export function raporlanabilir(it: AskResponse): boolean {
  return Boolean(it.result || it.kpi || it.contribution || it.prescription);
}

// §B Adım 2 (1 Ağustos 2026) — sağ panel artık İNCE bir YIĞIN kapsayıcısı: bir thread'in
// (aynı konudaki tüm cevaplar) item dizisini alır, her raporlanabilir item için bir
// <ReportCard> render eder (eski tek-rapor gövdesi ARTIK ReportCard'ta) — yeni cevap
// ÖNCEKİLERİ SİLMEZ, altına eklenir (kullanıcının "altta biriken akış" tarifi). `fb` (verify
// geri bildirim map'i) burada TEK, PAYLAŞILAN state olarak tutulur (içerik-anahtarlı olduğu
// için yığındaki TÜM kartlarda güvenle paylaşılabilir) — `pending`/`error` artık TÜM render'ı
// DEĞİŞTİRMEZ, yığının ALTINA eklenen bir kuyruk göstergesi/hata kutusu olur.
export function ReportPanel({
  thread,
  pending,
  viewHint,
  onCubeEdit,
  error,
  sessionId,
  contextLabel,
  onClearContext,
  onContinue,
  onReply,
  onReplyMulti,
}: {
  thread: Thread | null;
  pending: boolean;
  // YALNIZ thread'in EN SON raporlanabilir item'ına geçirilir (bkz. aşağıdaki lastReportableIdx).
  viewHint?: { kind: string; nonce: number } | null;
  onCubeEdit?: (edit: { cq: CubeQuery; label: string }) => void;
  error: string | null;
  sessionId?: string;
  // §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — "bağlam: X" göstergesi ARTIK burada: eski sol
  // chat'in bu göstergesi kaldırıldı (kullanıcı: "bağlam olarak da mesela oee eklenebiliyor
  // küp bağlamı olarak vs o da sağda panelde olacak artık") — akış SAĞDA olduğu için bağlam
  // bilgisi de SAĞDA olmalı.
  contextLabel?: string | null;
  onClearContext?: () => void;
  // §B düzeltmesi (1 Ağustos 2026) — bu panelin KENDİ komposer'ı: aktif thread'in GÜNCEL
  // bağlamıyla devam eder (eski TEK komposer'ın bağlamsal davranışı, artık burada).
  onContinue?: (text: string) => void;
  // Bir karta "yanıtla": bağlam O ÇAPA karttan gelir, sonuç thread'in SONUNA eklenir.
  // `hucre` (Faz G2): grafikte işaret edilen koordinat — ReportCard'dan page.tsx'e
  // geçirilir, orada `AskRequest.anchor` olur.
  onReply?: (threadId: string, anchorIndex: number, text: string,
             hucre?: { dimension: string; value: string }) => void;
  // Birden fazla kart seçip birleşik bağlamla sor: çapa = seçilenlerin EN SONuncusu.
  onReplyMulti?: (threadId: string, anchorIndex: number, extraIndices: number[], text: string) => void;
}) {
  // Verify geri bildirimi ("✓ doğru"/"✗ yanlış") İÇERİK-ANAHTARLI (verifyKey = label::sql) —
  // bu yüzden TÜM kartlar (hatta thread'ler) arasında GÜVENLE paylaşılabilir tek bir map.
  const [fb, setFb] = useState<Record<string, "ok" | "bad">>({});
  const scrollRef = useRef<HTMLDivElement>(null);
  // §B düzeltmesi (1 Ağustos 2026) — çoklu-seçim bağlam: hangi kartların seçili olduğu
  // (index'e göre, thread'in KENDİ item dizisindeki konum) + iki alt-komposer'ın metni.
  const [selectionMode, setSelectionMode] = useState(false);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [continueValue, setContinueValue] = useState("");
  const [multiValue, setMultiValue] = useState("");
  // Thread değişince seçim sıfırlanır — React'ın "render sırasında state ayarlama" deseni
  // (bkz. react.dev "Adjusting state when a prop changes"), `useEffect` içinde setState'in
  // gereksiz bir ekstra render turuna yol açmasını ÖNLER (eslint react-hooks kuralı).
  const [selectionResetKey, setSelectionResetKey] = useState(thread?.id);
  if (thread?.id !== selectionResetKey) {
    setSelectionResetKey(thread?.id);
    setSelectionMode(false);
    setSelected(new Set());
  }

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [thread?.id, thread?.items.length, pending]);

  if (error && !thread) {
    return (
      <Center>
        <div className="max-w-sm border border-red-300 bg-red-50 px-4 py-3 font-mono text-[13px] text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
          {error}
        </div>
      </Center>
    );
  }

  if (pending && !thread) {
    return (
      <Center>
        <div className="flex items-center gap-2 font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} />
          yürütülüyor…
        </div>
      </Center>
    );
  }

  if (!thread) {
    return (
      <Center>
        <div className="max-w-xs text-center font-mono text-[13px] text-neutral-400">
          <span className="dima-caret" style={{ height: "0.9em" }} /> soldan sor — rapor burada belirir
        </div>
      </Center>
    );
  }

  // "chip:" ile başlayan sentetik chip-düzenleme etiketleri gerçek bir soru DEĞİLDİR (bkz.
  // vqr.py::store — "chip etiketleri soru değildir") — verify bunlarla değil, GERİYE doğru en
  // yakın GERÇEK soruyla öğrenir. Sayfa-seviyeli tek `verifyLabel` state'i YERİNE her kart
  // KENDİ thread'indeki konumundan bunu türetir (thread değiştirmede/geçmişte gezinmede asla
  // bayatlamaz).
  const nearestRealQuestion = (items: AskResponse[], index: number): string | null => {
    for (let i = index; i >= 0; i--) {
      if (!items[i].question.startsWith("chip:")) return items[i].question;
    }
    return null;
  };
  let lastReportableIdx = -1;
  // FAZ 0.23 — aynı kapı (aşağıdaki render dalıyla TEK sahip). Eskiden `it.result || it.kpi`
  // burada TEKRAR yazılıydı → `lastReportableIdx`/`viewHint` de aynı körlüğü MİRAS ALIYORDU.
  thread.items.forEach((it, i) => { if (raporlanabilir(it)) lastReportableIdx = i; });

  // §B düzeltmesi (1 Ağustos 2026) — çoklu-seçim: en-son (en büyük index) seçilen kart
  // yapısal ÇAPA olur (kendi cube_query/sql'i normal follow-up gibi kullanılır), geri
  // kalanı `extra_context` olarak (yalnız Discovery grounding'i, backend'de bilinçli
  // kapsam sınırı — bkz. ask.py::_with_extra_context) eklenir.
  const submitReplyMulti = () => {
    const t = multiValue.trim();
    if (!t || !thread || !onReplyMulti || selected.size === 0) return;
    const idxs = Array.from(selected).sort((a, b) => a - b);
    const anchorIndex = idxs[idxs.length - 1];
    const extraIndices = idxs.slice(0, -1);
    onReplyMulti(thread.id, anchorIndex, extraIndices, t);
    setMultiValue("");
    setSelected(new Set());
    setSelectionMode(false);
  };

  return (
    <div className="flex h-full min-h-0 flex-col">
      {/* §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — üst çubuk: SOLDA aktif bağlam göstergesi
          (eski sol chat'ten taşındı), SAĞDA seçim modu toggle'ı + sayaç. Thread değişince
          seçim otomatik sıfırlanır (bkz. yukarıdaki render-sırasında-ayarlama). */}
      <div className="flex shrink-0 items-center gap-2 border-b border-hairline px-4 py-1.5">
        {contextLabel && (
          <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wide text-neutral-400">
            <span className="text-accent">◆</span>
            <span>bağlam: {contextLabel}</span>
            <button
              onClick={onClearContext}
              title="Bu thread'i kapat — panel temizlenir, sonraki soru yeni bir thread başlatır"
              className="border border-hairline px-1 leading-tight transition-colors hover:border-accent/50 hover:text-foreground"
            >
              ×
            </button>
          </span>
        )}
        <button
          onClick={() => { setSelectionMode((m) => !m); setSelected(new Set()); }}
          className={`border px-2 py-0.5 font-mono text-[11px] transition-colors ${
            selectionMode
              ? "border-accent/40 text-accent"
              : "border-hairline text-neutral-400 hover:text-foreground"
          }`}
        >
          {selectionMode ? "✕ seçimi bitir" : "☐ kartları seç"}
        </button>
        {selectionMode && (
          <>
            <span className="font-mono text-[11px] text-neutral-400">{selected.size} seçili</span>
            {selected.size > 0 && (
              <button
                onClick={() => setSelected(new Set())}
                className="font-mono text-[11px] text-neutral-400 underline-offset-2 transition-colors hover:text-foreground hover:underline"
              >
                temizle
              </button>
            )}
          </>
        )}
      </div>
      <div ref={scrollRef} className="min-h-0 flex-1 overflow-auto">
        {thread.items.map((it, i) => {
          if (raporlanabilir(it)) {
            return (
              <ReportCard
                key={`${thread.id}-${i}`}
                item={it}
                index={i}
                threadId={thread.id}
                viewHint={i === lastReportableIdx ? viewHint : null}
                onCubeEdit={onCubeEdit}
                precedingLabel={nearestRealQuestion(thread.items, i)}
                sessionId={sessionId}
                fb={fb}
                setFb={setFb}
                onReply={onReply}
                selectable={selectionMode}
                selected={selected.has(i)}
                onToggleSelect={() =>
                  setSelected((s) => {
                    const n = new Set(s);
                    if (n.has(i)) n.delete(i);
                    else n.add(i);
                    return n;
                  })
                }
              />
            );
          }
          // §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — not-yalnız (result/kpi'siz, ör.
          // netleştirme/upload bildirimi) item'lar ARTIK burada, hafif bir blok olarak
          // render edilir — bu akış eskiden SADECE sol chat'te vardı, kullanıcı: "follow
          // up önerileri artık sağda gelmeli çünkü artık thread sağda akacak". Öneri-chip'i
          // tıklaması bu SPESİFİK item'a anchor'lı bir "yanıtla" (aynı mekanizma, `onReply`).
          if (it.note) {
            return (
              <div key={`${thread.id}-${i}-note`} className="mx-auto max-w-4xl px-8 py-4">
                <h3 className="mb-1.5 font-mono text-[13px] leading-snug text-foreground">
                  {it.question}
                </h3>
                <div className="border-l-2 border-amber-500/50 bg-amber-500/[0.04] py-1.5 pl-3 font-mono text-[12px] leading-snug text-neutral-500">
                  {it.note}
                </div>
                {it.suggestions && it.suggestions.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1.5">
                    {it.suggestions.map((s) => (
                      <button
                        key={s.label}
                        onClick={() => onReply?.(thread.id, i, s.query)}
                        className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-600 transition-colors hover:border-accent/50 hover:text-foreground dark:text-neutral-300"
                      >
                        {s.label}
                      </button>
                    ))}
                  </div>
                )}
                {/* ⚠️ FAZ 0.23 — SAF-NOT dalında `next_steps` YOKTU (ölçüldü:
                    `grep -n "next_steps" ReportPanel.tsx` → 0 isabet). Sonuç:
                    `_intent_uyusmazlik_chipi` (`ask.py`) *"Hangi ölçüyü istiyorsun?"*
                    diye soruyordu ve **altında tıklanacak hiçbir şey yoktu.**
                    Desen `ReportCard.tsx`'in K2 bloğunun AYNISI — `onCubeEdit` →
                    `/cube`, **0 LLM**. `suggestions`'tan AYRI durur: o yeni bir SORU
                    sorar (`onReply`), bu ise mevcut sorguyu DÜZENLER (`cube_query` taşır). */}
                {onCubeEdit && (it.next_steps?.length ?? 0) > 0 && (
                  <div className="mt-3">
                    <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                      sonraki adım
                    </div>
                    <div className="flex flex-wrap gap-1.5">
                      {it.next_steps!.map((step, si) => (
                        <button
                          key={`${step.kind}-${si}`}
                          onClick={() => onCubeEdit({ cq: step.cube_query, label: step.label })}
                          title="Deterministik koşar — LLM yok"
                          className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-500 transition-colors hover:border-foreground/30 hover:text-foreground"
                        >
                          <span className="mr-1 text-neutral-400">
                            {step.kind === "dimension" ? "⌗" : step.kind === "time" ? "◷" : "∑"}
                          </span>
                          {step.label}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          }
          return null;
        })}
        {pending && (
          <div className="mx-auto flex max-w-4xl items-center gap-2 px-8 py-4 font-mono text-[13px] text-neutral-400">
            <span className="dima-caret" style={{ height: "0.9em" }} />
            yürütülüyor…
          </div>
        )}
        {error && (
          <div className="mx-auto max-w-4xl px-8 py-4">
            <div className="max-w-sm border border-red-300 bg-red-50 px-4 py-3 font-mono text-[13px] text-red-700 dark:border-red-900 dark:bg-red-950/30 dark:text-red-400">
              {error}
            </div>
          </div>
        )}
      </div>
      {/* §B düzeltmesi (1 Ağustos 2026) — alt komposer(lar): seçim modunda ve ≥1 kart
          seçiliyken "birleşik bağlam" çubuğu; aksi halde normal "devam et" çubuğu — ikisi
          karşılıklı dışlayıcı. Bu, eski TEK global komposer'ın bağlamsal davranışının
          taşındığı YER (bkz. ChatPanel'in kendi komposer'ının artık HER ZAMAN yeni thread
          açması). */}
      {selectionMode && selected.size > 0 && onReplyMulti ? (
        <div className="shrink-0 border-t border-hairline bg-accent/[0.03] px-4 py-3">
          <div className="mb-1.5 font-mono text-[10px] uppercase tracking-wider text-neutral-400">
            {selected.size} kart birleştirilerek soruluyor
          </div>
          <div className="flex items-center gap-2">
            <span className="select-none font-mono text-sm text-accent">›</span>
            <div className="flex-1">
              <CaretInput
                value={multiValue}
                onChange={setMultiValue}
                onSubmit={submitReplyMulti}
                busy={pending}
                size="inline"
              />
            </div>
          </div>
        </div>
      ) : (
        onContinue && (
          <div className="shrink-0 border-t border-hairline px-4 py-3">
            <div className="flex items-center gap-2">
              <span className="select-none font-mono text-sm text-accent">›</span>
              <div className="flex-1">
                <CaretInput
                  value={continueValue}
                  onChange={setContinueValue}
                  onSubmit={() => {
                    const t = continueValue.trim();
                    if (!t) return;
                    onContinue(t);
                    setContinueValue("");
                  }}
                  busy={pending}
                  size="inline"
                />
              </div>
            </div>
          </div>
        )
      )}
    </div>
  );
}

// Boş/bekleme durumlarında landing ile aynı imza: alt-orta ink filigran.
function Center({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative flex h-full items-center justify-center p-6">
      {children}
      <Link
        href="/brand"
        className="absolute inset-x-0 bottom-8 flex justify-center opacity-30 transition-opacity hover:opacity-80"
      >
        <BrandMark size="sm" ink />
      </Link>
    </div>
  );
}
