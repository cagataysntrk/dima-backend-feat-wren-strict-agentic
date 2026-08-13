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
import { getOneri, oneriTik, type OneriAdayi } from "@/lib/api-client";
import { useFeature } from "@/lib/useFeature";

/** `6.4` — debounce 200 ms. Her tuşta uç çağırmak, ucu bir DDoS'a çevirir. */
const DEBOUNCE_MS = 200;
/** `6.4` — **≤7** öneri, kaydırma yok. Görünmeyen bir öneri, olmayan bir öneridir. */
const AZAMI = 7;

export function OneriSeridi({
  metin,
  onSec,
  sonBakilanlar = [],
}: {
  metin: string;
  onSec: (etiket: string) => void;
  /** `5.9` — boş girdide gösterilecek **son bakılanlar**. Yeni bir depo AÇMAZ:
   *  sohbetin kendi kartlarından türetilir (kalıcı durum yok, izin yok, senkron yok). */
  sonBakilanlar?: string[];
}) {
  // 🔴 `6.6` — TUŞ. Kapalıyken şerit çizilmez **ve `/oneri` hiç çağrılmaz** 🆀.
  // ⚠ Planın `localStorage` çaresi UYGULANMADI: `useFeature` zaten var, bayrak normal
  // kanaldan akar ve planın kendi uyardığı **A/B kaybı** (`§40.3`) doğmaz 🆝.
  const acik = useFeature("oneri_katmani");
  const kapaliBayrak = acik === null || acik === "off";
  const [adaylar, setAdaylar] = useState<OneriAdayi[]>([]);
  const [secili, setSecili] = useState(0);
  const [kapali, setKapali] = useState(false);
  const sonIstek = useRef(0);

  useEffect(() => {
    const q = metin.trim();
    // 🔴 Bayrak kapalıysa **ağa hiç çıkma** — «çizmemek» yetmez, `E-1`'in ölçümü
    // istekten başlar.
    if (kapaliBayrak || q.length < 2 || kapali) {
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
      else if (e.key === "Enter" && adaylar[secili]) {
        e.preventDefault();
        sec(secili);
      } else if (e.key === "Escape") {
        // 🔴 `8.4` — «yazdı, hiçbirini tıklamadı» **NEGATİF** sinyaldir: gösterilenler
        // yanlıştı. Sessizce kapatmak, o bilgiyi çöpe atmak olurdu 🆆.
        oneriTik(metin.trim(), adaylar.map((a) => a.kimlik), -1);
        setKapali(true);
      }
    };
    window.addEventListener("keydown", el, true);
    return () => window.removeEventListener("keydown", el, true);
  }, [adaylar, secili, onSec]);

  useEffect(() => { setKapali(false); }, [metin]);

  // 🔴 `FAZ 8.1` — SEÇİMİN TEK KAPISI. Fare ve klavye **aynı** yoldan geçer; iki ayrı
  // yol olsaydı biri kaydeder öteki kaydetmezdi ve sayı sessizce eksik kalırdı ㊲.
  function sec(i: number) {
    const a = adaylar[i];
    if (!a) return;
    oneriTik(metin.trim(), adaylar.map((x) => x.kimlik), i);
    onSec(a.etiket);
    setKapali(true);
  }

  if (kapaliBayrak) return null;

  // `5.9` — **BOŞ GİRDİ**: uç çağrılmaz, sohbetin kendi geçmişinden son bakılanlar
  // gösterilir. ⚠ *«En çok sorulanlar»* ve *«dikeyin çekirdek 5'i»* **uygulanmadı**:
  // ikisi de ölçüye dayanır ve o ölçü kodda **yok** (bkz. `5.5`'in gerekçeli ⊘'si) —
  // uydurulmuş bir sıralama, sıralama değildir ㊱.
  if (!metin.trim() && sonBakilanlar.length && !kapali) {
    return (
      <div className="mt-1 flex flex-wrap items-center gap-1 font-mono text-xs">
        <span className="select-none text-neutral-600">son bakılanlar:</span>
        {sonBakilanlar.slice(0, AZAMI).map((e) => (
          <button
            key={e}
            type="button"
            onMouseDown={(ev) => { ev.preventDefault(); onSec(e); }}
            className="rounded border border-neutral-700 px-2 py-0.5 text-neutral-400 transition-colors hover:text-neutral-200"
          >
            {e}
          </button>
        ))}
      </div>
    );
  }

  if (!adaylar.length) return null;
  return (
    <div className="mt-1 flex flex-wrap gap-1 font-mono text-xs">
      {adaylar.map((a, i) => (
        <button
          key={a.kimlik}
          type="button"
          onMouseDown={(e) => { e.preventDefault(); sec(i); }}
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
