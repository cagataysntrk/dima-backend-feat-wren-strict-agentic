"use client";

/** FAZ 7.5 · **A11Y-4** — `window.prompt()` yerine erişilebilir ad sorma yüzeyi.
 *
 * ## Ölçülen kusur
 *
 * `window.prompt("Yeni pano adı:", …)` depoda **dört yerde** birincil etkileşim
 * yüzeyiydi (`AnalysisCanvas` · `DashboardsPanel` ×2 · `ReportCard`). EK I'nin
 * **A11Y-4**'ü bunu açıkça yasaklıyor ve gerekçesi teorik değil:
 *
 * | # | `window.prompt()` neden bir yüzey değildir |
 * |---|---|
 * | 1 | **Tarayıcı onu bastırabilir** — Chrome iframe'de ve arka plan sekmesinde hiç göstermez; çağrı `null` döner ve kullanıcı **hiçbir şey görmeden** iptal etmiş sayılır |
 * | 2 | **Ana iş parçacığını kilitler** — açıkken React render edemez, sorgu iptal edilemez |
 * | 3 | **Stillenemez** — karanlık modda beyaz bir sistem kutusu açılır (FAZ 7.2'nin tam tersi) |
 * | 4 | **Doğrulanamaz** — boş ad, çok uzun ad, yalnız boşluk: `prompt` hiçbirini söyleyemez |
 *
 * 🔴 (1) en sinsisidir: **hata gibi görünmez, iptal gibi görünür.** Kullanıcı panonun
 * neden oluşmadığını asla öğrenemez.
 *
 * ## Neden `Promise` döndüren bir hook
 *
 * `window.prompt` **senkron bir değer** döndürür; onu bir bileşen ağacına çevirmek
 * normalde dört çağrı yerinin **hepsinin** state makinesi yazmasını gerektirirdi —
 * yani aynı kuralın **dört sahibi**. `sor()` bir `Promise<string | null>` döndürerek
 * çağrı yerlerini `const ad = await sor(...)` satırında bırakır: **tek satır değişti,
 * davranış tamamen değişti.**
 *
 * ⚠ `null` dönüşü `window.prompt` ile **aynı anlamı** taşır (iptal) — çağıranların
 * mevcut `if (!title) return` kontrolleri geçerli kalır, sessizce anlam kaymaz.
 */

import { useCallback, useRef, useState } from "react";

import { useOdakTuzagi } from "@/lib/odakTuzagi";

/** Pano/rapor adı üst sınırı. ⚠ `window.prompt` bunu **söyleyemezdi**; 300 karakterlik
 *  bir ad sunucuya gider ve orada reddedilirdi — hata, sebebinden çok uzakta. */
const AZAMI = 80;

type Istek = {
  baslik: string;
  varsayilan: string;
  coz: (deger: string | null) => void;
};

/** `sor()` + render edilecek `alan`. Kullanım:
 *
 * ```tsx
 * const { sor, alan } = useAdSor();
 * const yeni = async () => { const ad = await sor("Yeni pano adı:", "Panom"); if (!ad) return; … };
 * return (<> … {alan} </>);
 * ```
 */
export function useAdSor() {
  const [istek, setIstek] = useState<Istek | null>(null);
  const [deger, setDeger] = useState("");
  // ⚠ Aynı anda iki `sor()` açılırsa ilkinin sözü **asla çözülmezdi** ve çağıran
  // sonsuza kadar beklerdi — bu yüzden önceki istek iptalle kapatılır.
  const acikRef = useRef<Istek | null>(null);

  const sor = useCallback((baslik: string, varsayilan = "") => {
    acikRef.current?.coz(null);
    setDeger(varsayilan);
    return new Promise<string | null>((coz) => {
      const y = { baslik, varsayilan, coz };
      acikRef.current = y;
      setIstek(y);
    });
  }, []);

  const kapat = useCallback((sonuc: string | null) => {
    acikRef.current?.coz(sonuc);
    acikRef.current = null;
    setIstek(null);
  }, []);

  const alan = istek ? (
    <AdSorKutusu
      baslik={istek.baslik}
      deger={deger}
      setDeger={setDeger}
      onIptal={() => kapat(null)}
      onOnay={() => kapat(deger.trim() || null)}
    />
  ) : null;

  return { sor, alan };
}

function AdSorKutusu({
  baslik,
  deger,
  setDeger,
  onIptal,
  onOnay,
}: {
  baslik: string;
  deger: string;
  setDeger: (v: string) => void;
  onIptal: () => void;
  onOnay: () => void;
}) {
  const ref = useOdakTuzagi<HTMLDivElement>(true, onIptal);
  const bos = deger.trim().length === 0;
  const uzun = deger.length > AZAMI;

  return (
    // Perde: tıklama iptaldir — ama `onMouseDown` DEĞİL `onClick` ile, yoksa kutunun
    // içinde başlayıp dışında biten bir metin seçimi kutuyu kazara kapatırdı.
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      onClick={onIptal}
    >
      <div
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-labelledby="adsor-baslik"
        className="w-full max-w-sm border border-hairline bg-background p-4 shadow-[var(--shadow-2)]"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="adsor-baslik" className="mb-3 font-mono text-[12px] text-foreground">
          {baslik}
        </h2>
        <input
          autoFocus
          value={deger}
          onChange={(e) => setDeger(e.target.value)}
          onKeyDown={(e) => {
            // A11Y-5: fareye zorunlu bağımlılık yok — Enter onaylar, Esc tuzakta iptal eder.
            if (e.key === "Enter" && !bos && !uzun) onOnay();
          }}
          aria-label={baslik}
          aria-invalid={uzun || undefined}
          aria-describedby={uzun ? "adsor-hata" : undefined}
          className="w-full border border-hairline bg-transparent px-2 py-1.5 font-mono text-[12px] text-foreground outline-none focus:border-accent"
        />
        {/* 🔴 A11Y-9 / K6: sınır rengi TEK KANAL olamaz — hata metni de yazılır. */}
        {uzun && (
          <p id="adsor-hata" className="mt-1.5 font-mono text-[11px] text-[var(--negative)]">
            ⚠ En çok {AZAMI} karakter ({deger.length}).
          </p>
        )}
        <div className="mt-3 flex justify-end gap-2">
          <button
            onClick={onIptal}
            className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-500 transition-colors hover:text-foreground"
          >
            vazgeç
          </button>
          <button
            onClick={onOnay}
            disabled={bos || uzun}
            className="border border-hairline px-2 py-1 font-mono text-[11px] text-foreground transition-colors hover:border-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
          >
            tamam
          </button>
        </div>
      </div>
    </div>
  );
}
