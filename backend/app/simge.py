"""🔴🔴 `§SB` — **TEKNİK SİMGE: normalizasyonun sildiği bilgi.**

Bu modül tek bir soruyu cevaplar: *«bu token bir teknik simge mi?»* — ve cevabı bir
**sözlükten değil bir yazım imzasından** alır.

⚠ Neden `cube_router` içinde DEĞİL: o dosyanın büyüme tavanı bu eklemeyle kırmızı verdi
ve kapının kendi mesajı nettir — *«yeni davranışı modüle çıkar, tavanı yükseltme»*.
Ayrım yapısal olarak da doğru: `cube_router` **eşleştirir**, bu dosya bir **yazım
sınıfı** tanır ve o sınıfın tek sahibi olmalıdır.
"""

from __future__ import annotations

import re


#: 🔴🔴 `§SB` — **TEKNİK SİMGE, NORMALİZASYONDA YOK OLUYOR.**
#:
#: ## Ölçülen kusur (curl `N+2` turu, 2026-08-10)
#:
#:     «müşteri bazında ortalama dE bu yıl»
#:       _norm → 'musteri bazinda ortalama **de** bu yil'
#:       hiçbir küp eşleşmedi → **R4** («ölçü eşleşmedi»)
#:       kullanıcı: *«parti için hangi ölçüyü istiyorsun?»* — ve listede dE **yok**
#:
#: `dE` (Delta E, renk sapması) bir **simgedir**; normalizasyon onu `de`'ye çeviriyor ve
#: `de` Türkçede bir **bağlaçtır**. Yani terim yalnız kaybolmuyor, kaybolduğu yer de
#: onu geri getirmeyi **tehlikeli** kılıyor: `de`'yi sinonim yazmak her cümlede
#: ateşlerdi (`§73`'ün ölçtüğü tek-harf felaketinin birebir kardeşi).
#:
#: > 🔴 Ve kullanıcının kuralı burada birebir geçerli: *«tek tek sinonim yazmak
#: > aptallık»*. Kök çözüm bir sözlük değil bir **imza**.
#:
#: ## İmza — kapalı, yapısal, ölçülmüş
#:
#: Türkçe sözcüklerde **sözcük içi büyük harf yoktur**. `dE` · `kWh` · `pH` · `mAh` bu
#: imzayı taşır; `ciro` · `fire` taşımaz. Ve `OEE` gibi **tümü büyük** kısaltmalar da
#: taşımaz — onlar zaten küçültülünce doğru eşleşir, yani kapsam dışı bırakılmaları
#: bir eksik değil bir **daraltmadır**.
#:
#: ⊙ Katalog tarafı ölçüldü: simge taşıyan kimlik **tam iki tane** —
#: `kalite.ort_dE` ve `sikayet.ort_sapma_dE`. Yani yüklemin çarpma alanı **iki satır**.
#:
#: ⚠ Bu bir **yönlendirme değil bir görünürlük** düzeltmesidir: hiçbir küp seçilmez,
#: yalnız kullanıcının yazdığı simgenin sahipleri netleştirmeye **chip** olarak katılır.
#: İki sahip varken tahmin etmek zaten yasaktır (`§V5`).
#:
#: *Bir terimi normalize etmek onu okunur yapar; ama bazı terimlerin bilgisi tam olarak
#: normalize edilen yerdedir.*
_SIMGE_PARCA = re.compile(r"^[a-zçğıöşü]+[A-ZÇĞİÖŞÜ][A-Za-zÇĞİÖŞÜçğıöşü0-9]*$")


def simgeler(metin: str) -> set[str]:
    """Metindeki **sözcük içi büyük harfli** parçalar — ham (normalize EDİLMEMİŞ) girdi."""
    return {p for p in re.split(r"[^A-Za-zÇĞİÖŞÜçğıöşü0-9_]+", str(metin or ""))
            for p in re.split(r"[_]+", p) if _SIMGE_PARCA.match(p)}


def sahipler(ham_soru: str, schema: dict, *, haric: str | None = None) -> list[str]:
    """Sorudaki teknik simgeyi **kimliğinde** taşıyan ölçülerin gösterim etiketleri.

    Döner: chip etiketleri (boş liste = simge yok ya da sahibi yok). `haric` verilen
    küp atlanır — netleştirmeyi zaten o küp açmıştır.

    ⚠ Eşleşme **büyük/küçük harfe duyarlıdır**: iki taraf da simge sınıfına daraltılmış
    olduğu için bu bir katılık değil, imzanın kendisidir.
    """
    simge = simgeler(ham_soru)
    if not simge:
        return []
    out: list[str] = []
    for c in (schema or {}).get("cubes") or []:
        if haric and c.get("name") == haric:
            continue
        for m in (c.get("measures") or []):
            if not (simgeler(m) & simge):
                continue
            etiket = (c.get("measure_synonyms_display") or {}).get(m) or str(m)
            if etiket not in out:
                out.append(etiket)
    return out
