r"""🔴🔴 `§0.7` — BİR KART KİMLİĞİ **BİR İŞİ** GÖSTERMELİ; göstermiyorsa **yazılı olmalı**.

## Ölçülen kusur

Bir denetim ajanı raporun kimlik uzayının çöktüğünü bildirdi; kendi ölçümüm **daha
yaygın** buldu: `68` kart kimliğinden **13'ü** birden çok başlık taşıyor, ve **dokuz
`D`** gerçek çakışma — üç ayrı bölüm aynı adları **bağımsız** kullanmış.

    §38      kapanış kartları        D1 = Garsona şema verme
    §14.1    FAZ 3 yol haritası      D1 = Olgu sayacı
    §14.11   rakip analizi kalemleri D7 = AVA `ckb`  (§38'de D7 = Yetki denetimi)

🔴 **Bu bir biçim kusuru değil, bir ÖLÇÜM kusurudur.** Çakışan bir kimlik iki farklı
işaret taşır ve **ikisi de doğru** görünür:

    «✅ D1 · Olgu sayacı TAMAMLANDI»            (§14.1)
    «⏸ D11 olgu üretimi — sayaç tesisatı PARK»  (§38.3/§40.9)

İkisi **aynı işi** anlatıyor. *Bir raporda bir kimlik iki işi gösteriyorsa, o raporun
karne satırları artık sayılamaz — çünkü sayım kimliğe dayanır.*

⊙ **Bedeli soyut değil:** `§14.11 D9` *«MCP açılınca zorunlu hâle gelir»* diyor,
`mcp_yuzeyi: beta` **açıldı**, madde **işaretsiz** — ama *«D9»* adı `§38`'de ✅ okunduğu
için hiçbir tarama kırmızı vermiyor. **Bir kimliğin çakışması, bir borcu görünmez yapar.**

## Bu kapı ne yapar — ve bilerek ne YAPMAZ

✅ Çakışmaları **rapordan sayar** ve her birinin `§0.7` kimlik haritasında **yazılı**
olmasını ister. Yeni bir çakışma doğarsa harita güncellenene kadar kırmızı kalır.

⊘ **Kimlikleri yeniden numaralandırmayı İSTEMEZ.** Numaraları değiştirmek, onlara atıf
yapan commit mesajlarını ve kapı dosyalarını **sessizce yanlış** yapardı — yani çakışmayı
düzeltirken daha kötü bir çakışma üretirdi.

> *Bir kimliği yeniden adlandırmak geçmişi yanlışlar; onu belgelemek yalnız geleceği
> düzeltir.*
"""

from __future__ import annotations

import collections
import pathlib
import re

import pytest

_RAPOR = (pathlib.Path(__file__).parent.parent.parent / "belgeler" / "arastirma"
          / "2026-08-11_REKABET-VE-MIMARI-ANALIZI.md")

pytestmark = pytest.mark.skipif(
    not _RAPOR.parent.is_dir(),
    reason="`belgeler/` bağlanmamış — konteynere `-v \"$PWD/belgeler:/belgeler:ro\"` ekleyin")

#: 🔴 **AYNI İŞ, FARKLI İFADE** — bir çakışma değil, bir yeniden yazım.
#:
#: ⚠ Liste `ADR-0008` anlamında **kapalıdır**: her kalem tek tek okunup *«bu iki başlık
#: aynı işi mi anlatıyor»* diye yargılandı. Bir kimliği buraya eklemek, o yargıyı
#: **vermek** demektir — ve yanlış verilirse bir borcu bu kapı da görünmez yapar.
#:
#: ⊙ Ayrımın kendisi ölçülemez: *«aynı iş mi, başka iş mi»* bir **yargıdır**, bir ölçüm
#: değil (bu deponun ㊾ numaralı dersi: bir alanı türetmek, onu üreten yargıyı da
#: türetebiliyorsan mümkündür). O yüzden yargı **listeye yazılıyor**, koda değil.
AYNI_IS_FARKLI_IFADE = {
    # `§C3` iki kez yazıldı: kalem *«MCP yüzeyini aç»*, kapanışı *«MCP açılış şartları»*
    "C3": "MCP yüzeyi — kalem ve açılış şartları aynı işin iki yüzü",
    # `§E3` kartı FDR idi; ölçüm BH'yi çürüttü ve yerine *«tarama genişliği beyanı»* kondu
    "E3": "FDR → beyan: kartın kendisi ölçümle YER DEĞİŞTİRDİ, ikinci bir iş değil",
    # `§F1` başlığı ayrıştırıcıya `###` satırı olarak düşüyor — bir kimlik değil
    "F1": "ayrıştırıcı gürültüsü: `### F ·` başlığı kimlik sanılıyor",
    # `§F14` başlığı bu turda düzeltildi (*«dört kullanılmayan»* → *«biri kullanılıyor»*)
    "F14": "aynı kart, başlığı 2026-08-12'de ölçümle düzeltildi",
    # ⟳ 08-12, geniş desenle görünür oldular — ikisi de AYNI İŞİN iki yazımı:
    "A12": "«Tur bazında ölçüm» ↔ «Çok turlu belleği TUR BAZINDA ölç» — kısaltma",
    "B12": "«Granülerliği tek kaynağa bağla + hour/minute aç» ↔ «hour/minute» — kısaltma",
}

#: 🔴 **KOD TARAFI ÇAKIŞMALAR** — haritada yazılı ama bu kapı **ölçemez**.
#: Bir kimliğin ikinci/üçüncü anlamı **kodda** yaşıyorsa (modül, sınıf, kapı dosyası),
#: raporu ayrıştıran bir kapı onu göremez. Bu bir kusur değil bir **KAPSAM**tır ve
#: `§0.7`'de de yazılıdır. *Bir kapının kapsamı, kapının kendisi kadar bir vaattir.*
HARITA_KOD_TARAFI = {
    "B9": "üç anlam: `§14.14` hakem (rapor) · `app/diyalog.py:89` ODAK VARLIK (kod) · "
          "`tests/test_b9_sparc_iliskileri.py` SParC (kapı) — son ikisi rapor dışında",
}

_MARKA = re.compile(r"[🔴🟡🟢✅⊘⏸⟳⚠⊙*`]")


def _temiz(t: str) -> str:
    return re.sub(r"\s+", " ", _MARKA.sub("", t).strip(" —·|").strip())


def _kimlikler() -> dict[str, set[str]]:
    """→ `{kimlik: {başlık, …}}` — hem tablo satırlarından hem alt başlıklardan."""
    s = _RAPOR.read_text(encoding="utf-8")
    kal: dict[str, set[str]] = collections.defaultdict(set)
    # 🔴🔴 **DESEN GENİŞLETİLDİ** (⟳ 08-12, denetim ajanı buldu, kendi ölçümüm doğruladı).
    # Eski hâli `[^|*\n]` idi ve hücre `🔴 **Draco…**` gibi **kalın** başlarsa `*`'ta
    # **duruyordu** → başlık kesiliyor, çakışma görünmüyordu. Ölçüm:
    #     dar desen : 62 kimlik · 13 çakışma · D6 ✗ D10 ✗
    #     geniş     : 68 kimlik · 17 çakışma · D6 ✓ D10 ✓
    # Marka temizliğini `_temiz()` **zaten** yapıyordu; desenin onu beklemesi gerekiyordu.
    # *Bir ayrıştırıcı, kendi temizleyicisinden önce durursa onu hiç çağırmamış olur.*
    desenler = (
        r"\*\*([A-F]\d{1,2})\*\*\s*\|\s*([^|\n]{4,60})",
        r"^#{3,4}\s*[⟳✅⊘⏸🔴🟡🟢 ]*([A-F]\d{1,2})\s*·\s*([^\n—(]{4,60})",
    )
    for d in desenler:
        for m in re.finditer(d, s, re.M):
            baslik = _temiz(m.group(2))
            # ⚠ `###` içeren bir yakalama bir başlık satırıdır, bir kart adı değil
            if baslik and "#" not in baslik:
                kal[m.group(1)].add(baslik)
    return kal


def _cakisanlar() -> dict[str, list[str]]:
    """Gerçek çakışmalar — **ön ek** olanlar elenir.

    ⚠ `«VQR → garson few-shot»` ile `«VQR → garson few-shot 🔴 EN YÜKSEK GETİRİ»` iki iş
    değil, bir işin iki yazımıdır. Bunu elemeyen bir sayaç, kendi gürültüsünü bulgu diye
    raporlar (ders ㉘).
    """
    cak = {}
    for k, v in _kimlikler().items():
        # ⚠ **TÜRKÇE BÜYÜK HARF** (ders ⑧): `İki-sağlayıcılı` ile `iki-sağlayıcılı`
        # aynı başlıktır ama `str.lower()` bunu ÇÖZMEZ (`İ` → `i̇`, birleşik noktalı).
        # Ölçüldü: `B9` bu yüzden **sahte bir çakışma** olarak sayılıyordu.
        def _kat(x: str) -> str:
            return x.replace("İ", "i").replace("I", "ı").lower()

        kalan = [a for a in v
                 if not any(a != b and _kat(b).startswith(_kat(a)) for b in v)]
        if len(kalan) > 1:
            cak[k] = sorted(kalan)
    return cak


def test_OLCUM_TABANI_AYAKTA():
    """⊘ **Boş yeşil avı** — sıfır kimlik ayrıştıran bir sayaç her raporu doğrular."""
    kal = _kimlikler()
    assert len(kal) >= 40, (
        f"⊘ ölçüm tabanı çöktü: yalnız {len(kal)} kart kimliği ayrıştırıldı. "
        "Raporun tablo biçimi değiştiyse ayrıştırıcı düzeltilsin — kapı susturulmasın.")


def test_HER_CAKISMA_YA_HARITADA_YA_GEREKCELI():
    """🔴🔴 **ASIL KAPI.** Çakışan her kimlik ya `§0.7` haritasında **yazılı** olmalı,
    ya da *«aynı iş, farklı ifade»* diye **gerekçelenmiş**.

    Kırmızı verirse yeni bir kimlik iki işi gösteriyor demektir — ve o an bir borç
    görünmez olmaya başlamıştır.
    """
    metin = _RAPOR.read_text(encoding="utf-8")
    harita = metin[metin.index("### 0.7 "):metin.index("\n## ", metin.index("### 0.7 "))]
    bildirilmemis = {}
    for k, basliklar in _cakisanlar().items():
        if k in AYNI_IS_FARKLI_IFADE:
            continue
        if f"**{k}**" not in harita:
            bildirilmemis[k] = basliklar
    assert not bildirilmemis, (
        f"🔴 KİMLİK ÇAKIŞMASI BİLDİRİLMEMİŞ: {bildirilmemis}\n"
        "Bu kimlik(ler) birden çok işi adlandırıyor ama `§0.7` kimlik haritasında yok. "
        "*Bir kimliğin çakışması bir borcu görünmez yapar* — haritaya yazın (yeniden "
        "numaralandırmayın: numara değiştirmek geçmiş commit'leri sessizce yanlışlar), "
        "ya da aynı işin iki yazımıysa `AYNI_IS_FARKLI_IFADE`'ye **gerekçesiyle** ekleyin.")


def test_HARITA_OLCUMLE_TUTUYOR():
    """⚠ Ters yön: haritada yazılı ama **artık çakışmayan** bir kimlik kalmamalı.

    ⊙ Bu, `§F8` hijyeninin kimlik uzayındaki hâli: bayat bir uyarı, gerçek bir uyarıyı
    gürültüye boğar. *Kalkmış bir riski ilan etmeye devam etmek, ilanın kendisini
    okunmaz yapar.*
    """
    metin = _RAPOR.read_text(encoding="utf-8")
    bas = metin.index("### 0.7 ")
    harita = metin[bas:metin.index("\n## ", bas)]
    yazili = set(re.findall(r"\|\s*\*\*([A-F]\d{1,2})\*\*\s*\|", harita))
    assert yazili, "⊘ ölçüm tabanı çöktü: `§0.7` haritasından hiç kimlik okunamadı"
    olculen = set(_cakisanlar())
    # ⚠ Kod tarafı çakışmalar burada da muaf — bu kapı RAPORU ayrıştırır ve
    # `B9`'un iki anlamı kodda yaşıyor (yukarıdaki `HARITA_KOD_TARAFI`).
    hayalet = yazili - olculen - set(HARITA_KOD_TARAFI)
    assert not hayalet, (
        f"🔴 `§0.7` haritası BAYAT: {sorted(hayalet)} artık çakışmıyor. "
        "Kimlik tekilleştiyse satır kaldırılsın — *bayat bir uyarı, gerçek uyarıyı "
        "gürültüye boğar.*")


def test_D9_BORCU_HARITADA_ADIYLA_GECIYOR():
    """🔴 Çakışmanın **ölçülmüş bedeli** yazılı kalmalı.

    `§14.11 D9`'un şartı (`mcp_yuzeyi` açılması) gerçekleşti ama madde işaretsiz kaldı,
    çünkü *«D9»* `§38`'de ✅ okunuyor. Bu somut vaka haritadan düşerse, çakışmanın
    **neden** önemli olduğu da düşer ve harita bir biçim notuna dönüşür.
    """
    metin = _RAPOR.read_text(encoding="utf-8")
    bas = metin.index("### 0.7 ")
    harita = metin[bas:metin.index("\n## ", bas)]
    assert "agent_error" in harita and "mcp_yuzeyi" in harita, (
        "🔴 `D9` vakası haritadan silinmiş — *bir kuralın gerekçesi, kuralın kendisidir.*")


def test_HARITA_OLCUMLE_AYNI_SAYIDA():
    """🔴🔴 **SAYI TUTARLILIĞI** — harita, ölçülen çakışmaların **hepsini** saymalı.

    Ölçülen kusur (08-12): `§0.7` haritası **dokuz `D`** sayıyordu, gerçek **on bir**
    (`D6` ve `D10` eksikti) — ve kapı bunu **göremiyordu**, çünkü ayrıştırıcısı `**`'ta
    duruyordu. Yani harita eksik, kapı kör, ve taban yüklemi (`≥40`) **62** sayıp yeşil
    kalıyordu: *sağlıklı görünen bir kapı, iki satırı sessizce düşürüyordu.*

    ⚠ Bu yüklem `test_HER_CAKISMA_YA_HARITADA_YA_GEREKCELI`'den **farklı**: o *«her
    çakışma bir yerde yazılı mı»* diye sorar, bu *«sayılar tutuyor mu»* diye. İkisi
    ayrı kusur sınıfı — biri **eksik satır**, öteki **eksik ayrıştırma**.
    """
    metin = _RAPOR.read_text(encoding="utf-8")
    bas = metin.index("### 0.7 ")
    harita = metin[bas:metin.index("\n## ", bas)]
    import re as _re

    yazili = set(_re.findall(r"\|\s*\*\*([A-F]\d{1,2})\*\*\s*\|", harita))
    olculen = {k for k in _cakisanlar() if k not in AYNI_IS_FARKLI_IFADE}
    yazili -= set(HARITA_KOD_TARAFI)          # kapının ölçemediği, ama YAZILI olanlar
    assert yazili == olculen, (
        f"🔴 HARİTA ↔ ÖLÇÜM AYRIŞTI\n"
        f"  haritada var, ölçümde yok : {sorted(yazili - olculen)}\n"
        f"  ölçümde var, haritada yok : {sorted(olculen - yazili)}\n"
        "*Bir haritanın eksik olması, ayrıştırıcının kör olmasından ayırt edilemez — "
        "bu yüzden ikisi de sayılır.*")
