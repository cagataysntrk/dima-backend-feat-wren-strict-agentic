"""🔴🔴 KÖK-2 + KÖK-3 — **UYUM KAPISI** ve **BEYANLI KISMİ CEVAP**.

## Ölçülen kusur

`route()` bir `CubeQuery` üretiyor ama sorudaki **niyet işaretinin** sorguda karşılığı
olduğu hiçbir yerde denetlenmiyordu. `ocak ve haziran ciro karşılaştır` → Ocak–Haziran
**toplamı**, ve `source=cube` rozetiyle — yani *"kanıtlanmış yol"* damgasıyla.

## 🔴 Ölçüt ÜÇ KEZ düzeltildi — hepsi yanlış-pozitif ölçümüyle

| tur | hedef | meşru soruda bozulan | kök neden |
|---|---|---|---|
| 1 | 5/5 | **2/6** | `route()` bir **sarmalayıcı** döndürüyor; `dimensions` doğrudan okundu → her kırılımlı soru ihlal verdi |
| 2 | 4/5 | 0/6 | `_TOPN_CUE` `son`u içeriyor → *"son 3 ay"* üstünlük sanıldı; düzeltilince `son 3 ay ve son 6 ay` hedefi kaçtı |
| 3 | 5/5 | **10/525** | `_cok_donem` göreli aralığı saymıyordu; ve `kur` cube'unun ölçü ADI *"en yüksek kur"* |
| **4** | 🟢 **5/5** | 🟢 **0/525** | ipucu bir **ölçü adının içindeyse** ipucu değildir |

*Bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*
"""

from __future__ import annotations

import pytest

from app.cube_router import route
from app.uyum import denetle, kismi_cevap_notu

#: Raporun ⊙ KAPI satırındaki beş hedef — **hiçbiri tek birleşik sayı döndürmemeli**.
HEDEFLER = [
    "mart cirosunu subata gore kiyasla",
    "ocak ve haziran ciro karsilastir",
    "2025 ve 2026 ciro kiyasla",
    "son 3 ay ve son 6 ay ciro",
    "ciro degisimi son 6 ay",
]

#: Raporun *"ve bugün doğru çalışanlar bozulmasın"* şartı.
CALISANLAR = [
    "ciro en yuksek 5 makine",
    "bu yil makine bazinda oee",
    "bu yil toplam ciro",
    "mart ayinda fire orani",
    "makine bazinda fire bu yil",
    "gecen yil toplam uretim",
]


def _cm(schema, cq):
    ad = (cq.get("cube_query") or {}).get("cube")
    return next((c for c in schema["cubes"] if c["name"] == ad), None)


@pytest.mark.parametrize("q", HEDEFLER)
def test_HEDEF_SESSIZCE_GECMIYOR(q, schema):
    """🔴 **ASIL KAPI.** Beşinin de ya `route()` reddetmeli ya da **ihlal etiketi**
    almalı. Sessizce tek bir sayı dönmesi kabul edilemez."""
    cq = route(q, schema)
    if cq is None:
        return                      # route zaten reddetti — dürüst ret, kabul
    ihlaller = denetle(q, cq, _cm(schema, cq))
    assert ihlaller, f"🔴 «{q}» sessizce cevaplandı — niyet sorguya taşınmadı"


@pytest.mark.parametrize("q", CALISANLAR)
def test_CALISAN_SORU_BOZULMUYOR(q, schema):
    """🔴 Raporun kendi şartı: *"bugün doğru çalışanlar bozulmasın"*.

    ⚠ Bu, KÖK-2'nin **kapsam daraltma riskinin** kapısıdır ve KÖK-3'ün var olma sebebi."""
    cq = route(q, schema)
    if cq is None:
        pytest.skip(f"⊘ route çözemedi: {q}")
    assert not denetle(q, cq, _cm(schema, cq)), f"🔴 «{q}» yanlışlıkla etiketlendi"


def test_GENIS_YANLIS_POZITIF_SIFIR(schema):
    """🔴 **Bu dosyanın en pahalı kapısı** — katalogdan üretilmiş meşru sorular.

    Ölçüldü: 525 `route()`-çözülür soruda **0** ihlal. Bu sayı bir hedef değil bir
    **taban**: kapı genişletildiğinde burası önce kırmızı verir."""
    sorular = []
    for c in schema["cubes"]:
        for m, syns in list((c.get("measure_synonyms") or {}).items())[:5]:
            t = (syns or [m])[0].removesuffix("!")
            for k in ("bu yıl {t}", "geçen ay {t}", "{t} bu yıl ne kadar",
                      "mart ayında {t}", "2025 yılında {t}"):
                sorular.append(k.format(t=t))
            dims = (c.get("dimensions") or [])[:1]
            if dims:
                sorular.append(f"bu yıl {dims[0]} bazında {t}")

    kotu = []
    cozulen = 0
    for q in sorular:
        cq = route(q, schema)
        if not cq:
            continue
        cozulen += 1
        ih = denetle(q, cq, _cm(schema, cq))
        if ih:
            kotu.append(f"{[i.isaret for i in ih]} ← {q}")
    assert cozulen > 300, f"⊘ ölçüm tabanı çöktü: yalnız {cozulen} soru çözüldü"
    assert not kotu, ("🔴 meşru soruda ihlal:\n  " + "\n  ".join(kotu[:12])
                      + f"\n  … toplam {len(kotu)}/{cozulen}")


# ═══════════════════════════════════════════════════════════════════════════════
# ÖLÇÜLEN ÜÇ YANLIŞ-POZİTİF — her biri kendi kapısıyla kilitlendi
# ═══════════════════════════════════════════════════════════════════════════════

def test_SARMALAYICI_OKUNUYOR(schema):
    """🔴 `route()` `{cube_query: {...}, order, limit}` döndürür. İlk yazımda `dimensions`
    **doğrudan** okundu ve her kırılımlı soru ihlal verdi.

    ⚠ Bu, deponun kendi defterindeki *"bir alan adını okumadan yazmak"* sınıfı — ve bir
    kapı içinde en tehlikeli hâli: kapı **kırmızı** verir ve kırmızı *"çalışıyor"* gibi
    görünür. *Bir sözleşmeyi okumadan denetleyen kapı, denetlediğini sanır.*"""
    cq = route("bu yil makine bazinda oee", schema)
    assert cq and (cq.get("cube_query") or {}).get("dimensions"), "vaka bayatlamış"
    assert not denetle("bu yil makine bazinda oee", cq, _cm(schema, cq))


def test_SON_N_AY_USTUNLUK_DEGIL(schema):
    """🔴 `_TOPN_CUE` kalıbı `son`u içerir (*"son 5 makine"* meşrudur). Ama *"son 3 ay"*
    bir **dönem edatıdır**. *Bir kalıbı ödünç almak, bağlamını da ödünç almayı gerektirir.*"""
    q = "son 3 ay toplam ciro"
    cq = route(q, schema)
    if cq is None:
        pytest.skip("⊘ route çözemedi")
    assert "ustunluk" not in [i.isaret for i in denetle(q, cq, _cm(schema, cq))]


def test_OLCU_ADINDAKI_USTUNLUK_SAYILMIYOR(schema):
    """🔴 `kur` cube'unun ölçüsü **`en yüksek kur`** diye adlandırılmış. *"bu yıl en
    yüksek kur"* sorusunda `en yüksek` bir sıralama isteği değil, **ölçünün adıdır**.

    *Bir ipucu, başka bir şeyin adının içindeyse, ipucu değildir.*"""
    sema = {"cubes": [{"name": "kur", "synonyms": ["kur"],
                       "measure_synonyms": {"en_yuksek_kur": ["en yuksek kur"]},
                       "measures": ["en_yuksek_kur"], "dimensions": []}]}
    cq = {"cube_query": {"cube": "kur", "measures": ["en_yuksek_kur"]}}
    assert not denetle("bu yil en yuksek kur", cq, sema["cubes"][0])


def test_DONEM_FILTRESI_ESIK_SANILMIYOR(schema):
    """⚠ Kapının en olası yanlış-pozitifi: her dönemli soruda `gte '2026-01-01'` filtresi
    var. Bunu bir **eşik** sanmak, katalogdaki her soruyu ihlal ederdi."""
    q = "bu yil toplam ciro"
    cq = route(q, schema)
    assert cq and not denetle(q, cq, _cm(schema, cq))


# ═══════════════════════════════════════════════════════════════════════════════
# KÖK-3 · BEYANLI KISMİ CEVAP
# ═══════════════════════════════════════════════════════════════════════════════

def test_KISMI_CEVAP_ROZETSIZ_VE_YOL_GOSTERIR(schema):
    """🔴 ADR-0008 *"yanlış cevaba güven rozeti takma"* der. Beyanlı kısmi cevap
    **rozetsizdir** — yasağı çiğnemez, **karşılar**: sayı doğrudur (küpten gelir),
    eksik olan sorunun bir **parçasıdır** ve bu **yazılır**."""
    q = "ocak ve haziran ciro karsilastir"
    cq = route(q, schema)
    if cq is None:
        pytest.skip("⊘ route reddetti")
    ihlaller = denetle(q, cq, _cm(schema, cq))
    metin = kismi_cevap_notu(ihlaller)
    assert "eksik" in metin.lower(), "🔴 eksiklik beyan edilmiyor"
    assert len(metin) > 60, "🔴 ret var, yol yok"


def test_UYUMLU_CEVAPTA_NOT_YOK():
    """⚠ Ters yön: ihlal yoksa **hiçbir şey söyleme**. Her cevaba uyarı eklemek,
    uyarıyı okunmaz yapar."""
    assert kismi_cevap_notu([]) == ""


def test_AYNI_KAYIP_IKI_KEZ_ANLATILMIYOR(schema):
    """⚠ `kıyas` ihlali yazıldıysa `çok_dönem` tekrar etmez — kullanıcıya iki ayrı
    sorun varmış gibi görünürdü."""
    q = "mart cirosunu subat ile kiyasla"
    cq = route(q, schema)
    if cq is None:
        pytest.skip("⊘ route reddetti")
    isaretler = [i.isaret for i in denetle(q, cq, _cm(schema, cq))]
    assert not ("kiyas" in isaretler and "cok_donem" in isaretler)


def test_UCTAN_UCA_EKSIK_NIYET_ALANI(client):
    """⊙ Uçtan uca: cevap **etiketli** gidiyor mu — `eksik_niyet` alanı dolu mu?"""
    from tests.conftest import ask

    d = ask(client, "ocak ve haziran ciro karşılaştır")
    if d.get("source") != "cube":
        pytest.skip("⊘ bu soru cube yolundan dönmedi")
    assert d.get("eksik_niyet"), "🔴 eksik niyet cevaba taşınmıyor"
    assert "eksik" in (d.get("note") or "").lower()
