"use client";

import { useEffect, useRef, useState } from "react";
import { vurguSuz } from "@/lib/vurgu";
import { sonBakilanEtiketler, type Thread } from "@/lib/threads";
import type { CubeQuery } from "@/lib/types";
import { CaretInput } from "@/components/CaretInput";
import { DurdurDugmesi } from "@/components/DurdurDugmesi";
import { OneriSeridi } from "@/components/OneriSeridi";

// SQL provenance — keskin, monospace "sistem readout" rozeti. "vqr" (VQR birebir/yakın
// eşleşme tekrar oynatma) ve "meta"/"catalog" (deterministik, veri sorgusu değil) da
// LLM'siz aile — cube/kpi ile aynı vurguyu taşır ki kullanıcı ne zaman LLM'in atlandığını
// görebilsin (strict-agentic /ask önceden her soruyu LLM'e düşürüyordu, artık düşürmüyor).
// 🔴 FAZ 7.8 · **K2 — MADALYA KALDIRILDI.** Bu bir ÇIKARMA kalemidir.
//
// Burada `confidenceBadge()` vardı: `explain.confidence`'ı 🥇/🥈/🥉'ye ve **yüzdeye**
// çeviriyordu (`Yüksek güven (100%)`). Kaynağı `answer.py::_EXPLAIN_PATH` — ve o
// **sabit kodlu bir YOL ETİKETİDİR**, hesaplanmış değil:
//   cube → 1.0 · vqr → 0.95 · cube+llm → 0.85 · rule → None
//
// Yani kullanıcı **"Yüksek güven (100%)"** okuyordu ve arkasında **hiçbir ölçüm yoktu**;
// söylenen tek şey *"bu cevap route()'tan geldi"*ydi.
//
// 🔴 MIMARI §9'un kendi yasağının üründe **canlı ihlaliydi**:
//    *"kalibre edilmediği sürece o sayı bir güven değil bir SÜSTÜR."*
//
// ⚠ Ve süs zararsız değil: kalibre edilmemiş güven **uygun güveni bozar** — kullanıcı
// %100 gördüğü bir cevabı denetlemez. Bir rozetin en kötü hâli, denetlemeyi
// GEREKSİZ göstermesidir.
//
// Yerine geçen bir şey **yazılmadı**, çünkü zaten vardı: `SourceBadge`'in kendisi
// (◆ CUBE · ◆ VQR · ◈ LLM) **yolu** söylüyor — ve yol, ölçülmüş bir olgudur.
// Kademe bilgisi ise makbuzun katman 1'inde (`Makbuz.tsx`) düz Türkçe duruyor.

/** FAZ 1.5 — SERTİFİKA KADEMESİ. **Yeni bir panel DEĞİL**: var olan güven rozetinin
 * yanında duran bir kademe (yol haritası birebir: *"güven rozetinin kademesi (yeni panel
 * DEĞİL)"*; K5 panel tavanı 13/13, boşluk 0).
 *
 * `confidence` *"bu YOL ne kadar deterministik"* der; sertifika *"bu METRİĞİN TANIMINI
 * kim onayladı"* der. İkisi farklı sorulardır — bir metrik DOĞRU hesaplanıp YANLIŞ
 * tanımlanmış olabilir ve determinizm onu yakalamaz.
 *
 * 🔴 **Çürümüş bir sertifika kademe VERMEZ**, ⚠ döner: çürük bir onayı "sertifikalı" diye
 * göstermek rozeti bir SÜSE çevirirdi (MIMARI'nin kalibre edilmemiş güven sayısına
 * itirazının aynısı). Kademe kararı BACKEND'de (`certification.rozet_kademesi`);
 * burada yalnız GÖSTERİLİR — ikinci bir eşik kümesi yazmak "aynı kuralın iki sahibi" olurdu. */
export function sertifikaRozeti(
  sertifika: { kademe?: string | null; otomatik_iptal_nedeni?: string[] | null } | null | undefined,
): { emoji: string; title: string } | null {
  const kademe = sertifika?.kademe;
  if (!kademe) return null;
  if (kademe === "uyari") {
    const neden = (sertifika?.otomatik_iptal_nedeni ?? []).join(", ");
    return {
      emoji: "⚠",
      title: `Sertifika YENİDEN DOĞRULAMA gerektiriyor${neden ? ` (${neden})` : ""} — `
        + "onay hâlâ kayıtlı ama dayandığı tanım/köken değişmiş.",
    };
  }
  const etiket: Record<string, string> = {
    onerilen: "Önerilen — bir sahip önerdi, henüz onaylanmadı",
    sertifikali: "Sertifikalı — tanımı bir sahip onayladı",
    master_veri: "Master veri — kurumsal referans tanım",
  };
  const simge: Record<string, string> = {
    onerilen: "○", sertifikali: "◉", master_veri: "★",
  };
  return { emoji: simge[kademe] ?? "○", title: etiket[kademe] ?? kademe };
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
  sertifika,
}: {
  source: string | null;
  /** 🔴 FAZ 7.3(k) — `sertifikaRozeti()` **export edilmiş ama HİÇ ÇAĞRILMAMIŞTI**
   *  (zincirin beşinci kopukluğu). Rozet artık yol rozetinin yanında duruyor: yol
   *  *"nereden geldi"*, sertifika *"tanımını kim onayladı"* der.
   *
   *  ⚠ `uyari` kademesi burada **gösterilmez** — onun yeri `SertifikaBandi`dir.
   *  *Bir uyarıyı bir etiketin içine sıkıştırmak, onu bir etikete indirger.* */
  sertifika?: { kademe?: string | null; otomatik_iptal_nedeni?: string[] | null } | null;
}) {
  if (!source) return null;
  const sert = sertifika?.kademe && sertifika.kademe !== "uyari"
    ? sertifikaRozeti(sertifika) : null;
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
      title={title}
      className={`inline-flex h-[20px] items-center gap-1 border px-1.5 font-mono text-[10px] tracking-wide ${cls}`}
    >
      {label}
      {sert && (
        <span className="ml-1 opacity-[var(--opacity-soluk)]" title={sert.title}>
          {sert.emoji}
        </span>
      )}
    </span>
  );
}

export function ChatPanel({
  threads,
  activeThreadId,
  pending,
  pendingQuestion,
  liveTrace,
  aktifJobId,
  compact,
  onSelectThread,
  onSubmit,
  yolSiniri = null,
  mod = null,
  onMod,
  kapsam = null,
  onKapsam,
  superadmin = false,
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
  // FAZ 1.12 · AI Act Md.14 — arka-plana kuyruklanan işin kimliği; yalnız o zaman
  // (uzun Discovery) dolar ve durdurma düğmesi ancak o zaman görünür.
  aktifJobId?: string | null;
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
  // 🔴 FAZ 5.14 — HIZLI ↔ DERİN. ⚠ Seçim SORUYA bağlıdır ve her mesajda sıfırlanır
  // (`page.tsx` `onSettled`). *Yapışkan bir ayar, unutulmuş bir ayardır.*
  mod?: "hizli" | "derin" | null;
  onMod?: (m: "hizli" | "derin" | null) => void;
  // FAZ 2.3 — kapsam merceği. `undefined` onKapsam → anahtar HİÇ çizilmez (bayrak kapalı).
  kapsam?: "departman" | "genel" | "portfoy" | null;
  onKapsam?: (k: "departman" | "genel" | "portfoy") => void;
  // `portfoy` yalnız superadmin'e TEKLİF edilir — sınır backend'de, bu yalnız nezaket.
  superadmin?: boolean;
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
                      <SourceBadge source={reportable.source} sertifika={reportable.explain?.sertifika} />
                    </>
                  ) : last.note ? (
                    // 🔴 `DA-8` — tek satırlık önizlemede biçimleme yapılamaz (kırpma
                    // doğru davranıştır: bu bir thread LİSTESİ, cevabın okunduğu yer değil).
                    // Ama `**` işaretleri burada da görünürdü → sökülür.
                    <span className="truncate text-amber-600">{vurguSuz(last.note)}</span>
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
                {/* FAZ 1.12 · Md.14 — durdurma, BEKLEMENİN yanında durur: kullanıcı
                    beklerken aradığı düğme burasıdır. `aktifJobId` yoksa hiç görünmez. */}
                <span className="ml-auto">
                  <DurdurDugmesi jobId={aktifJobId ?? null} />
                </span>
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
        {/* FAZ 2.3 — KAPSAM MERCEĞİ. `yol` anahtarıyla AYNI desen: yeni bir panel/ekran
            DEĞİL, komposerin üstünde üç seviyeli bir seçim.
            🔴 Bir GÖRÜNÜRLÜK aracıdır, GÜVENLİK SINIRI DEĞİL: `genel`e dönmek hiçbir
            yetki AÇMAZ — sınırı backend (`authorize()` + RLS) koyar. `portfoy` yalnız
            superadmin'e görünür; görünürlük bir sınır değil, YAPAMAYACAĞI bir şeyi
            kullanıcıya teklif etmeme nezaketidir. */}
        {onKapsam && (
          <div className="mb-2 flex items-center gap-1.5">
            <span className="select-none font-mono text-[10px] uppercase tracking-wider text-neutral-400">
              kapsam
            </span>
            {([
              ["genel", "genel", "Bugünkü tam katalog (varsayılan)"],
              ["departman", "departmanım", "Yalnız departmanıma atanmış metrikler — atanmamışlar da görünür"],
              ...(superadmin
                ? [["portfoy", "portföy", "Çok-tenant birleşik görünüm (yalnız superadmin)"] as const]
                : []),
            ] as const).map(([deger, etiket, ipucu]) => (
              <button
                key={etiket}
                type="button"
                onClick={() => onKapsam(deger)}
                title={ipucu}
                className={`border px-1.5 py-0.5 font-mono text-[10px] transition-colors ${
                  (kapsam ?? "genel") === deger
                    ? "border-accent/50 text-accent"
                    : "border-hairline text-neutral-500 hover:text-foreground"
                }`}
              >
                {etiket}
              </button>
            ))}
          </div>
        )}
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
        {/* 🔴 FAZ 5.14 — HIZLI ↔ DERİN. Soru kutusunun yanında **iki konumlu** anahtar.
            `yol_siniri` üç konumlu bir UZMAN ayarıdır; bu ise günlük kullanım için
            **tek soruluk** bir karardır ve her mesajda sıfırlanır. İkisi aynı sunucu
            kapısından geçer — aynı davranışa iki AD, iki uygulama değil. */}
        {onMod && (
          <div className="mb-1.5 inline-flex border border-hairline">
            {([
              ["hizli", "hızlı", "Yalnız kanıtlanmış küp yolu — LLM'e HİÇ gidilmez"],
              ["derin", "derin", "Tam merdiven: küp → LLM seçimi → keşif"],
            ] as const).map(([deger, etiket, ipucu], i) => (
              <button
                key={deger}
                type="button"
                title={ipucu}
                onClick={() => onMod(mod === deger ? null : deger)}
                className={`${i ? "border-l border-hairline " : ""}px-2 py-0.5 font-mono text-[10px] transition-colors ${
                  mod === deger
                    ? "bg-accent/10 text-accent"
                    : "text-neutral-500 hover:text-foreground"
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
                className="select-none font-mono text-sm text-neutral-500 transition-colors hover:text-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
              >
                {uploading ? "⋯" : "📎"}
              </button>
            </>
          )}
          <span className="select-none font-mono text-sm text-accent">›</span>
          <div className="flex-1">
            <CaretInput value={value} onChange={setValue} onSubmit={send} busy={pending} size="inline" />
            {/* 🔴 FAZ 6.3 — yazarken-ara şeridi. Tıklanan aday yalnız METNİ tamamlar;
                sorgu koşmaz, sayı üretmez. */}
            <OneriSeridi
              metin={value}
              onSec={setValue}
              /* `5.9` — son bakılanlar sohbetin KENDİ kartlarından türer: yeni bir
                 depo, yeni bir izin, yeni bir senkron YOK. */
              sonBakilanlar={sonBakilanEtiketler(threads)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
