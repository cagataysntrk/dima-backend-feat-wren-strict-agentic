"""🔴 `§B13` — *«DEĞER PROFİLLEME BİZDE YOK»* — ÖLÇÜLDÜ VE ÇÜRÜDÜ.

## Kartın iddiası (`§11.5`)

> 🔴 Wren'in **6 doğruluk sütunundan biri**, bizde **yok**: kullanıcının yazdığı değer
> (*«kırmızı»*) DB'deki değere (*«KIRMIZI»*, *«Kırmızı-01»*) **eşlenmeli**.
> ⊙ `deger_capasi.py` bunun **bir kısmını** yapıyor.

## Canlı ölçüm (2026-08-12, curl)

| kullanıcının yazdığı | kurulan süzgeç | |
|---|---|---|
| `SİYAH partilerin cirosu` | `renk eq **"Siyah"**` · 1 satır | ✅ büyük/küçük **+ Türkçe İ** |
| `kontinü kasar makinesinin oee` | `makine eq **"KONTİNÜ KASAR"**` · 1 satır | ✅ ters yön (küçük → BÜYÜK) |
| `ferraro sanfor oee` | `makine eq **"FERRARO SANFOR-1"**` · 1 satır | 🔴 **kısmi → tam**: kartın `Kırmızı-01` vakasının **ta kendisi** |
| `kırmızı partilerin cirosu` | süzgeç kurulmadı · **beyan** | ✅ *«Kırmızı» renk listesinde yok. Var olanlar: Açık · Beyaz · Koyu · Orta · Siyah. Hangisini istersin?»* |

⊙ Yani hem **eşleme** hem — daha önemlisi — **eşleşmeyenin beyanı** çalışıyor.
`deger_capasi.py`'nin kendi cümlesi: *«uydurulmuş bir değer, sessiz bir sıfır satırdır…
bir uydurma yokluk, uydurma sayıdan daha sinsidir, çünkü sıfır bir cevap gibi görünür.»*

## ⚠ VE BİR SAHTE KUSUR — ürün suçlanmadan önce karakterize edildi

`siyah renkli partiler` → **0 satır, süzgeç boş** göründü. Değer eşleştirici kusuru
sanılabilirdi. Ölçüldü: cevap *«Hangi ölçüyü istiyorsun?»* — soruda **ölçü yok**
(*«partiler»* bir sayım değil bir varlık adı) ve sistem **doğru** soruyor. Ölçü verilince
(`siyah renk parti sayısı`) süzgeç kuruluyor: `renk eq "Siyah"` ✅.

> *Bir yolun çalışmadığını göstermek için, o yola gerçekten girildiğini önce doğrulamak
> gerekir.*

## 🔴 KARAR: YAPILMIYOR — ölçüye dayanan **on dördüncü** «yapma»

Kartın istediği yetenek **var ve canlı**. Geriye kalan tek fark, Wren'in profillemeyi
*build-time istatistiği* olarak tutması; bizimki **çalışma-zamanı bulanık eşleme +
katalog enum'u**. İkisi aynı kullanıcı sonucunu veriyor ve bizimki **beyan da ediyor**.
*Aynı sonucu veren iki yoldan birini, öteki «standart» diye yeniden yazmak, kazancı
ölçülmemiş bir göçtür.*
"""

from __future__ import annotations

import pytest

from tests.conftest import ask


@pytest.mark.parametrize("soru,boyut,beklenen", [
    ("bu yıl SİYAH partilerin cirosu", "renk", "Siyah"),
    ("bu yıl kontinü kasar makinesinin ortalama oee", "makine", "KONTİNÜ KASAR"),
    ("bu yıl ferraro sanfor ortalama oee", "makine", "FERRARO SANFOR-1"),
])
def test_KULLANICININ_YAZDIGI_deger_DB_degerine_eslenir(client, soru, boyut, beklenen):
    """🔴 Kartın *«eşlenmeli»* dediği şey. Üçüncü satır `Kırmızı-01` vakasıdır:
    **kısmi** bir ad (`ferraro sanfor`) **tam** değere (`FERRARO SANFOR-1`) eşleniyor."""
    d = ask(client, soru)
    suzgecler = [f for f in ((d.get("cube_query") or {}).get("filters") or [])
                 if f.get("dimension") == boyut]
    assert suzgecler, f"{boyut} süzgeci hiç kurulmadı: {d.get('note')}"
    assert suzgecler[0].get("value") == beklenen, suzgecler


def test_OLMAYAN_deger_SESSIZ_SIFIRA_donmez(client):
    """🔴 `deger_capasi`'nin varlık sebebi: *«bir uydurma yokluk, uydurma sayıdan daha
    sinsidir, çünkü sıfır bir cevap gibi görünür.»*
    ⚠ **Değişmez «şu cümle» değil «sessiz sıfır YOK»tur.** Ölçüldü: aynı soru iki farklı
    dürüst yola düşebiliyor —
      · canlı katalogda **değer çapası**: *«Kırmızı» renk listesinde yok. Var olanlar:
        Açık · Beyaz · Koyu · Orta · Siyah. Hangisini istersin?»*
      · test fikstüründe **yazım önerisi**: *«"kirmizi" yerine "karimiz" mi demek
        istedin?»*
    İkisi de bir **soru** üretir ve satır döndürmez. Testi tek bir cümleye bağlamak,
    ötekini bir kusur gibi gösterirdi (bu turda aracın yirminci yanılması olurdu).
    """
    d = ask(client, "bu yıl kırmızı partilerin cirosu")
    n = (d.get("note") or "") + " " + (d.get("answer") or "")
    satir = ((d.get("result") or {}).get("rows")) or []
    assert not satir, f"olmayan değerle satır döndü — sessiz sıfırın tersi kadar kötü: {satir[:2]}"
    assert n.strip(), "olmayan değer SESSİZCE geçti — beyan yok"
    assert "?" in n, f"beyan var ama SORU yok — kullanıcı ne yapacağını bilemez: {n[:200]}"


def test_OLCUSUZ_SORU_deger_kusuru_SANILMAZ(client):
    """⚠ Sahte kusurun kilidi: *«siyah renkli partiler»* → süzgeç boş görünür ama sebep
    **ölçü yokluğudur**, değer eşleştirici değil. Bu ayrım kaybolursa bir gün burada
    olmayan bir kusur *«düzeltilir»*."""
    d = ask(client, "siyah renkli partiler")
    n = (d.get("note") or "") + (d.get("answer") or "")
    assert "ölçü" in n.lower(), f"ölçü netleştirmesi kayboldu: {n[:160]}"
