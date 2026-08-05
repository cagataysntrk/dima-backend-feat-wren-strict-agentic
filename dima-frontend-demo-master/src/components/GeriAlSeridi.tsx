"use client";

/** **GERİ AL ŞERİDİ** — soft-delete'in kullanıcıya ulaşan yarısı. *(denetim F2)*
 *
 * ## 🔴 Ölçülen kusur
 *
 * Sunucu beş nesneyi **silmiyor, damgalıyor** (`deleted_at`); kayıt **duruyor**. Ama
 * arayüzde — ve **hiçbir uçta** — silinmiş bir şeyi geri getiren tek bir yol yoktu.
 *
 * > 🔴 *Kullanıcı açısından soft-delete ile hard-delete **birebir aynı deneyimdi**.*
 * > ADR-0019'un bedeli ödenmiş güvenlik ağı kimseye ulaşmıyordu —
 * > *geri alınamayan bir soft-delete, pahalı bir hard-delete'tir.*
 *
 * ## Neden modal değil, şerit
 *
 * Bir onay modalı **silmeden önce** durdurur ve her silmede kullanıcıyı yorar.
 * `onay_akisi.py`'nin kendi araştırması *"izin isteklerinin ~%93'ü onaylanıyor"* diyor:
 * her silmeye modal koymak, %93 için gereksiz bir tıklama üretirdi.
 *
 * 🔴 Doğru denge **silmeden sonra**: eylem hemen olur (hızlı yol korunur), ve yanlışsa
 * **geri alınır**. *İyi bir güvenlik ağı, yürüyüşü yavaşlatmaz; düşüşü yakalar.*
 *
 * ## ⚠ Şerit kaybolur, YETENEK kaybolmaz
 *
 * Şerit **8 saniye** durur — ama sunucuda süre sınırı **yoktur**: kayıt durduğu sürece
 * geri alınabilir. Şeridi bir sınır sanmak, kullanıcıya *"sekiz saniyede karar ver"*
 * demek olurdu. *Bir kolaylığın süresi, bir garantinin süresi değildir.*
 *
 * ⚠ **Sekiz saniye, üç değil**: bir satırın kaybolduğunu fark etmek, kararı vermekten
 * uzun sürer. Üç saniyelik bir şerit tam da fark edildiği anda kaybolur.
 *
 * ## K5 — panel değil
 *
 * Şerit; `export function …Panel` DEĞİL. Panel tavanı 13/13.
 */

import { useEffect, useRef, useState } from "react";

/** Şeridin ekranda kalma süresi. ⚠ Sunucudaki geri-alma **süresiz**; bu yalnız
 *  şeridin ömrü. */
const OMUR_MS = 8000;

export function GeriAlSeridi({
  etiket,
  onGeriAl,
}: {
  /** Silinen şeyin adı — *"silindi"* tek başına **neyin** silindiğini söylemez ve
   *  kullanıcı geri alıp almayacağına karar veremez. `null` → şerit yok. */
  etiket: string | null;
  onGeriAl: () => void | Promise<void>;
}) {
  const [gorunur, setGorunur] = useState(false);
  const [bekliyor, setBekliyor] = useState(false);
  // ⚠ Zamanlayıcı **yeni bir silmede sıfırlanmalı**: art arda iki silmede ilk sayaç
  // ikincisinin şeridini erken kapatırdı.
  const zamanlayici = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!etiket) return;
    setGorunur(true);
    setBekliyor(false);
    if (zamanlayici.current) clearTimeout(zamanlayici.current);
    zamanlayici.current = setTimeout(() => setGorunur(false), OMUR_MS);
    return () => {
      if (zamanlayici.current) clearTimeout(zamanlayici.current);
    };
  }, [etiket]);

  if (!etiket || !gorunur) return null;

  return (
    <div
      // ⚠ `role="status"` — `alert` DEĞİL: bu bir **hata değil**, kullanıcının kendi
      // yaptığı bir işin bildirimi. Alarma çevirmek, her silmeyi bir olaya dönüştürürdü.
      role="status"
      className="mb-2 flex items-center gap-2 border-l-2 border-hairline bg-neutral-500/[0.05] py-1.5 pl-2.5 pr-1.5"
    >
      <p className="min-w-0 flex-1 truncate font-mono text-[11px] text-neutral-500">
        {/* 🔴 Ad **yazılır**: *"silindi"* tek başına neyin silindiğini söylemez. */}
        <span className="text-foreground">{etiket}</span> silindi
      </p>
      <button
        onClick={async () => {
          setBekliyor(true);
          try {
            await onGeriAl();
            setGorunur(false);
          } finally {
            setBekliyor(false);
          }
        }}
        disabled={bekliyor}
        aria-label="Silmeyi geri al"
        className="shrink-0 border border-hairline px-1.5 py-0.5 font-mono text-[11px] text-foreground transition-colors hover:border-accent disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
      >
        {bekliyor ? "…" : "geri al"}
      </button>
    </div>
  );
}
