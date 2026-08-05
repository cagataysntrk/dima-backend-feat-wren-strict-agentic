"use client";

/** FAZ 7.2 — **TEMA TERCİHİ**: sistem varsayımını kullanıcının açık kararı ezer.
 *
 * ## 🔴 Üç durum, iki değil
 *
 * | değer | anlamı |
 * |---|---|
 * | `"sistem"` | *"karar vermedim"* — `prefers-color-scheme` geçerli |
 * | `"light"` | *"açık istiyorum"* — sistem karanlık olsa bile |
 * | `"dark"` | *"karanlık istiyorum"* — sistem açık olsa bile |
 *
 * ⚠ İkiye indirmek (yalnız açık/karanlık) **"karar vermedim" hâlini yok ederdi**: ilk
 * açılışta bir varsayılan seçmek zorunda kalırdık ve o varsayılan, kullanıcının sistem
 * tercihini **sessizce ezerdi**.
 *
 * ## ⚠ FOUC (flash of unstyled content) — ve neden burada çözülmüyor
 *
 * `localStorage` yalnız istemcide okunur; ilk boyamada tema **bir kare** geç uygulanır.
 * Doğru çözümü `layout.tsx`'te çalışan bir **satır içi script**tir ve o, ayrı bir
 * dosyanın işi değildir. Burada **çözülmüş gibi yapılmıyor** — sınır yazılı.
 */

export type Tema = "sistem" | "light" | "dark";

const ANAHTAR = "dima-tema";

/** Kayıtlı tercih. ⚠ Tanınmayan bir değer **`"sistem"`e düşer**: bozuk bir
 *  `localStorage` değeri kullanıcıyı okuyamadığı bir temaya kilitlememeli. */
export function temaOku(): Tema {
  if (typeof window === "undefined") return "sistem";
  const v = window.localStorage.getItem(ANAHTAR);
  return v === "light" || v === "dark" ? v : "sistem";
}

/** Tercihi uygular **ve saklar**.
 *
 * 🔴 `"sistem"` seçildiğinde öznitelik **SİLİNİR**, `"light"` yazılmaz: öznitelik
 * bırakılırsa CSS o değeri bir **karar** sanar ve `prefers-color-scheme` bir daha hiç
 * devreye girmez. *"Karar vermedim" ile "açık seçtim" aynı şey değildir.*
 */
export function temaUygula(t: Tema): void {
  if (typeof document === "undefined") return;
  const kok = document.documentElement;
  if (t === "sistem") {
    kok.removeAttribute("data-theme");
    window.localStorage.removeItem(ANAHTAR);
    return;
  }
  kok.setAttribute("data-theme", t);
  window.localStorage.setItem(ANAHTAR, t);
}

/** Açılışta kayıtlı tercihi geri koyar. */
export function temaBaslat(): void {
  const t = temaOku();
  if (t !== "sistem") temaUygula(t);
}
