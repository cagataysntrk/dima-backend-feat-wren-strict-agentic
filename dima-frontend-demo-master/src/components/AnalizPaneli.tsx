"use client";

/** **ANALİZ PANELİ** — grafiğin **makinesinin** yaşadığı yer.
 *
 * ## 🔴 Neden panel, neden modal DEĞİL
 *
 * Kullanıcının kendi gerekçesi: *"panel açıkken chate panele grafiğe bakıp bir yandan
 * yorum yazabilir; modalda bunu yapmak için kapatmak zorunda kalır."*
 *
 * Bu, NN/g'nin modal kuralının birebir kendisi: modal yalnız **geri alınamaz eylem**,
 * **zorunlu bilgi** ve **kesintiyi hak eden durum** için meşrudur. Analiz göstermek
 * için değil — çünkü *"arka plan içeriğini bloke eden modaller bilinçli seçimi
 * engeller"* ve kullanıcılar bunu aşmak için **aynı sayfayı ikinci sekmede açar**,
 * ki bu ürünün başarısızlık sinyalidir.
 *
 * ## Modal OLMAMANIN dört şartı — dördü de burada
 *
 * | şart | neden |
 * |---|---|
 * | `role="complementary"` — `dialog` **DEĞİL** | `dialog` rolü ekran okuyucuya *"bu bir kesinti, bitirmeden devam edemezsin"* der; vaadimiz tam tersi |
 * | **focus trap YOK** · `inert` YOK · `aria-modal` YOK | üçü de paneli modale çevirir; arkadaki sohbet **ölür** |
 * | **reflow**, overlay DEĞİL | üstüne binmek modal davranışıdır — arkadakini okuyamazsın |
 * | Escape **yalnız odak panel içindeyken** | composer'da yazarken panelin kapanması, ürünün tek vaadini kırar |
 *
 * ## 🔴 Grafiği makinesinden ayırma
 *
 * Bir rapor kartında **~59 katman/işlem** var (başlıkta 20 düğme, `InterpretationBar`'da
 * 15 kontrol, drill · katkı · reçete katmanları). Kullanıcının ölçülmüş şikâyeti:
 * *"grafikler aşırı fazla ve boğucu, asıl unsur gibi duruyor."*
 *
 * > Grafiği *"olduğu gibi"* sohbete koymak, grafiği değil **bütün makinesini** sohbete
 * > koymaktır. Ama çözüm grafiği küçültmek de değil — *okunamayan bir thumbnail, sıfır
 * > bilgi taşıyan ekstra bir etkileşim maliyetidir.*
 *
 * **Ayrım:** sohbette **temiz grafik** (sıfır kontrol) · panelde **aynı grafik + tüm
 * makine**. Sohbet **okunur**, panel **çalışılır**.
 */

import { useCallback, useEffect, useId, useRef, useState } from "react";

import { useKapsamliEscape } from "@/lib/odakTuzagi";

/** ⚠ Alt sınır **zorunlu**: ölçülmüş kusur — alt sınırsız yeniden boyutlandırmada
 *  kullanıcılar paneli minimuma çekiyor ve *"metin okunamaz hâle geliyor"*. */
export const PANEL_MIN = 400;
export const PANEL_VARSAYILAN = 480;
/** Sohbetin okunabilirlik tabanı. ⚠ Bu sınırın **altında panel açılmaz** — panel
 *  sohbeti okunamaz yaparak kendine yer açamaz. */
export const SOHBET_MIN = 520;

function maksGenislik(): number {
  if (typeof window === "undefined") return PANEL_VARSAYILAN;
  // %55'i aşamaz VE sohbete en az `SOHBET_MIN` bırakmalı — hangisi daha darsa o.
  return Math.max(PANEL_MIN, Math.min(window.innerWidth * 0.55,
                                      window.innerWidth - SOHBET_MIN));
}

export function AnalizPaneli({
  acik,
  onKapat,
  baslik,
  /** Çoklu analizde gezinme — `‹ 3/5 ›`. ⚠ Sekme şeridi **değil**: beş analizden
   *  sonra şerit taşar ve kullanıcı hangi sekmede olduğunu kaybeder. */
  sira,
  toplam,
  onOnceki,
  onSonraki,
  /** Paneli açan düğme — 🔴 kapanışta odak **buraya döner**. */
  acanRef,
  children,
}: {
  acik: boolean;
  onKapat: () => void;
  baslik: string;
  sira?: number;
  toplam?: number;
  onOnceki?: () => void;
  onSonraki?: () => void;
  acanRef?: React.RefObject<HTMLElement | null>;
  children: React.ReactNode;
}) {
  const [genislik, setGenislik] = useState(PANEL_VARSAYILAN);
  const [surukluyor, setSurukluyor] = useState(false);
  const panelRef = useRef<HTMLElement>(null);
  const baslikId = useId();

  // Ekran daralınca panel kendini **kısar** — sohbetin alt sınırını yemez.
  useEffect(() => {
    const f = () => setGenislik((g) => Math.min(g, maksGenislik()));
    window.addEventListener("resize", f);
    return () => window.removeEventListener("resize", f);
  }, []);

  // 🔴 KAPANIŞTA ODAK **açan düğmeye döner**.
  // *Odak yönetiminde ana fikir: kullanıcıyı kaybetme.* Kapanışta odağı geri
  // taşımamak, onu boşluğa ya da belgenin başına düşürür.
  const kapat = useCallback(() => {
    onKapat();
    acanRef?.current?.focus?.();
  }, [onKapat, acanRef]);

  // 🔴 ESCAPE — **tek sahipten** (`lib/odakTuzagi.ts`). Elle dinleyici yazmak,
  // `A11Y-3`'ün yasakladığı *"aynı kuralın iki sahibi"* durumunu doğururdu; kapı
  // bunu doğru şekilde kırmızı verdi ve ben muafiyet değil **genişletme** seçtim.
  useKapsamliEscape(acik, kapat, panelRef);

  // ── AYIRICI: klavyeyle de sürüklenebilir (WAI-ARIA Window Splitter) ──────
  // ⚠ Ayırıcıyı klavyesiz bırakmak yaygın bir hata: fare zorunluluğu doğurur.
  const adim = useCallback((delta: number) => {
    setGenislik((g) => Math.max(PANEL_MIN, Math.min(maksGenislik(), g + delta)));
  }, []);

  const ayiriciTus = (e: React.KeyboardEvent) => {
    const harita: Record<string, number> = { ArrowLeft: 24, ArrowRight: -24 };
    if (e.key in harita) {
      e.preventDefault();
      adim(harita[e.key]);
      return;
    }
    if (e.key === "Home") {
      e.preventDefault();
      setGenislik(maksGenislik());       // en GENİŞ panel = en dar sohbet
    } else if (e.key === "End") {
      e.preventDefault();
      setGenislik(PANEL_MIN);
    }
  };

  useEffect(() => {
    if (!surukluyor) return;
    const hareket = (e: MouseEvent) => {
      setGenislik(Math.max(PANEL_MIN, Math.min(maksGenislik(),
                                               window.innerWidth - e.clientX)));
    };
    const birak = () => setSurukluyor(false);
    window.addEventListener("mousemove", hareket);
    window.addEventListener("mouseup", birak);
    return () => {
      window.removeEventListener("mousemove", hareket);
      window.removeEventListener("mouseup", birak);
    };
  }, [surukluyor]);

  if (!acik) return null;

  return (
    <>
      {/* AYIRICI — `role="separator"` + klavye. ⚠ `aria-valuenow` **yüzde**: piksel
          değeri ekran okuyucuya hiçbir şey anlatmaz. */}
      <div
        role="separator"
        tabIndex={0}
        aria-orientation="vertical"
        aria-label="Analiz paneli genişliği"
        aria-valuenow={Math.round((genislik / (typeof window !== "undefined" ? window.innerWidth : 1)) * 100)}
        aria-valuemin={Math.round((PANEL_MIN / (typeof window !== "undefined" ? window.innerWidth : 1)) * 100)}
        aria-valuemax={55}
        onMouseDown={() => setSurukluyor(true)}
        onKeyDown={ayiriciTus}
        className="w-1 shrink-0 cursor-col-resize bg-[var(--surface-kenar)] transition-colors hover:bg-accent/40 focus:bg-accent focus:outline-none max-lg:hidden"
      />

      <aside
        ref={panelRef}
        data-no-print
        data-kayan-panel
        // 🔴 `complementary` — `dialog` DEĞİL. Gerekçe dosya başlığında.
        role="complementary"
        aria-labelledby={baslikId}
        style={{ width: genislik }}
        className="flex h-full shrink-0 flex-col border-l border-[var(--surface-kenar)] bg-[var(--surface-2)] transition-[width] duration-[var(--motion-md)] ease-[var(--ease-standard)] max-lg:fixed max-lg:inset-0 max-lg:z-40 max-lg:!w-full max-lg:border-l-0"
      >
        <header className="flex h-14 shrink-0 items-center gap-2 border-b border-[var(--surface-kenar)] px-3">
          {/* ⚠ `tabindex={-1}`: odak **otomatik taşınmaz** (kullanıcı yazıyor olabilir),
              ama Tab ile ulaşılabilir ve klavyeyle açılışta programlı odaklanabilir. */}
          <h2
            id={baslikId}
            tabIndex={-1}
            className="min-w-0 flex-1 truncate text-[var(--text-panel)] text-foreground outline-none"
          >
            {baslik}
          </h2>

          {/* ÇOKLU ANALİZ — `‹ 3/5 ›`. Sekme şeridi DEĞİL: beş analizden sonra taşar. */}
          {typeof sira === "number" && typeof toplam === "number" && toplam > 1 && (
            <div className="flex shrink-0 items-center gap-0.5 font-mono text-[var(--text-meta)] text-muted">
              <button
                onClick={onOnceki}
                disabled={!onOnceki}
                aria-label="Önceki analiz"
                className="rounded-[var(--radius-chip)] px-1.5 py-1 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
              >
                ‹
              </button>
              <span aria-live="polite">{sira}/{toplam}</span>
              <button
                onClick={onSonraki}
                disabled={!onSonraki}
                aria-label="Sonraki analiz"
                className="rounded-[var(--radius-chip)] px-1.5 py-1 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
              >
                ›
              </button>
            </div>
          )}

          <button
            onClick={kapat}
            aria-label="Analiz panelini kapat"
            title="Kapat · Esc"
            className="shrink-0 rounded-[var(--radius-btn)] px-2 py-1 text-muted transition-colors hover:bg-[var(--surface-3)] hover:text-foreground"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
              <path d="M18 6 6 18M6 6l12 12" />
            </svg>
          </button>
        </header>

        {/* ⚠ Panel içi **compact** yoğunluk — sohbet *comfortable*. İki yoğunluk
            KASITLIDIR: sohbet insan metnidir, panel veri yüzeyidir. Tutarsızlık
            değil, bağlam farkı. */}
        <div className="min-h-0 flex-1 overflow-auto p-3 text-[var(--text-panel)] leading-[var(--lh-panel)]">
          {children}
        </div>
      </aside>
    </>
  );
}
