"use client";

/** FAZ 8.1 (kontrol listesi · madde 2) — **KAYIT BİLDİRİMİ.**
 *
 * ## Neden bu bir kod maddesi
 *
 * 8.1'in kendisi *"KOD DEĞİL"*: 1-2 gerçek kullanıcı, 2-4 hafta. Ama kontrol listesinin
 * ikinci maddesi **kod ister**: kullanıcıya *"sorularınız ürünü geliştirmek için
 * kaydediliyor"* bildirimi. Ölçüldü — **hiçbir yerde yoktu**.
 *
 * 🔴 Ve bu, ertelenebilir bir cila değil: `interaction_log` **varsayılan olarak açık**
 * (`interaction_log: bool = True`) ve gerçek kullanıcı penceresi tam da **onun
 * doldurulması için** açılıyor. *Bir veriyi toplamaya başladığın an, toplandığını
 * söylemen gereken andır — sonra değil.*
 *
 * ## Ne kaydediliyor — ve ne KAYDEDİLMİYOR
 *
 * Bildirimin işe yaraması için **ikisini birden** söylemesi gerekir. Yalnız *"kayıt
 * tutuluyor"* demek, kullanıcıya en kötüyü varsaydırır: *"demek ki verilerim de
 * saklanıyor."* Oysa `InteractionLog` **ham sonuç satırı tutmaz** — soru metni, seçilen
 * yol, red gerekçesi, süre ve token sayıları. Bunu **söylemek**, bildirimin yarısıdır.
 *
 * ## ⚠ Neden kapatılabilir ama geri getirilebilir
 *
 * Bildirim kalıcı bir şerit olsaydı, üçüncü günden sonra **görünmez** olurdu (banner
 * körlüğü) — yani bilgilendirme değil, dekor. Kapatılabilir; ama kararı `localStorage`'da
 * saklanır ve **yardım panelinden her zaman okunabilir**: *bir bildirimi kapatmak, onu
 * geri alınamaz biçimde silmek olmamalı.*
 *
 * ⚠ **Bu bir rıza (consent) mekanizması DEĞİLDİR ve öyleymiş gibi yapılmıyor.** Kapatmak
 * kaydı durdurmaz; bir onay kutusu koymak, arkasında gerçekten kaydı durduran bir yol
 * olmadan **yanlış beyandır**. Kaydı kapatma yolu bugün **yöneticidedir**
 * (`DIMA_INTERACTION_LOG=false`) ve bildirim bunu **yazıyor**.
 */

import { useState } from "react";

import { useIstemciDegeri } from "@/lib/istemci";

const ANAHTAR = "dima-kayit-bildirimi-okundu";

/** ⚠ Modül düzeyinde: `useIstemciDegeri`ye her render'da yeni kimlikli bir okuyucu
 *  geçmek `useSyncExternalStore`u sonsuz döngüye sokar. */
function _okundu(): boolean {
  return window.localStorage.getItem(ANAHTAR) === "1";
}

export function KayitBildirimi() {
  // ⚠ `useState(() => localStorage…)` YAZILMAZ: sunucuda `window` yoktur ve ilk render
  // ile istemci render'ı ayrışır (hidrasyon hatası). ⟳ Ama okuma da **effect'te
  // yapılmaz**: orada senkron `setState` basamaklı render tetikler (React'ın uyarısı).
  // Doğru araç `useSyncExternalStore`; üçüncü parametresi sorunun kendisini adlandırır:
  // *"sunucuda ne göstereyim?"*. Bkz. `lib/istemci.ts`.
  const okundu = useIstemciDegeri(_okundu, true);
  const [kapatildi, setKapatildi] = useState(false);
  const gorunur = !okundu && !kapatildi;

  if (!gorunur) return null;

  return (
    <div
      role="note"
      aria-label="Kayıt bildirimi"
      className="mx-auto flex max-w-2xl items-start gap-3 border border-hairline px-3 py-2"
    >
      <p className="min-w-0 font-mono text-[11px] leading-snug text-neutral-500">
        Sorularınız ürünü geliştirmek için <span className="text-foreground">kaydediliyor</span>{" "}
        (soru metni, seçilen yol, süre).{" "}
        {/* 🔴 İkinci yarı olmadan ilk yarı, kullanıcıya en kötüyü varsaydırır. */}
        <span className="text-foreground">Sonuç satırlarınız kaydedilmez.</span> Kaydı
        tamamen durdurmak kurulum ayarıdır (<code>DIMA_INTERACTION_LOG=false</code>) — bu
        bildirimi kapatmak kaydı durdurmaz.
      </p>
      <button
        onClick={() => {
          window.localStorage.setItem(ANAHTAR, "1");
          setKapatildi(true);
        }}
        aria-label="Kayıt bildirimini kapat"
        title="Kapat — metin yardım panelinde kalır"
        className="shrink-0 border border-hairline px-1.5 py-0.5 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
      >
        anladım
      </button>
    </div>
  );
}
