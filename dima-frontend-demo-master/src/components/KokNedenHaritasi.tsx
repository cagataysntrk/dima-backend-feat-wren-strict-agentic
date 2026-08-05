"use client";

/** 🌳 **KÖK-NEDEN HARİTASI** — *sayıda boğulma, ilişkiye tıkla.*
 *
 * ## Bugünkü kusur (kullanıcının kendi ifadesi)
 *
 * > *"Çok karışık, kullanıcılar kolay kolay anlamıyor çözemiyor."*
 *
 * `DrillDownPanel` bir **tablo yığını**: hangi yolun bakmaya değer olduğunu **söylemiyor**.
 * Eksik olan veri değil **önceliktir** — ve bakılmayanın **görünmesidir**.
 *
 * ## 🔴 Neden `…Panel` değil, neden panelde
 *
 * Ad `…Panel` **değil** (K1): bu bir yüzey türü değil, bir **araştırma aracıdır**;
 * `AnalizPaneli`nin içinde yaşar, kendi panelini açmaz. Panel sayısı sabit kalır.
 *
 * Kullanıcı *"cevabın altında açılsın"* dedi; **panelde açılıyor** ve gerekçesi
 * kullanıcının **kendi** şikâyeti:
 *
 * | gerekçe | |
 * |---|---|
 * | *"altına doğru açılıyor, boğuluyor"* | ağaç sohbette açılırsa kartı metrelerce uzatır — şikâyet edilen şeyin ta kendisi |
 * | ağaç **genişlik** ister | sohbet sütunu dar; panel sürüklenerek %55vw'ye açılır |
 * | *"not alırken bakabilmeli"* | panel açıkken sohbet görünür kalır — panelin varlık sebebi |
 * | *"modal olmasın"* | ✅ panel modal değildir (`AnalizPaneli` — `complementary`) |
 *
 * ## Düğüm = bir hipotez; ağırlığı = veriden gelen sinyal
 *
 * Ve o ağırlık kullanıcı **tıklamadan önce** hesaplanmış olarak gelir (`/ask/kok-neden`).
 * 🔴 Puanlama **burada değil backend'de**: insanın tıklayarak verdiği karar ile bir
 * ajanın vereceği karar **aynı karardır**, ve frontend'e gömülü bir mantık **çağrılamaz**.
 *
 * ## 🔴 Silik düğümler bu tasarımın en dürüst parçası
 *
 * *Yalnız bulduğunu gösteren bir ağaç, bakmadığını gizler.*
 * ⚠ **Silik ≠ kapalı.** Hiçbir düğüm devre dışı bırakılmaz, yalnız önceliksizleşir —
 * çünkü bazen **verinin yokluğu bulgunun kendisidir** (*"o vardiyada hiç kayıt yok"*).
 *
 * ## Boğulmama kuralı — yol + BİR kat
 *
 * Ekranda her an yalnız iki şey olur: **kat edilen yol** (daima görünür, geri dönülebilir)
 * ve **açık olan tek kat**. *Bir ağaç, tüm dallarını aynı anda gösterdiğinde ağaç olmaktan
 * çıkar, yığın olur* — ve yığın, şikâyet edilen şeyin ta kendisi.
 *
 * ## Responsive — ağaç küçük ekranda ağaç DEĞİLDİR
 *
 * | genişlik | izdüşüm |
 * |---|---|
 * | ≥1280px | yatay: yol solda, kat sağda |
 * | 768–1279 | dikey: yol üstte, kat altta |
 * | <768px | 🔴 yol = **kaydırılabilir çip şeridi**, kat = **kart listesi** |
 *
 * 375px'lik bir ekranda ağaç çizmek okunamaz. Aynı veri, **farklı izdüşüm** — ve yol
 * her üç izdüşümde de daima görünür.
 */

import { useCallback, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { drillAsk, kokNedenHaritasi } from "@/lib/api-client";
import type { CubeQuery, KokNedenDugum, KokNedenDurum, QueryResult } from "@/lib/types";
import { ResultView } from "@/components/ResultView";

/** Kat edilen yolun bir adımı. ⚠ Her adım **kendi** `cube_query`'sini saklar: geri
 *  dönüş bir "geri al" değil, o adımın kendi sorgusuna dönüştür. */
interface Adim {
  etiket: string;
  cubeQuery: CubeQuery;
  sonuc: QueryResult | null;
}

/** 🔴 Dört görsel ağırlık — durumun **tek** çeviricisi.
 *
 * ⚠ `olculemedi` ve `kapsam_disi` **kesikli kenarlı**: kesik çizgi *"burada bir şey
 * var ama ölçülmedi"* der; düz silik bir kutu ise yalnız *"önemsiz"* der. İki farklı
 * cümle, iki farklı çizgi. */
const AGIRLIK: Record<KokNedenDurum, { kutu: string; rozet: string; ad: string }> = {
  kanitli: {
    kutu: "border-accent/60 bg-accent/[0.07] text-foreground",
    rozet: "text-accent",
    ad: "kanıtlı",
  },
  zayif: {
    kutu: "border-[var(--surface-kenar)] bg-[var(--surface-3)] text-neutral-600 dark:text-neutral-300",
    rozet: "text-neutral-500",
    ad: "zayıf",
  },
  olculemedi: {
    kutu: "border-dashed border-[var(--surface-kenar)] text-neutral-500 opacity-80",
    rozet: "text-neutral-400",
    ad: "⊘ ölçülemedi",
  },
  kapsam_disi: {
    kutu: "border-dashed border-[var(--surface-kenar)] text-neutral-400 opacity-60",
    rozet: "text-neutral-400",
    ad: "kapsam dışı",
  },
};

/** Sinyal çubuğu — düğümün **kendi küçük grafiği**.
 *
 * ⚠ Bir sayı (`%61`) *"bu çok mu az mı?"* sorusunu cevaplamaz; bir çubuk cevaplar.
 * Ölçek 0-100 **sabittir**: kendi maksimumuna göre normalize etmek, en zayıf düğümü
 * bile dolu gösterirdi — *bir grafiği kendi verisine göre ölçeklendirmek, karşılaştırmayı
 * yok eder.* */
function SinyalCubugu({ sinyal, durum }: { sinyal: number; durum: KokNedenDurum }) {
  const dolu = Math.max(0, Math.min(100, sinyal));
  return (
    <div
      className="h-1 w-full overflow-hidden rounded-[var(--radius-chip)] bg-[var(--surface-kenar)]"
      role="img"
      aria-label={`sinyal %${dolu.toFixed(0)}`}
    >
      <div
        className={`h-full transition-[width] duration-[var(--motion-md)] ease-[var(--ease-standard)] ${
          durum === "kanitli" ? "bg-accent" : "bg-neutral-400/60"
        }`}
        style={{ width: `${dolu}%` }}
      />
    </div>
  );
}

/** Tek düğüm kartı. 🔴 **Hiçbir durumda `disabled` DEĞİL** — silik ≠ kapalı. */
function DugumKarti({
  d,
  onAc,
}: {
  d: KokNedenDugum;
  onAc: (d: KokNedenDugum) => void;
}) {
  const a = AGIRLIK[d.durum] ?? AGIRLIK.zayif;
  const acilabilir = d.cube_query !== null;
  return (
    <button
      type="button"
      onClick={() => onAc(d)}
      // ⚠ `kapsam_disi` düğümün `cube_query`si yoktur (o cube'a atlamak ayrı bir
      // adımdır) — ama yine de **tıklanabilir**: tıklanınca ne yapılabileceğini anlatır.
      title={d.gerekce ?? undefined}
      data-durum={d.durum}
      className={`flex w-full flex-col gap-1.5 rounded-[var(--radius-lg)] border p-3 text-left transition-colors duration-[var(--motion-md)] ease-[var(--ease-standard)] hover:border-accent/50 ${a.kutu}`}
    >
      <span className="flex items-baseline gap-2">
        <span className="min-w-0 flex-1 truncate text-[var(--text-panel)]">{d.etiket}</span>
        <span className={`shrink-0 font-mono text-[var(--text-etiket)] ${a.rozet}`}>
          {d.durum === "kanitli" || d.durum === "zayif" ? `%${d.sinyal.toFixed(0)}` : a.ad}
        </span>
      </span>
      <SinyalCubugu sinyal={d.sinyal} durum={d.durum} />
      {d.gerekce && (
        <span className="text-[var(--text-etiket)] leading-snug text-neutral-500 dark:text-neutral-400">
          {d.gerekce}
        </span>
      )}
      {!acilabilir && (
        <span className="font-mono text-[var(--text-etiket)] text-neutral-400">
          ↳ ilişkili cube&apos;a geçmek için tıkla
        </span>
      )}
    </button>
  );
}

export function KokNedenHaritasi({
  cubeQuery,
  sessionId,
  onNot,
}: {
  cubeQuery: CubeQuery;
  sessionId?: string;
  /** Vaka kaydı → sohbet. 🔴 Not **yoluyla birlikte** gider: *bir not, kökeni olmadan
   *  bir kanaattir.* Yol kaydedilmezse not yeniden üretilemez, doğrulanamaz, tartışılamaz. */
  onNot?: (kayit: { yol: string[]; not: string; cubeQuery: CubeQuery }) => void;
}) {
  const [yol, setYol] = useState<Adim[]>([]);
  const [notMetni, setNotMetni] = useState("");
  const [notAcik, setNotAcik] = useState(false);

  // Açık olan kat: yolun sonundaki sorgu (yol boşsa kökün kendisi).
  const aktifCq = yol.length ? yol[yol.length - 1].cubeQuery : cubeQuery;

  const harita = useQuery({
    queryKey: ["kok-neden", aktifCq],
    queryFn: () => kokNedenHaritasi({ cube_query: aktifCq, session_id: sessionId }),
  });

  const ac = useCallback(
    async (d: KokNedenDugum) => {
      if (!d.cube_query) return;   // kapsam dışı — cube atlaması ayrı bir adım
      // Her genişletme adımı GERÇEK bir sorgu koşar (`/ask/drill`, `expand`) ve
      // ⚠ **kendi küçük grafiğini** üretir — çıplak tablo ASLA (`ResultView` seçer).
      const cevap = await drillAsk({
        cube_query: aktifCq,
        session_id: sessionId,
        action: "expand",
        dimension: d.boyut,
      });
      setYol((y) => [
        ...y,
        { etiket: d.etiket, cubeQuery: cevap.cube_query ?? d.cube_query!, sonuc: cevap.result },
      ]);
    },
    [aktifCq, sessionId],
  );

  /** 🔴 Geri dönüş **yolu kısaltır**, bir "geri al" değildir: her adım kendi sorgusunu
   *  taşıdığı için o noktaya dönmek yeniden hesaplama gerektirmez. */
  const geriDon = (i: number) => setYol((y) => y.slice(0, i));

  const yolEtiketleri = ["kök", ...yol.map((a) => a.etiket)];

  const notKaydet = () => {
    const metin = notMetni.trim();
    if (!metin) return;
    onNot?.({ yol: yolEtiketleri, not: metin, cubeQuery: aktifCq });
    setNotMetni("");
    setNotAcik(false);
  };

  const dugumler = harita.data?.dugumler ?? [];
  const son = yol.length ? yol[yol.length - 1] : null;

  return (
    <div className="flex min-h-0 flex-col gap-3">
      {/* ── YOL — üç izdüşümün HEPSİNDE görünür ────────────────────────────
          🔴 <768px'te ağaç çizilmez: 375px'lik bir ekranda ağaç okunamaz.
          Aynı veri, farklı izdüşüm — yol bir **kaydırılabilir çip şeridi** olur. */}
      <nav
        aria-label="Kök-neden yolu"
        data-yol
        className="flex shrink-0 items-center gap-1 overflow-x-auto pb-1"
      >
        {yolEtiketleri.map((e, i) => (
          <span key={`${e}-${i}`} className="flex shrink-0 items-center gap-1">
            {i > 0 && <span className="text-neutral-400">›</span>}
            <button
              type="button"
              onClick={() => geriDon(i)}
              className={`rounded-[var(--radius-chip)] px-2 py-0.5 font-mono text-[var(--text-etiket)] transition-colors ${
                i === yolEtiketleri.length - 1
                  ? "bg-accent/10 text-accent"
                  : "text-neutral-500 hover:text-foreground"
              }`}
            >
              {e}
            </button>
          </span>
        ))}
      </nav>

      {/* ── AÇIK KAT'IN KENDİ GRAFİĞİ — çıplak tablo ASLA ────────────────── */}
      {son?.sonuc && (
        <div className="shrink-0 rounded-[var(--radius-lg)] border border-[var(--surface-kenar)] bg-[var(--surface-2)] p-2">
          <ResultView result={son.sonuc} />
        </div>
      )}

      {/* ── DÜĞÜMLER — yalnız BİR kat; kardeşler yok, çocuklar yok ──────────
          `md:grid-cols-2 xl:grid-cols-3`: dar ekranda **kart listesi**, geniş
          ekranda yatay yayılım. Ağaç çizgisi yok — çünkü tek kat gösteriliyor
          ve *bir katın çizgisi, olmayan bir dallanmayı ima eder.* */}
      {harita.isPending ? (
        <p className="text-[var(--text-panel)] text-muted">yollar puanlanıyor…</p>
      ) : harita.isError ? (
        <p className="text-[var(--text-panel)] text-negative">
          Kök-neden haritası alınamadı — sorgu yapısal bir cube_query taşımıyor olabilir.
        </p>
      ) : dugumler.length === 0 ? (
        <p className="text-[var(--text-panel)] text-muted">
          {harita.data?.note ?? "Bu sorguda dallanacak kullanılmayan boyut kalmadı."}
        </p>
      ) : (
        <div className="grid min-h-0 gap-2 overflow-auto md:grid-cols-2 xl:grid-cols-3">
          {dugumler.map((d) => (
            <DugumKarti key={`${d.boyut}-${d.durum}`} d={d} onAc={ac} />
          ))}
        </div>
      )}

      {/* ── NOT — kökeniyle kaydedilir ──────────────────────────────────────
          🔴 *Bir not, kökeni olmadan bir kanaattir.* Bu, deponun makbuz kültürünün
          birebir karşılığı: yol kaydedilmezse not yeniden üretilemez, doğrulanamaz,
          tartışılamaz. */}
      {onNot && (
        <div className="shrink-0 border-t border-[var(--surface-kenar)] pt-2">
          {notAcik ? (
            <div className="flex flex-col gap-1.5">
              <span className="font-mono text-[var(--text-etiket)] text-neutral-400">
                {yolEtiketleri.join(" ── ")} ── ✎
              </span>
              <textarea
                value={notMetni}
                onChange={(e) => setNotMetni(e.target.value)}
                rows={2}
                autoFocus
                placeholder="Bu noktada ne gördün?"
                className="w-full resize-none rounded-[var(--radius-btn)] border border-[var(--surface-kenar)] bg-[var(--surface-2)] px-2 py-1.5 text-[var(--text-panel)] outline-none focus:border-accent/60"
              />
              <div className="flex gap-1.5">
                <button
                  type="button"
                  onClick={notKaydet}
                  disabled={!notMetni.trim()}
                  className="rounded-[var(--radius-btn)] bg-accent px-3 py-1 text-[var(--text-panel)] text-white transition-opacity disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                >
                  sohbete kaydet
                </button>
                <button
                  type="button"
                  onClick={() => setNotAcik(false)}
                  className="rounded-[var(--radius-btn)] px-3 py-1 text-[var(--text-panel)] text-muted transition-colors hover:text-foreground"
                >
                  vazgeç
                </button>
              </div>
            </div>
          ) : (
            <button
              type="button"
              onClick={() => setNotAcik(true)}
              className="rounded-[var(--radius-btn)] px-2 py-1 font-mono text-[var(--text-etiket)] text-neutral-500 transition-colors hover:text-accent"
            >
              ✎ bu noktada not al
            </button>
          )}
        </div>
      )}
    </div>
  );
}
