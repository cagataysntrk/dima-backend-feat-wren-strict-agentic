"use client";

/** **HATA ŞERİDİ** — başarısız bir mutasyonun kullanıcıya görünen yüzü. (denetim F3)
 *
 * ## Neden bir şerit, bir modal değil
 *
 * Modal kullanıcıyı **durdurur** ve bir onay ister; oysa burada onaylanacak bir şey yok —
 * bir şey **olmadı** ve kullanıcının bunu bilmesi gerekiyor. Şerit, listenin üstünde
 * kalır ve kullanıcı işine devam edebilir.
 *
 * ⚠ **Kapatılabilir ama kendiliğinden kaybolmaz**: bir hata mesajı üç saniyede solarsa,
 * tam da okunması gereken anda kaybolur. *Bir hatayı zaman aşımına uğratmak, onu
 * kullanıcının dikkatine değil takvimine bağlamaktır.*
 *
 * ## K5 — panel değil
 *
 * `export function …Panel` DEĞİL: bu bir şerittir ve var olan yüzeylerin **içinde**
 * durur. Panel tavanı 13/13.
 */

export function HataSeridi({
  metin,
  onKapat,
}: {
  metin: string | null;
  onKapat?: () => void;
}) {
  if (!metin) return null;
  return (
    <div
      // 🔴 `role="alert"`: ekran okuyucu bunu **anında** duyurur. `role="status"` bir
      // ilerleme bildirimi içindir ve başarısızlığı sıraya alır — *bir hatayı sıraya
      // almak, onu ıskalatmaktır.*
      role="alert"
      className="mb-2 flex items-start gap-2 border-l-2 border-[var(--negative)] bg-[var(--negative)]/[0.06] py-1.5 pl-2.5 pr-1.5"
    >
      <p className="min-w-0 flex-1 font-mono text-[11px] leading-snug text-neutral-500">
        {metin}
      </p>
      {onKapat && (
        <button
          onClick={onKapat}
          aria-label="Hatayı kapat"
          title="Kapat"
          className="shrink-0 px-1 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground"
        >
          ✕
        </button>
      )}
    </div>
  );
}
