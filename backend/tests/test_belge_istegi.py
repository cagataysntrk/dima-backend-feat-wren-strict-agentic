"""🔴🔴 `§RG` — **BİR BELGE, TEK FİŞLE KARŞILANAMAZ.**

## Ölçülen kusur (curl, 2026-08-10 · beş koşum, aynı soru)

    «son 2 yıl satış raporu hazırla»
      SORGU,SORGU,RAPOR              → 2 blok   ✅
      (plan YOK)                     → rapor YOK 🔴
      SORGU×3,RAPOR                  → 3 blok   ✅
      SORGU×3,RAPOR                  → 3 blok   ✅
      SORGU×4,RAPOR                  → 4 blok   ✅

**5'te 4.** Bir koşumda route/garson tek fişle cevapladı ve orkestratör sustu
(*«route zaten cevapladı → boşluk YOK»*). Kullanıcı bir **belge** istedi, bir **tablo**
aldı — ve hangisini alacağı **modelin o anki tercihine** kalmıştı.

🔴 Oysa bir rapor **tanımı gereği** çok bölümlüdür; tek bir sorgu onu karşılayamaz.
Merdivenin kendi kuralı bunu zaten söylüyor: *«tek fişte olmuyorsa orkestre eder»*.

## Yüklem bir SÖZLÜK değil, bir YETENEK LİSTESİ

Aranan şey bir Türkçe kelime değil, **bu sistemin ürettiği teslimat türlerinin adı** —
`plan_semasi.FIILLER`'in içinde yazılı. `simge.sahipler`'in katalog kimliklerine,
`§KD`'nin boyut adlarına bakması gibi. ADR-0008'in yasakladığı **açık uçlu sözlük**
değildir: küme `FIILLER` kadar kapalıdır.

*Bir teslimat türünü tanımayan sistem, onu ancak tesadüfen üretir.*
"""

from app import plan_semasi as ps


def test_RAPOR_ISTEGI_TANINIR():
    """🔴 **Kapının kalbi** — ölçülen sorunun kendisi."""
    assert ps.belge_istegi("son 2 yıl satış raporu hazırla") == "RAPOR"


def test_PANO_ISTEGI_TANINIR():
    assert ps.belge_istegi("bana bir satış panosu oluştur") == "PANO"


def test_CEKIM_EKLERI_GECER():
    """⚠ `_syn_hit` çağrılır (yeniden yazılmaz): kelime başı + geçerli ek zinciri
    disiplini bütün depoda aynıdır."""
    for q in ("raporu hazırla", "raporunu çıkar", "panoyu kur", "panosunu oluştur"):
        assert ps.belge_istegi(q) is not None, q


def test_ALAKASIZ_SORU_BELGE_ISTEMEZ():
    """🔴🔴 **Yanlış-pozitif kapısı.** Sıradan bir veri sorusu orkestratöre zorlanmamalı —
    zorlanırsa her soru çok adımlı bir plana döner ve deterministik yol ölür."""
    for q in ("bu yıl toplam ciro", "makine bazında oee", "en çok fire veren hat"):
        assert ps.belge_istegi(q) is None, q


def test_BENZER_KELIME_YAKALANMAZ():
    """⚠ `raportaj` bir teslimat türü değildir; ek zinciri disiplini onu eler."""
    assert ps.belge_istegi("raportaj tekniği nedir") is None


def test_KUME_FIILLERLE_TUTARLI():
    """🔴 `KAT-1` — belge fiilleri **bu dosyanın kendi fiilleridir**. İkinci bir liste
    yazmak, bir gün yalnız birini güncellemek demekti.
    *Bir yüklemin sözlüğü, sistemin kendi yetenek listesinden başkası olamaz.*"""
    assert set(ps.BELGE_FIILLERI) <= set(ps.FIILLER)


def test_BOS_SORU_SESSIZ():
    assert ps.belge_istegi("") is None and ps.belge_istegi(None) is None
