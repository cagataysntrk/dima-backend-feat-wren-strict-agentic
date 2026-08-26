"""🔴 **KÖK ÇÖZÜM** — takip sorusunu bağlayan şey **ekrandaki satır**, kelime listesi değil.

## Önceki sürüm TİKELDİ

```python
_KARSILASTIRMA = ("yuksek", "dusuk", "fazla", …)   # 🔴 kelime listesi
_KARSILASTIRMA_AZAMI_KELIME = 4                     # 🔴 eşik
```

Çalışıyordu ama *"yıkama neden **geride kaldı**"* · *"3. vardiya neden **zayıf**"* ·
*"bu aşama neden **sorunlu**"* yine düşerdi — ve her biri listeye bir kelime daha
eklettirirdi (`ADR-0008`).

## Kök: sorunun ekrandaki bir SATIRI adlandırması

| soru | bağ |
|---|---|
| `yıkama neden yüksek` | `yıkama` ∈ mevcut kırılımın **değerleri** ✅ |
| `yıkama neden geride kaldı` | aynı ✅ — **liste büyümeden** |
| `fire oranı neden yüksek olur genel olarak` | `fire oranı` bir **ölçü adı** → bağ YOK |

⊙ Bu ayrım *"genel olarak"* sorusunu **kendiliğinden** dışarıda bırakır — uzunluk eşiğine
gerek kalmaz. *Zamir "şu" der; değer HANGİSİ olduğunu söyler.*

## Sahiplik

*"Ekranda ne var"* sorusunun sahibi **bağlam katmanı** (`app/context.py`), sınıflandırıcı
değil (`KAT-1`). `followup.sinifla` değerleri **alır**, okumaz.
"""

from __future__ import annotations

import pytest

from app import context as ctx
from app import followup as fu
from app import cube_router as cr


def _cq():
    return {"cube": "parti", "measures": ["toplam_fire_kg"], "dimensions": ["asama"]}


def _sema():
    """⚠ Kaynak **katalog**, ekran değil: `AskRequest`'te `previous_result` alanı YOK —
    ilk yazım var olmayan bir alanı okuyordu ve **sessizce hiçbir şey yapıyordu**.
    *Var olmayan bir alanı okuyan kod testi de geçer; onu curl yakaladı.*"""
    return {"cubes": [{"name": "parti",
                       "dimension_values": {"asama": ["YIKAMA", "KURUTMA", "ÖN FİKSE"]}}]}


def test_CAPA_DEGERLERI_EKRANDAN_OKUNUYOR():
    d = ctx.capa_degerleri(_cq(), _sema())
    assert d and "yikama" in d and "kurutma" in d


def test_RAPOR_YOKSA_NONE():
    """`KURAL B`: çapa yoksa sınıflandırıcı bugünkü davranışına döner."""
    assert ctx.capa_degerleri(_cq(), None) is None
    assert ctx.capa_degerleri({"cube": "x"}, _sema()) is None


@pytest.mark.parametrize("soru", [
    "yıkama neden yüksek",
    "yıkama neden geride kaldı",     # 🔴 eski listede YOKTU — kök çözümün kanıtı
    "yıkama neden bu kadar sorunlu",
])
def test_EKRANDAKI_SATIRI_ANAN_SORU_TAKIPTIR(soru):
    d = ctx.capa_degerleri(_cq(), _sema())
    n = fu.sinifla(cr._norm(soru), baglam_var=True, capa_degerleri=d)
    assert n.tur == fu.TUR_NEDEN, f"🔴 {soru!r} takip sayılmadı: {n}"


def test_GENEL_SORU_YENI_KONU_KALIR():
    """⚠ Genişlemenin sınırı — ve eşiksiz sağlanıyor: `fire oranı` bir **ölçü adı**,
    ekrandaki bir satır değil."""
    d = ctx.capa_degerleri(_cq(), _sema())
    n = fu.sinifla(cr._norm("fire orani neden yuksek olur genel olarak"),
                   baglam_var=True, capa_degerleri=d)
    assert n.tur != fu.TUR_NEDEN, f"🔴 genel soru takip sanıldı: {n}"


def _sema_tireli():
    """Katalog değeri **tireli** — gerçek demo katalogda `makine` boyutunun çoğu
    değeri böyle (`RAM-1`, `RAM-2`, `RAM-3`, `ŞARDON-1`, `FERRARO SANFOR-1`)."""
    return {"cubes": [{"name": "oee",
                       "dimension_values": {"makine": ["RAM-3", "RAM-2", "ÖRGÜ HAT"]}}]}


def _cq_tireli():
    return {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}


@pytest.mark.parametrize("soru", [
    "ram 3 neden dusuk",     # 🔴 kullanıcı bulgusu — boşlukla yazılan tireli katalog adı
    "ram-3 neden dusuk",     # katalogla BİREBİR (tireli) — hep çalışıyordu, regresyon kilidi
])
def test_TIRELI_KATALOG_ADI_BOSLUKLA_DA_TAKIPTIR(soru):
    """🔴🔴 Kullanıcı bulgusu (2026-08-26): `RAM-3` ekrandaki raporun bir satırıyken
    *"ram 3 neden düşük"* (boşluklu, DOĞAL yazım) `capa_degerleri`'nde eşleşmiyordu —
    `_norm()` tire/boşluk ayrımını birleştirmiyor — ve tur SESSİZCE *yeni konu*
    (`kalip-yok`) sayılıyordu; `neden` hiç `kok_neden`/`contribution`'a ulaşmıyordu.
    Bu, kullanıcının "sadece ham sayı geliyor, açıklama yok" şikayetinin GERÇEK köküydü
    — `plan_tuketici._anlat`'ın HESAPLA/BAGLA düzeltmesi bile bu tur hiç
    tetiklenmediği için işe yaramıyordu."""
    d = ctx.capa_degerleri(_cq_tireli(), _sema_tireli())
    n = fu.sinifla(cr._norm(soru), baglam_var=True, capa_degerleri=d)
    assert n.tur == fu.TUR_NEDEN, f"🔴 {soru!r} takip sayılmadı: {n}"


def test_KELIME_LISTESI_SILINDI():
    """🔴 `ADR-0008`. Tikel çözümün kalıntısı kalmamalı."""
    import inspect

    # ⚠ Ölçüt **kod**, anlatı değil: kaldırılan listenin *kaydı* şerhte durmalı ve
    # duruyor. Kapı yorumları eleyip yalnız çalıştırılabilir satırlara bakar.
    # *Bir kapı, koruduğu şeyin kaydını da yasaklarsa, kararı silmiş olur.*
    src = inspect.getsource(fu)
    govde = [l for l in src.splitlines()
             if l.strip() and not l.strip().startswith(("#", '"', "*", "|", ">"))]
    assert not any("_KARSILASTIRMA" in l for l in govde), "🔴 kelime listesi geri gelmiş"
    assert "_capaya_deger" in src


def test_SINIFLANDIRICI_KATALOG_OKUMUYOR():
    """`KAT-1`: değerleri **çağıran** verir; sınıflandırıcı sonuç/katalog okumaz.

    ⚠ Ölçüt **AST** — metin taraması iki kez yanlış pozitif verdi (şerhler kararı
    anlatmak için o isimleri anmak **zorunda**). *Bir kapı, koruduğu şeyin kaydını da
    yasaklarsa, kararı silmiş olur.*"""
    import ast
    import inspect
    import textwrap

    for fn in (fu.sinifla, fu._capaya_deger):
        agac = ast.parse(textwrap.dedent(inspect.getsource(fn)))
        adlar = {n.id for n in ast.walk(agac) if isinstance(n, ast.Name)}
        adlar |= {n.attr for n in ast.walk(agac) if isinstance(n, ast.Attribute)}
        assert not (adlar & {"previous_result", "cube_query", "schema", "rows"}), (
            f"🔴 {fn.__name__} sonuç/sorgu/şema okuyor — `KAT-1`: {adlar & {'previous_result','cube_query','schema','rows'}}")
