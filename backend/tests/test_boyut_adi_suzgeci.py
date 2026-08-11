"""🔴🔴 `§DB` — **BİR BOYUTUN ADI, O BOYUTUN DEĞERİ OLAMAZ.**

## Ölçülen kusur (curl `X` turu, 2026-08-11 · X18)

    «bu yıl operatör bazında ilk seferde doğru oranı»
      garson (self-consistency %100) →
        {"dimension": "operator", "operator": "eq", "value": "Operatör"}
      §DK-2 → «Operatör» operator listesinde yok. Var olanlar: AYLİN BULUT · … (+1)
              Hangisini istersin?

`§DK-2` **doğru** davrandı — ama kullanıcı bir **kırılım** istemişti. Yani dürüst bir
red, **çıkmaz** bir red oldu: dokuz operatör adı listelendi ve sorunun kendisi cevapsız
kaldı. *Dürüst bir red bir başarı değildir.*

🔴 Kök bir dil sorunu değil bir **tür** sorunudur: hiç kimse `operator = "Operatör"` diye
süzmez. Ve kanıt katalogdadır — değer, süzdüğü boyutun **kendi adı/etiketidir**.
"""

from app import deger_capasi as dc

_SEMA = {"cubes": [{
    "name": "parti",
    "dimensions": ["operator", "musteri"],
    "dimension_labels": {"operator": "operatör", "musteri": "müşteri"},
    "dimension_synonyms": {"operator": ["operatör", "çalışan"], "musteri": ["müşteri"]},
    "dimension_values": {"operator": ["AYLİN BULUT", "MURAT DEMİR"],
                         "musteri": ["TOROS ÖRME"]},
}]}


def _cq(deger):
    return {"cube": "parti", "measures": ["ilk_seferde_tamam_yuzde"],
            "dimensions": ["operator"],
            "filters": [{"dimension": "operator", "operator": "eq", "value": deger}]}


def test_BOYUT_ADI_SUZGECI_DUSER():
    """🔴 **Kapının kalbi** — ölçülen vakanın kendisi."""
    cq = _cq("Operatör")
    b = dc.denetle(cq, _SEMA)
    assert b and b[0].boyut_adi, f"🔴 yakalanmadı: {b}"
    not_ = dc.duzelt_yerinde(cq, b)
    assert cq["filters"] == [], "🔴 süzgeç düşmedi"
    assert not_ and "kırılım" in not_


def test_TEKNIK_AD_DA_SAYILIR():
    """⚠ Etiket (`operatör`) kadar teknik ad (`operator`) da boyutun kendi adıdır."""
    cq = _cq("operator")
    assert dc.denetle(cq, _SEMA)[0].boyut_adi


def test_SINONIM_DE_SAYILIR():
    """⚠ Kaynak **katalog**: bir kelime listesi yazmak her yeni katalogda elle bakım
    isterdi (ADR-0008)."""
    cq = _cq("çalışan")
    assert dc.denetle(cq, _SEMA)[0].boyut_adi


def test_GERCEK_DEGERE_DOKUNULMAZ():
    """🔴🔴 **Yanlış-pozitif kapısı** (`§101.1`): gerçek bir operatör adı süzgeci
    **aynen** kalır — yoksa bir kusuru düzeltirken kullanıcının gerçek filtresini
    silerdik."""
    cq = _cq("MURAT DEMİR")
    b = dc.denetle(cq, _SEMA)
    assert not any(x.boyut_adi for x in b)
    dc.duzelt_yerinde(cq, b)
    assert cq["filters"], "🔴 gerçek süzgeç düştü"


def test_BASKA_BOYUTUN_ADI_SAYILMAZ():
    """⚠ Yüklem **dar**: değer, süzdüğü boyutun **kendi** adına eşit olmalı. `musteri`
    boyutunu *«operatör»* diye süzmek gerçekten anlamsız olabilir ama onu bu kapı değil
    `§DK-2` (katalogda yok → netleştirme) karşılar. *Bir yüklemi genişletmek, onun
    kanıtını zayıflatmaktır.*"""
    cq = {"cube": "parti", "measures": ["x"], "dimensions": ["musteri"],
          "filters": [{"dimension": "musteri", "operator": "eq", "value": "operatör"}]}
    assert not any(b.boyut_adi for b in dc.denetle(cq, _SEMA))


def test_BEYAN_DISLAMA_CUMLESIYLE_KARISMAZ():
    """⚠ *«Etkisiz bir dışlama»* burada **yalan** olurdu: ortada bir dışlama yok, bir
    tür karışıklığı var. *Bir beyan, ölçebildiğinden fazlasını söylediği anda bir
    varsayıma dönüşür.*"""
    cq = _cq("Operatör")
    not_ = dc.duzelt_yerinde(cq, dc.denetle(cq, _SEMA))
    assert "dışlama" not in not_
