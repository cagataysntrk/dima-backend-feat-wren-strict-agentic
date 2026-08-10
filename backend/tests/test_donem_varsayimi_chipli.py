"""🔴🔴 `§TZ` — **BEYANIN YANINDA BİR TIK OLMALI: `D3` doğruydu, YAN ETKİSİ ölçülmemişti.**

## Ölçülen kusur (curl `N+1` turu, 2026-08-10)

    «makine bazında ortalama oee»
      note        : ⏱ Dönemi çözemedim — verinin son 12 ayı alındı (01.06.2025 – 30.06.2026).
                    Başka bir dönem **YAZARSAN** onu uygularım.
      suggestions : **[]**

`D3` (`varsayilan_donem` → `beta`) ölçülmüş ve doğru bir karardı: sormak yerine
**beyanla varsaymak** kullanıcıyı cevapsız bırakmıyor. Ama netleştirme dalı ölünce onun
**chip'leri de** öldü ve düzeltme yolu bir **tıktan** bir **yazma** eylemine düştü.

## 🔴 Ve bu, BEŞ BAYAT KAPININ neyi koruduğunu gösterdi

`test_ask_golden` × 4 · `test_explain` × 2 · `test_soz_katalogu` · `test_sinir_once_konusur`
— hepsi *«Tümü chip'i olmalı»* diyordu ve **haklıydılar**. Yanlış olan tek şey, o chip'in
bir **netleştirme turunda** gelmesi gerektiği varsayımıydı.

> *Bayat bir kapı bazen yanlış cevabı değil, doğru cevabın eski adresini tutar.*

⚠ Kapılar bu yüzden **beklentilerini gevşeterek** değil, **yetenek geri verilerek**
yeşile döndü: chip yine var, yalnız artık bir cevabın **yanında** geliyor — sorunun
yerine değil.
"""

import pytest

from app import donem_capasi as dc


def _cq_varsayimli():
    """Taşıyıcıyı `varsayilan_yerinde`'nin bıraktığı biçimde kurar."""
    return {"cube": "oee", "measures": ["ort_oee"],
            "_capa_notu": ("⏱ Dönemi çözemedim — son 12 ay", dc.IZ_VARSAYILAN)}


def test_VARSAYIM_YAPILDIYSA_CHIP_GELIR():
    """🔴 **Kapının kalbi.** Beyan tek başına yetmez; düzeltme **tıklanabilir** olmalı."""
    _n, _t, chipler = dc.notu_al(_cq_varsayimli(), None, [])
    assert [c["label"] for c in chipler] == ["Bugün", "Bu hafta", "Bu ay", "Bu yıl", "Tümü"]


def test_TUMU_SECENEGI_KORUNDU():
    """🔴 Beş bayat kapının **ortak** beklentisi — yetenek geri verildi."""
    _n, _t, chipler = dc.notu_al(_cq_varsayimli(), None, [])
    assert any(c["label"] == "Tümü" and c["query"] == "tüm zamanlar" for c in chipler)


def test_NOT_VE_IZ_BOZULMADI():
    """⚠ Üçüncü dönüş bir **ek**tir: ilk ikisi birebir eski davranışını korur."""
    note, trace, _c = dc.notu_al(_cq_varsayimli(), "önceki not", ["önceki iz"])
    assert note.startswith("önceki not ⏱")
    assert trace == ["önceki iz", dc.IZ_VARSAYILAN]


def test_SUREKLILIK_IZINDE_CHIP_YOK():
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    Taşıyıcının öteki kullanıcısı (`KÖK-4`, önceki turdan taşınan dönem) bir **varsayım
    değil** bir **süreklilik**tir. Orada düzeltme önerisi, kullanıcının **kendi seçtiği**
    dönemi geri almasını önerirdi — yani yardım değil gürültü."""
    cq = {"cube": "oee", "_capa_notu": ("önceki turdan taşındı", dc.IZ)}
    _n, _t, chipler = dc.notu_al(cq, None, [])
    assert chipler == []


def test_TASIYICI_YOKSA_SESSIZ():
    """Varsayım yoksa üç dönüş de bugünkü hâlinde (`KURAL B`)."""
    assert dc.notu_al({"cube": "oee"}, "n", ["i"]) == ("n", ["i"], [])


def test_TASIYICI_BOSALTILIR():
    """*Bir taşıyıcı alan, taşıdığı yere varınca boşaltılmalıdır* — chip eklemek bunu
    değiştirmez."""
    cq = _cq_varsayimli()
    dc.notu_al(cq, None, [])
    assert "_capa_notu" not in cq


def test_CHIP_LISTESI_KOPYA_DONER():
    """⚠ Çağıran listeyi düzenlerse modül sabiti bozulmamalı — bir sonraki istek
    eksik chip görürdü."""
    _n, _t, c1 = dc.notu_al(_cq_varsayimli(), None, [])
    c1[0]["label"] = "BOZULDU"
    _n2, _t2, c2 = dc.notu_al(_cq_varsayimli(), None, [])
    assert c2[0]["label"] == "Bugün"


def test_NETLESTIRME_DALI_AYNI_LISTEYI_OKUR():
    """🔴 `KAT-1` — liste iki yerde yazılıydı ve `D3` yalnız birini besliyordu.
    *Aynı menüyü iki yerde tutmak, bir gün yalnız birini güncellemektir.*"""
    pytest.importorskip("app.routers.ask")
    from app.routers.ask import _PERIOD_SUGGESTIONS

    assert _PERIOD_SUGGESTIONS == [dict(x) for x in dc.DONEM_SECENEKLERI]
