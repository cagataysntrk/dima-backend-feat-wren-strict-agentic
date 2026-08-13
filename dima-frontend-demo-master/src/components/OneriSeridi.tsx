"use client";

// 🔴 FAZ 6.2/6.3/6.4/6.5 — YAZARKEN-ARA ŞERİDİ.
//
// Backend motoru `backend/app/oneri.py`, ucu `GET /oneri`. Bu bileşen o ucun
// **gerçek tüketicisidir**: `test_uc_yetim_degil` bir sarmalayıcının UI'da
// çağrılmasını şart koşar (`SARMALAYICI_MUAF` bugüne dek **boş** — muafiyet
// verilmemiş, verilmeyecek).
//
// ⊘ Sorgu KOŞMAZ: tıklanan aday yalnız **metni** tamamlar. Sayıyı küp koyar.
// ⚠ Yetki süzmesi **motorda** ve **sıralamadan önce** yapılır — bu bileşen süzmez,
//   süzülmüş listeyi alır (bir öneri listesi envanterdir).

import { useEffect, useRef, useState } from "react";
import { getOneri, type OneriAdayi } from "@/lib/api-client";

/** `6.4` — debounce 200 ms. Her tuşta uç çağırmak, ucu bir DDoS'a çevirir. */
const DEBOUNCE_MS = 200;
/** `6.4` — **≤7** öneri, kaydırma yok. Görünmeyen bir öneri, olmayan bir öneridir. */
const AZAMI = 7;

export function OneriSeridi({
  metin,
  onSec,
}: {
  metin: string;
  onSec: (etiket: string) => void;
}) {
  const [adaylar, setAdaylar] = useState<OneriAdayi[]>([]);
  const [secili, setSecili] = useState(0);
  const [kapali, setKapali] = useState(false);
  const sonIstek = useRef(0);

  useEffect(() => {
    const q = metin.trim();
    if (q.length < 2 || kapali) {
      setAdaylar([]);
      return;
    }
    const kimlik = ++sonIstek.current;
    const t = setTimeout(() => {
      getOneri(q)
        .then((y) => {
          // ⚠ Yarış koruması: geç dönen ESKİ bir cevap yeni listeyi EZMEMELİ —
          // typeahead'de en sık görülen görsel hata budur.
          if (kimlik === sonIstek.current) {
            setAdaylar(y.adaylar.slice(0, AZAMI));
            setSecili(0);
          }
        })
        .catch(() => setAdaylar([]));   // öneri katmanı cevabı BOZMAZ (§101.1)
    }, DEBOUNCE_MS);
    return () => clearTimeout(t);
  }, [metin, kapali]);

  // `6.5` — Klavye: ↓↑ Enter Esc. **Poliş değil, iddianın kanıtı**: bir öneri şeridi
  // fareye mecbur bırakıyorsa yazarken-ara değildir.
  useEffect(() => {
    if (!adaylar.length) return;
    const el = (e: KeyboardEvent) => {
      if (e.key === "ArrowDown") { e.preventDefault(); setSecili((s) => (s + 1) % adaylar.length); }
      else if (e.key === "ArrowUp") { e.preventDefault(); setSecili((s) => (s - 1 + adaylar.length) % adaylar.length); }
      else if (e.key === "Enter" && adaylar[secili]) { e.preventDefault(); onSec(adaylar[secili].etiket); setKapali(true); }
      else if (e.key === "Escape") { setKapali(true); }
    };
    window.addEventListener("keydown", el, true);
    return () => window.removeEventListener("keydown", el, true);
  }, [adaylar, secili, onSec]);

  useEffect(() => { setKapali(false); }, [metin]);

  if (!adaylar.length) return null;
  return (
    <div className="mt-1 flex flex-wrap gap-1 font-mono text-xs">
      {adaylar.map((a, i) => (
        <button
          key={a.kimlik}
          type="button"
          onMouseDown={(e) => { e.preventDefault(); onSec(a.etiket); setKapali(true); }}
          className={
            "rounded border px-2 py-0.5 transition-colors " +
            (i === secili
              ? "border-accent text-accent"
              : "border-neutral-700 text-neutral-400 hover:text-neutral-200")
          }
          title={`${a.cube} · ${a.kip}`}
        >
          {a.etiket}
        </button>
      ))}
    </div>
  );
}
