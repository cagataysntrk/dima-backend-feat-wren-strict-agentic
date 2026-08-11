"""🔴 `§F7` — **KAPSAM DIŞI BİR SORUDA KULLANICI BİR PLANLAYICI İZİ OKUYORDU.**

## F7'nin özü ZATEN TESLİM EDİLMİŞ — ölçüldü

Rapor `F7`: *«Kapsamı İLAN ET — yaşayanların hepsinde yazılı kapsam reddi var,
ölenlerin hiçbirinde yok.»* Canlı curl (2026-08-11) bunu **karşılanmış** buldu:

    «gelecek ay ciro tahmini»
      → Geleceğe dönük tahmin (forecast) **v1'de yok** — ve bu bir eksiklik değil,
        bilinçli bir karar… **Yapabildiğim:** geçmiş eğilimi gösterebilirim…
      + üç devam chip'i

`app/yetenek.py`'nin **üç kutusu** (`anlamadim` · `yapamiyorum` · `yapmiyorum`) tam da
raporun istediği ayrımı yapıyor: *«bir sınırı bir eksiklik gibi sunmak, kullanıcının
zamanını çalar.»* — oturumun **yirmi birinci** «yazılmış ve bağlı» vakası.

## 🔴 AMA BİR YOL KAÇAKTI

    «hava durumu nasıl»   (kataloğun TAMAMEN dışında)
      → source=cube+llm · rows=0 · cube=None
      → note: «**Bu cevap 1 adımda üretildi:** 1. **ANLAT** — bulguları cümleye
                çevirir — YALNIZ son adım olabilir (`kaynaklar`=``)»

Kullanıcı sorusunun kapsam dışı olduğunu öğrenmedi; **bir geliştirici iz satırı** okudu.

## Kök: BOŞ bir referans listesi sessizce geçiyordu

`plan_kosucu.dogrula` referans alanlarını **listeyi gezerek** denetliyor. `kaynaklar=[]`
için döngü **hiç dönmez** → hiçbir denetim çalışmaz → plan geçerli sayılır → makbuz
basılır. Oysa fonksiyonun kendi cümlesi zaten yazıyordu:

> *«bir anlatı, anlatacağı bulgulardan önce yazılamaz»*

Hiç bulgusu **olmayan** bir anlatı, o ihlalin en saf hâlidir — konum değil **varlık**
sorunu. Ve `plan_kosucu`'nun ikiz teşhisi de aynı sınıfı adlandırıyor: *«Boş bir sonuç
bir cevap değildir; makbuzlu boş bir sonuç ise bir…»*

⚠ Karar **çözmek değil reddetmek**: red gerekçesi garsona döner
(`plan_garson.ONARIM_YONERGESI`), plan yeniden yazılır; onarım da tükenirse **kapsam
beyanı** konuşur (`yetenek.kapsam_disi`). *Merdivenin kendi onarım yolu budur.*
"""

from __future__ import annotations

import pytest

from app.plan_kosucu import PlanHatasi, dogrula


def test_BOS_KAYNAKLI_anlati_REDDEDILIR():
    """🔴 Kusurun ta kendisi — ölçümden önce bu plan **geçiyordu**."""
    with pytest.raises(PlanHatasi) as e:
        dogrula({"adimlar": [{"fiil": "ANLAT", "kaynaklar": []}]})
    assert "boş" in str(e.value).lower()
    assert "anlat" in str(e.value).lower()


def test_DOLU_KAYNAKLI_anlati_GECER():
    """⚠ Kapsam kontrolü: düzeltme çalışan planları kesmemeli."""
    plan = {"adimlar": [
        {"fiil": "SORGU", "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}},
        {"fiil": "ANLAT", "kaynaklar": ["$1"]},
    ]}
    assert dogrula(plan)


def test_BOS_LISTE_her_referans_alaninda_REDDEDILIR():
    """Kural `ANLAT`a özel değil: **her** referans alanı boş olamaz — biri düzeltilip
    kardeşi unutulursa bu depoda *«kimlik asimetrisi»* denen kusur doğar."""
    with pytest.raises(PlanHatasi):
        dogrula({"adimlar": [
            {"fiil": "SORGU", "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}},
            {"fiil": "SIRALA", "kaynak": []},
        ]})


def test_BOS_PLAN_zaten_reddediliyordu():
    """Var olan güvence bozulmadı."""
    with pytest.raises(PlanHatasi):
        dogrula({"adimlar": []})


def test_ANLAT_SON_ADIM_kurali_KORUNDU():
    """Konum kuralı ile varlık kuralı **ayrı** iki denetimdir; ikincisi birincisini
    gölgelememeli."""
    with pytest.raises(PlanHatasi) as e:
        dogrula({"adimlar": [
            {"fiil": "ANLAT", "kaynaklar": ["$1"]},
            {"fiil": "SORGU", "cube_query": {"cube": "parti", "measures": ["toplam_ciro"]}},
        ]})
    assert "SON adım" in str(e.value)


# --- F7'nin ÖZÜ: kapsam beyanı hâlâ çalışıyor mu --------------------------------

def test_KAPSAM_BEYANI_ne_YAPABILDIGINI_de_soyler(client):
    """🔴 Raporun F7 şartı: *«yaşayanların hepsinde YAZILI kapsam reddi var»* — ve
    `contribution.py`'nin kendi cümlesi: *«Yapamam» bir cevap değildir; «şunu yapamam
    ama şunu biliyorum» bir cevaptır.*"""
    from tests.conftest import ask
    d = ask(client, "gelecek ay ciro tahmini")
    n = (d.get("note") or "") + (d.get("answer") or "")
    assert "v1'de yok" in n or "yapamıyorum" in n or "bilinçli bir karar" in n, n[:200]
    assert "Yapabildiğim" in n, "sınır söylendi ama YAPABİLDİĞİ söylenmedi"
