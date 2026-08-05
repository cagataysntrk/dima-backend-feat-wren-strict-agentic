"use client";

/** FAZ 7.5 · **A11Y-3 / A11Y-6** — modal odak tuzağı. **TEK SAHİP.**
 *
 * ## Neden bir hook, dört kopya değil
 *
 * Ölçüldü: depoda `focus-trap` / `trapFocus` **sıfır** kullanım vardı; beş bileşen
 * (`DrillDownPanel` · `ContractDetailPanel` · `Select` · `ResultView` ·
 * `SettingsDrawer`) `role="dialog"`/`fixed inset-0` açıyor ve **hiçbiri** odağı
 * tutmuyordu. Klavye kullanıcısı Tab'a bastığında odak **modalin arkasındaki** sayfaya
 * kaçıyor, ekran okuyucu kapalı bir yüzeyi okumaya devam ediyordu.
 *
 * 🔴 Her bileşene ayrı bir tuzak yazmak, bu deponun **en sık tekrarlayan kusur
 * sınıfıydı**: *"aynı kuralın iki sahibi ayrışır."* Beş kopyanın dördü bir gün
 * `shift+Tab`'ı unutur ve **hangisinin doğru olduğu ölçülemez** hâle gelir. Kural
 * burada **bir kez** yazılır.
 *
 * ## Üç davranış — üçü de bir kusurdan doğdu
 *
 * | # | Davranış | Olmasaydı |
 * |---|---|---|
 * | 1 | **Tab döngüsü** kapalı (son → ilk, shift+Tab ile ilk → son) | odak arkadaki sayfaya kaçar |
 * | 2 | **Esc kapatır** | fareye zorunlu bağımlılık (A11Y-5 ihlali) |
 * | 3 | Kapanışta odak **çağıran ögeye geri döner** | kullanıcı listede yerini kaybeder |
 *
 * ⚠ **Odağı geri vermek, açmaktan daha kolay unutulur** — çünkü açılış görünür,
 * kapanış görünmez. Bu yüzden `dispose` yolunda ve `try/finally` disiplinindedir.
 *
 * ⚠ **Sınır yazılı:** bu tuzak `inert`/`aria-hidden` ile arka planı ekran okuyucudan
 * **gizlemez** — o, kök düzeyinde bir DOM müdahalesidir ve tek bir hook'un işi
 * değildir. Burada **çözülmüş gibi yapılmıyor**.
 */

import { useEffect, useRef } from "react";

/** Odaklanabilir öge seçicisi. `[hidden]` ve `disabled` dışlanır; `tabindex="-1"`
 *  **bilinçli olarak** dışlanır — o, "programatik olarak odaklanabilir ama Tab
 *  sırasında değil" demektir. */
const ODAKLANABILIR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  '[tabindex]:not([tabindex="-1"])',
].join(",");

function odaklanabilirler(kok: HTMLElement): HTMLElement[] {
  return Array.from(kok.querySelectorAll<HTMLElement>(ODAKLANABILIR)).filter(
    (e) => e.offsetParent !== null || e === document.activeElement,
  );
}

/** Modal açıkken odağı `ref` içinde tutar, Esc'te `kapat()` çağırır, kapanışta odağı
 *  **açan ögeye** geri verir.
 *
 *  @param acik  modal görünür mü — `false` iken hiçbir dinleyici bağlanmaz
 *  @param kapat Esc'in çağıracağı kapatıcı
 */
export function useOdakTuzagi<T extends HTMLElement>(
  acik: boolean,
  kapat: () => void,
): React.RefObject<T | null> {
  const ref = useRef<T | null>(null);
  // ⚠ Kapatıcı her render'da yeni bir kimlik alabilir; dinleyiciyi yeniden bağlamak
  // yerine referansı tazeliyoruz — aksi hâlde her tuş vuruşunda yeniden bağlanırdı.
  //
  // 🔴 Ama tazeleme **render sırasında değil, commit'ten sonra** yapılır: render
  // sırasında bir ref'e yazmak React'ın açıkça yasakladığı şeydir (*"Cannot access refs
  // during render"*) ve eşzamanlı/yeniden-oynatılan render'larda **iptal edilmiş bir
  // render'ın kapatıcısını** kalıcı hâle getirebilir.
  //
  // ⚠ Bağımlılık dizisi **yok**: her commit'ten sonra koşar, yani dinleyici her zaman
  // en güncel kapatıcıyı görür. Ve dinleyici olayı **commit'ten sonra** okuduğu için
  // bir kare geç kalma riski yoktur. *Doğru zaman, en erken zaman değildir.*
  const kapatRef = useRef(kapat);
  useEffect(() => {
    kapatRef.current = kapat;
  });

  useEffect(() => {
    if (!acik) return;
    const kok = ref.current;
    if (!kok) return;

    // 🔴 Açan ögeyi ŞİMDİ yakala: kapanışta `document.activeElement` çoktan modalin
    // içindeki bir düğmedir ve oraya dönmek kullanıcıyı hiçbir yere götürmez.
    const cagiran = document.activeElement as HTMLElement | null;

    const ilk = odaklanabilirler(kok)[0] ?? kok;
    ilk.focus();

    const tus = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        kapatRef.current();
        return;
      }
      if (e.key !== "Tab") return;
      const ogeler = odaklanabilirler(kok);
      if (ogeler.length === 0) {
        e.preventDefault();
        return;
      }
      const bas = ogeler[0];
      const son = ogeler[ogeler.length - 1];
      const etkin = document.activeElement;
      // Döngüyü kapat: son → ilk (Tab), ilk → son (shift+Tab).
      if (!e.shiftKey && etkin === son) {
        e.preventDefault();
        bas.focus();
      } else if (e.shiftKey && etkin === bas) {
        e.preventDefault();
        son.focus();
      } else if (etkin instanceof Node && !kok.contains(etkin)) {
        // Odak dışarı kaçmışsa (programatik bir focus() ya da tarayıcı chrome'u)
        // geri çek — tuzağın adı bunu gerektirir.
        e.preventDefault();
        bas.focus();
      }
    };

    document.addEventListener("keydown", tus, true);
    return () => {
      document.removeEventListener("keydown", tus, true);
      // ⚠ Öge DOM'dan silinmiş olabilir; `isConnected` olmadan `focus()` sessizce
      // gövdeye düşer ve kullanıcı listedeki yerini kaybeder.
      if (cagiran?.isConnected) cagiran.focus();
    };
  }, [acik]);

  return ref;
}

/** **KAPSAMLI ESCAPE** — *modal olmayan* yüzeyler için. (FAZ 4)
 *
 * ## 🔴 Neden `useOdakTuzagi`'nın yanında, ayrı bir dosyada DEĞİL
 *
 * `test_A11Y3_TUZAGIN_TEK_SAHIBI_var` şunu söylüyor: klavye/odak kuralı **tek yerde**
 * yazılır. Üç modal kendi Esc dinleyicisini yazdığında *"hangisinin doğru olduğu
 * ölçülemez"* hâle gelmişti.
 *
 * Analiz paneli **modal değildir** ve odak tuzağı **istemez** — ama Escape ister.
 * Bu ihtiyaç için ayrı bir modül açmak, aynı kuralın **ikinci sahibini** doğururdu.
 * Doğrusu: tek sahibi **genişletmek**.
 *
 * ## Modal Escape'ten farkı — ve neden bu fark hayati
 *
 * | | modal | modal olmayan |
 * |---|---|---|
 * | Escape kapsamı | **global** — her yerden kapatır | 🔴 **yalnız odak içerideyken** |
 * | odak tuzağı | var | **yok** |
 * | arkadaki yüzey | ölü | **canlı** |
 *
 * ⚠ Escape'i modal olmayan bir panelde **global** yakalamak, kullanıcı composer'da
 * yazarken paneli kapatırdı. Panelin varlık sebebi *"hem bak hem yaz"*tı; global bir
 * Escape tam da o vaadi kırardı.
 *
 * *Aynı tuş, iki bağlamda iki farklı kuraldır — ve ikisini tek kurala indirgemek,
 * birini yanlış yapmaktır.*
 */
export function useKapsamliEscape(
  etkin: boolean,
  kapat: () => void,
  kapsam: React.RefObject<HTMLElement | null>,
) {
  useEffect(() => {
    if (!etkin) return;
    const f = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      const h = document.activeElement;
      // 🔴 Odak panelin İÇİNDE değilse dokunma — kullanıcı başka bir yerde yazıyordur.
      if (!h || !kapsam.current?.contains(h)) return;
      e.preventDefault();
      kapat();
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, [etkin, kapat, kapsam]);
}
