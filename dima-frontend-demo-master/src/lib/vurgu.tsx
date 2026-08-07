import type { ReactNode } from "react";

/**
 * 🔴 `DA-8` — **BACKEND MARKDOWN YAZIYOR, EKRANDA YORUMLAYICI YOKTU.**
 *
 * Kullanıcıya giden metinler `**kalın**` ve `*«örnek»*` işaretleri taşıyor
 * (`app/yetenek.py:335` · `app/uyum.py:387` · `app/soz.py` katalogu) — bunlar üslup
 * süsü değil, cümlenin **hangi parçasının kritik** olduğunu söyleyen işaretler.
 * Ama depoda hiçbir markdown kütüphanesi yok ve not blokları düz metin basıyordu:
 * kullanıcı *"Geleceğe dönük tahmin \*\*v1'de yok\*\*"* diye **yıldızları okuyordu**.
 *
 * Bir denetim ajanı yakaladı. *Bir vurgu işareti, yorumlanmadığında vurgunun tersini
 * yapar: gözü tam da kritik kelimeden kaçırır.*
 *
 * ## Neden kütüphane DEĞİL
 *
 * Tam bir markdown yorumlayıcısı bağlamak (link · liste · kod · HTML) bu metinlerin
 * ihtiyacı olmayan bir yüzey açar ve **HTML enjeksiyonu** yolunu da beraberinde getirir.
 * Bu işlev yalnız iki işaret tanır ve çıktısı **React düğümüdür** — `dangerouslySet`
 * yok, dolayısıyla enjeksiyon yapısal olarak imkânsız.
 *
 * ⚠ Kapsam **kapalı**: `**kalın**` ve `*eğik*`. Tanınmayan her şey **olduğu gibi**
 * kalır — *şüphede metni bozmamak, yanlış biçimlemekten iyidir.*
 */
const DESEN = /(\*\*[^*]+\*\*|\*[^*]+\*)/g;

export function vurgula(metin: string | null | undefined): ReactNode {
  if (!metin) return metin ?? null;
  const parcalar = metin.split(DESEN);
  return parcalar.map((p, i) => {
    if (p.startsWith("**") && p.endsWith("**") && p.length > 4) {
      return (
        <strong key={i} className="font-semibold text-foreground">
          {p.slice(2, -2)}
        </strong>
      );
    }
    if (p.startsWith("*") && p.endsWith("*") && p.length > 2) {
      return (
        <em key={i} className="not-italic text-neutral-400">
          {p.slice(1, -1)}
        </em>
      );
    }
    return p;
  });
}

/**
 * İşaretleri **söker** — biçimlemenin mümkün olmadığı yerler için (tek satırlık
 * liste önizlemesi gibi). Vurguyu kaybeder ama yıldızları da göstermez.
 */
export function vurguSuz(metin: string | null | undefined): string {
  return (metin ?? "").replace(/\*\*?/g, "");
}
