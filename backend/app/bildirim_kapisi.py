"""FAZ 5.9 — **BİLDİRİM KAPISI: dört sıralı adım.** [bayraksız: kural]

## Ölçülen boşluk

`brief|digest` grep'i **sıfırdı**: her schedule **ayrı bildirim** atıyor. Alarm
literatüründe yanlış-alarm oranı **%72-99** `[DOĞRULANMADI — birincil kaynak okunmadı]`,
ama bizim ölçtüğümüz somut şey şu: **aynı sinyal, aynı gün, defalarca**.

> 🔴 *Bir uyarı sistemi, susturulduğu anda ölür.* Ve susturulmasının en hızlı yolu
> **tekrarıdır** — yanlışlığı değil.

## Dört adım — **sıra bağlayıcıdır**

    1. dedup_key = H(kaynak_tip, kaynak_id, yon)
    2. suppression_window  (DB'de kayıtlı; SİLİNMEZ, GİZLENİR)
    3. önem sıralaması
    4. correlation_group   (eşzamanlı ilişkili sinyaller TEK bildirimde)

Sıra neden bağlayıcı: **önce** aynı şeyi ikinci kez göndermemek, **sonra** kalanları
önemine göre sıralamak, **en son** ilişkili olanları birleştirmek. Ters sırada bir
birleştirme, bastırılacak bir sinyali gruba sokup **grubun tamamını** kurtarırdı.

## 🔴 BASTIRILAN BİLDİRİM **SİLİNMEZ, GİZLENİR**

Bastırma bir **görünürlük** kararıdır, bir **kayıt** kararı değil. Kayıt silinirse
*"neden bana haber verilmedi"* sorusunun cevabı kimsede olmaz — ve o soru bir olaydan
**sonra** sorulur. `bastirildi` damgası kayıtta durur.

> **Karar kaydı: `ADR-0032`** — bildirim kapısı — dört sıralı adım.
> ⚠ Atıf, kararın **yaşadığı yere** yazılır: kayıt ile kod birbirini ancak
> böyle doğrulayabilir (`tests/test_adr_dosyalari.py` iki yönü de kilitler).
"""

from __future__ import annotations

import hashlib
from typing import Any

#: Varsayılan bastırma penceresi (saniye) — **1 saat**. ⚠ Sonsuz bir pencere yoktur:
#: bir sinyal *bir daha asla* söylenmemeli değil, *tekrar tekrar* söylenmemelidir.
VARSAYILAN_PENCERE = 3600

#: Önem sırası — **büyükten küçüğe**. `critical` bir bastırma penceresine **girmez**
#: (aşağıya bak): kritik bir sinyali susturmak, sistemi susturmaktan kötüdür.
ONEM = {"critical": 3, "warning": 2, "info": 1}

#: 🔴 Bastırmadan **muaf** önem düzeyi. *Tekrar rahatsız edicidir; kaçırılan bir kritik
#: sinyal geri alınamaz.* Takas bilinçli ve tek yönlü.
MUAF_ONEM = ("critical",)


def dedup_key(kaynak_tip: str, kaynak_id: str, yon: str) -> str:
    """`H(kaynak_tip, kaynak_id, yon)` — **yön dahil**.

    ⚠ `yon` neden anahtarın parçası: *"fire yükseldi"* ile *"fire normale döndü"* **aynı
    kaynaktan** gelir ama **farklı haberlerdir**. Yönü anahtardan çıkarmak, iyi haberi
    kötü haberin penceresinde bastırırdı — ve kullanıcı sorunun **çözüldüğünü** hiç
    öğrenmezdi.
    """
    ham = "\x1f".join((str(kaynak_tip), str(kaynak_id), str(yon)))
    return hashlib.sha256(ham.encode("utf-8")).hexdigest()[:32]


def bastirilir_mi(anahtar: str, onem: str, gecmis: dict[str, float], simdi: float,
                  *, pencere: int = VARSAYILAN_PENCERE) -> bool:
    """**Adım 2.** Bu anahtar pencere içinde zaten gönderildi mi?

    `gecmis`: `{dedup_key: son_gonderim_ts}`. **Saf fonksiyon** — DB'siz test edilir.

    🔴 `critical` **bastırılmaz**. Tekrar rahatsız edicidir; kaçırılan bir kritik sinyal
    **geri alınamaz**. Takas tek yönlü ve bilinçlidir.
    """
    if str(onem) in MUAF_ONEM:
        return False
    son = gecmis.get(anahtar)
    return son is not None and (simdi - son) < pencere


def correlation_group(olay: dict[str, Any]) -> str:
    """**Adım 4.** Eşzamanlı **ilişkili** sinyaller tek bildirimde toplanır.

    Grup = `kaynak_tip` + `kaynak_id`. ⚠ Yönü **içermez** (dedup anahtarının aksine):
    *"fire yükseldi"* ve *"duruş yükseldi"* aynı vardiyadan geliyorsa kullanıcı **tek
    bir haber** ister; ama aynı ölçünün iki farklı yönü **iki ayrı haberdir** ve dedup
    onları zaten ayırdı. *Gruplama bir SUNUM kararı, dedup bir GÖNDERİM kararıdır.*
    """
    return f"{olay.get('kaynak_tip') or '-'}:{olay.get('kaynak_id') or '-'}"


def kapidan_gecir(olaylar: list[dict[str, Any]], gecmis: dict[str, float], simdi: float,
                  *, pencere: int = VARSAYILAN_PENCERE) -> dict[str, Any]:
    """Dört adımı **sırayla** uygular. Döner: `{gonderilecek, bastirilan, gruplar}`.

    🔴 **Sıra bağlayıcı.** Ters sırada bir birleştirme, bastırılacak bir sinyali gruba
    sokup **grubun tamamını** kurtarırdı — yani bastırma kuralı sessizce delinirdi.

    ⚠ **Bastırılanlar DÖNER.** Çağıran onları kayda yazar (`bastirildi=True`): *bastırma
    bir görünürlük kararıdır, bir kayıt kararı değil.* Kayıt silinirse **"neden bana
    haber verilmedi"** sorusunun cevabı kimsede olmaz — ve o soru bir olaydan SONRA
    sorulur.
    """
    gonderilecek: list[dict[str, Any]] = []
    bastirilan: list[dict[str, Any]] = []

    # 1) + 2) — anahtar üret, pencereyi uygula.
    for o in olaylar or []:
        anahtar = o.get("dedup_key") or dedup_key(
            o.get("kaynak_tip") or "", o.get("kaynak_id") or "", o.get("yon") or "")
        kayit = {**o, "dedup_key": anahtar}
        if bastirilir_mi(anahtar, str(o.get("onem") or "info"), gecmis, simdi,
                         pencere=pencere):
            bastirilan.append({**kayit, "bastirildi": True})
        else:
            gonderilecek.append(kayit)

    # 3) — önem sıralaması. ⚠ Kararlı sıralama: aynı önemde **geliş sırası** korunur,
    # aksi hâlde aynı girdi farklı turlarda farklı sıralanır ve kullanıcı bunu bir
    # değişiklik sanardı.
    gonderilecek.sort(key=lambda x: -ONEM.get(str(x.get("onem") or "info"), 0))

    # 4) — ilişkili olanları grupla (sıra korunur).
    gruplar: dict[str, list[dict[str, Any]]] = {}
    for o in gonderilecek:
        gruplar.setdefault(correlation_group(o), []).append(o)

    return {"gonderilecek": gonderilecek, "bastirilan": bastirilan, "gruplar": gruplar}


def tercih_izin_veriyor_mu(kategori: str, kanal: str,
                           tercihler: list[dict[str, Any]] | None) -> bool:
    """`NotificationPreference`'ın **ilk gerçek tüketicisi** — opt-out uygulanır.

    🔴 Tablo bugüne kadar **yetimdi** (0 satır, router yok): kullanıcı bir kategoriyi
    kapatabileceğini sanıyordu ama hiçbir kod ona bakmıyordu. *Beyan edilmiş ama
    okunmayan bir tercih, verilmemiş bir sözden kötüdür.*

    ⚠ **Kayıt yoksa VARSAYILAN AÇIK**: opt-out bir **karardır**, kaydın yokluğu bir
    karar değildir. Yokluğu "kapalı" saymak, hiç ayar yapmamış bir kullanıcıyı sessize
    alırdı.
    """
    for t in tercihler or []:
        if (str(t.get("category")) == str(kategori)
                and str(t.get("channel")) == str(kanal)
                and not t.get("deleted_at")):
            return bool(t.get("enabled", True))
    return True
