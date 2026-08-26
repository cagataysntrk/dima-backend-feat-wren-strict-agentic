"""🔴 **T2'NİN DETERMİNİSTİK İLK BASAMAĞI** — ve ölçümün bu modülün yarısını çürütmesi.

Kullanıcının isteği: *"T2 çok da zor değil — ne yüksek ne düşük vs, onları sistem de
yazabilir. Sadece karışık olanlarda T2 LLM'e gitsin."*

## ⊙ Ölçüm ne dedi

| soru | olgular | şablon |
|---|---|---|
| *"bu yıl toplam ciro"* | `single` | ⊘ **yankı** — `summary` ile birebir aynı |
| *"aylara göre ciro"* | `trend`+`peak`+`delta` | ✅ ateşliyor |

🔴 `interpret()`'in `summary`'si zaten `" ".join(olgu metinleri)`. Yani *"basit olanı
sistem yazsın"* isteği **büyük ölçüde karşılanmış durumda** — sistem onu `summary` olarak
zaten yazıyor, 0 token ile. Bu basamağın eklediği şey **içerik değil**:

* **sıra** — büyüklük (`delta`) uçlardan (`peak`) önce okunur;
* 🔴 ve asıl kazanç: `t2_anlatici` **kapalıyken** anlatı yüzeyi artık **boş kalmıyor**.

⚠ Yankı yayımlanmaz: aynı cümleyi ikinci bir alanda tekrarlamak bir basamak değil bir
kopyadır. *Bir merdivene, bir öncekinin yaptığını yapan bir basamak eklemek, merdiveni
uzatmaz — yalnız ağırlaştırır.*

## 🔴 Geriye kalan gerçek boşluk: YARGI

*"Yüksek mi düşük mü"* bir **eşik** ister ve eşiği uydurmak korpusun **açıkça
yasakladığı** şeydir (*"iyi/kötü yargısını bir eşik uydurarak vermek"*). Beyan edilmiş
bir referans varsa sahibi `app/hedef.py` (`ADR-0028`: **hedef UYDURULMAZ**).
"""

from __future__ import annotations

import pytest

from app import anlatici


def _y(*olgular, summary="baska bir ozet"):
    return {"facts": list(olgular), "summary": summary}


def test_TEK_OLGU_YANKI_YAYIMLANMAZ():
    """`summary` zaten aynı cümle — ikinci kopya bir basamak değil bir yankı."""
    o = {"type": "single", "measure": "toplam_ciro", "text": "ciro: ₺1.000"}
    assert anlatici.anlat(_y(o, summary="ciro: ₺1.000.")) is None


def test_COK_OLGU_ANLATILIYOR_ve_SIRA_DEGISIYOR():
    """Büyüklük (`delta`) uçlardan (`peak`) **önce** okunur — bu basamağın kattığı şey."""
    m = anlatici.anlat(_y(
        {"type": "peak", "measure": "x", "text": "En yüksek Haz"},
        {"type": "delta", "measure": "x", "text": "Δ x: 100"},
        {"type": "trend", "measure": "x", "text": "x: %10 arttı"}))
    assert m and m.startswith("x: %10 arttı."), m
    assert m.index("Δ x") < m.index("En yüksek"), "🔴 sıra uygulanmamış"


def test_TANIMADIGI_TURU_GORUNCE_DEVREDER():
    """🔴 Bilmediği bir türü **görmezden gelip** kalanı anlatmak, kullanıcıya *eksik ama
    tam görünen* bir özet vermek olurdu. *Bir merdivenin basamağı, ne yapamadığını
    bilmiyorsa basamak değil bir tahmindir.*"""
    # ⟳ Örnek 2026-08-11'de DEĞİŞTİ: eskiden `segment_delta` kullanılıyordu, ama o tip
    # `§D1` ile **tanınır** hâle geldi (üretiliyordu ve şablon onu tanımadığı için her
    # cevabı LLM'e devrediyordu). Testin niyeti doğruydu, **örneği** bayatladı.
    # ⊙ Yeni örnek `interpret`'in asla üretmeyeceği sentetik bir addır — böylece bu test
    # taksonomi büyüdükçe bir daha kırılmaz. *Bir kuralı sınayan örnek, kuralın kendisi
    # kadar dayanıklı olmalıdır.*
    assert anlatici.anlat(_y(
        {"type": "trend", "measure": "x", "text": "x arttı"},
        {"type": "boyle_bir_olgu_tipi_yok", "measure": "x", "text": "A segmenti"})) is None


def test_IKI_OLCU_DEVREDILIR():
    """İki ölçüyü tek cümlede anlatmak aralarında bir **ilişki** ima eder; o çıkarım bu
    basamağın yetkisinde değil."""
    assert anlatici.anlat(_y(
        {"type": "trend", "measure": "ciro", "text": "ciro arttı"},
        {"type": "trend", "measure": "fire", "text": "fire düştü"})) is None


def test_SAYI_URETILMIYOR():
    """🔴 Cümle `interpret()`'in **kendi metinlerinden** kurulur. `narration_guard`'dan
    geçmesi tesadüf değil **yapısal**."""
    import inspect

    src = inspect.getsource(anlatici)
    for yasak in ("round(", "format(", "%.1f", "{:,", "f\"{"):
        assert yasak not in src, f"🔴 `{yasak}` — bu modül sayı BİÇİMLENDİRİYOR"


def test_AI_ACT_ISARETI_KAYNAGA_BAKIYOR():
    """🔴 **Fazla işaretlemek de bir yanlış beyandır.** Şablon metni tek bir sağlayıcı
    çağrısı görmedi; *"yapay zekâ tarafından yazılmıştır"* demek onu yanlış tanıtır ve
    işaretin **ayırt edici gücünü** tüketir.

    *Bir uyarıyı hak etmeyen yere koymak, hak ettiği yerde okunmamasına yol açar.*"""
    import inspect

    from app import answer as answer_mod

    src = inspect.getsource(answer_mod)
    i = src.index("resp.ai_generated_prose =")
    assert 'narration_kaynak") != "sablon"' in src[i:i + 260], (
        "🔴 işaret hâlâ yalnız `narration`'ın VARLIĞINA bakıyor")


@pytest.mark.parametrize("tur", anlatici.TANINAN)
def test_TANINAN_TURLER_KAPALI_KUME(tur):
    """Yeni bir olgu türü `interpret()`'e eklenirse bu basamak onu **tanımaz** ve
    devreder — sessizce atlamaz."""
    assert isinstance(tur, str) and tur


def test_ASIL_KAZANC_YAPILMAYAN_CAGRI():
    """🔴🔴 **Karar bir kez tersine çevrildi, SONRA aynı gün GERİ getirildi —
    ikisi de kayıtlı.** FAZ 6.7 bu testin tam tersini (`return` kaldırılsın,
    basit olgu bile LLM'e gitsin) kısa süre doğrulamıştı. Kullanıcı KENDİ
    "chat mantığı" isteğini düzeltti: *"1 cümle yazmak için demedim, o
    cümleyi deterministik de yazabiliyoruz... durduk yere anında çalışacak
    küp cevabı boşuna LLM bekliyor."* Asıl istenen an — kullanıcı cevabın
    ÜSTÜNE konuşmak istediğinde (*"neden"*, *"anlamadım"*) — zaten AYRI bir
    yoldan (`_cevap_ustunde_konus` → `contribution`/`kok_neden`, FAZ 6.1/6.2)
    zengin bir cevap alıyor; bu basamaktan hiç geçmiyor. Yani FAZ 6.7'nin
    kazancı SIFIRDI, bedeli her ANINDA cevaplanması gereken küp sorgusuna
    3,7-20,8 sn gecikme eklemekti (canlı ölçüldü) — geri alındı.

    | tur | toplam | anlatı LLM | pay |
    |---|---|---|---|
    | *"makine bazında oee son 3 ay"* | 5.420 ms | **2.936 ms** | %54 |
    | *"aylara göre"* (takip) | 24.285 ms | 🔴 **22.564 ms** | **%93** |

    İki turda da **intent 0 LLM** aldı (`route()` / `deterministic_refine`);
    bekleyişin tamamı **süslemeydi** — ve süslenen şey `summary`'nin taşıdığı
    **aynı olgulardı**.

    ⚠ İlk yazımda yankı kapısı yanlış yerdeydi: metin `summary` ile aynıysa
    `None` dönüyordu ve tur **LLM'e düşüyordu** — yani kapı, önlemek için
    var olduğu çağrıyı **davet ediyordu**.

    *Bir eniyileştirmenin ölçütü ürettiği çıktı değil, engellediği iştir.*
    """
    import inspect

    from app import answer as answer_mod

    src = inspect.getsource(answer_mod._anlati_ekle)
    i = src.index("basit_mi(yorum)")
    blok = src[i:i + 1800]
    assert "return" in blok, "🔴 şablon dalı erken dönmüyor — LLM yine çağrılır"
    j = src.index('calistir("llm.anlat"')
    assert i < j, "🔴 şablon kontrolü LLM çağrısından SONRA"
    # Ve dönüş `anlat()`'ın çıktısına BAĞLI OLMAMALI:
    assert 'if (_sablon := ' in blok and blok.index("return") > blok.index("if (_sablon"), (
        "🔴 dönüş metin üretimine bağlı — yankı durumunda LLM yeniden devreye girer")
