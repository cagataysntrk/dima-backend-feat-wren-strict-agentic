"use client";

/** **İSTEMCİ DEĞERİ** — sunucuda okunamayan bir değeri hidrasyonu bozmadan okur.
 *
 * ## 🔴 Çözdüğü gerçek sorun
 *
 * `localStorage` · `document.cookie` · `window.innerWidth` sunucuda **yoktur**. Bu
 * yüzden depoda dört yerde aynı desen vardı:
 *
 * ```ts
 * const [x, setX] = useState(varsayilan);
 * useEffect(() => { setX(oku()); }, []);   // ← effect gövdesinde senkron setState
 * ```
 *
 * Niyet doğruydu (`useState(() => localStorage…)` yazmak **hidrasyon hatası** verirdi:
 * sunucu render'ı ile istemci render'ı ayrışır), ama uygulama React'ın uyardığı deseni
 * kuruyordu — *"effect gövdesinde senkron `setState` basamaklı render tetikler"* —
 * ve **dört kopya** hâlinde.
 *
 * ## Doğru araç: `useSyncExternalStore`
 *
 * React bu iş için **tam olarak** bunu sunuyor ve üçüncü parametresi (`getServerSnapshot`)
 * sorunun kendisini adlandırıyor: *"sunucuda ne göstereyim?"*. Hidrasyon uyumu React'ın
 * garantisi olur, bizim dikkatimizin değil.
 *
 * ⚠ Abonelik **boştur** (`() => () => {}`) ve bu doğrudur: bu değerler bir olay
 * yayınlamaz, yalnız ilk okumada gerekir. *Olmayan bir aboneliği taklit etmek, olmayan
 * bir güncellemeyi vaat etmek olurdu.* Değişimi yayınlayan bir kaynak varsa (tema gibi)
 * o kendi abonesini kurar — bkz. `lib/tema.ts`.
 */

import { useCallback, useSyncExternalStore } from "react";

const BOS_ABONE = () => () => {};

/** `oku()` yalnız **istemcide** çağrılır; sunucuda `sunucuVarsayilan` döner.
 *
 * ⚠ `oku` her render'da yeni bir kimlik alırsa `useSyncExternalStore` sonsuz döngüye
 * girer — o yüzden çağıran ya modül düzeyinde bir fonksiyon geçmeli ya da
 * `useCallback` kullanmalı. Bu kısıt burada **yazılıdır**, çünkü ihlali sessiz değil
 * ama teşhisi zordur.
 */
export function useIstemciDegeri<T>(oku: () => T, sunucuVarsayilan: T): T {
  return useSyncExternalStore(BOS_ABONE, oku, useCallback(() => sunucuVarsayilan,
                                                          [sunucuVarsayilan]));
}
