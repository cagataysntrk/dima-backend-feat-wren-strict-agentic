"""🔴🔴 *«X BAZINDA»*'NIN **DÖRDÜNCÜ ANLAMI**: bir BİRİM / PARA BİRİMİ.

## Ölçülen kusur (canlı tur, soru 22 — 2026-08-12)

    «dolar bazında ciro»
      → cevap: **₺** 137.588.350,68
      → beyan: *«bir **KIRILIM** istedin ama sorguya bir boyut taşıyamadım»*

⊙ Kullanıcı kırılım **istemedi**; bir **para birimi** istedi. Sistem ona *söylemediği
bir şeyi söylediğini* söylüyor.

> `niyet.py`'nin bu satır için yazdığı doktrin: *«Yanlış bir beyan, sessizlikten
> kötüdür: sistem kullanıcıya onun söylemediği bir şeyi söylediğini söylüyor — ve bu,
> güvenin en hızlı tükendiği yerdir.»*

⚠ `göre`/`bazında` aşırı-yüklenmesi bu depoda **üç kez** ısırmıştı (kırılım ·
granülerlik · dönem-aralığı). Bu **dördüncüsü**.

## Ayrım YAPISAL — kelime listesi değil, KATALOG

Ölçüldü (tüm küpler taranarak):

| soru | boyut adayı | «kırılım istendi» doğru mu |
|---|---|---|
| *«dolar bazında ciro»* | **[]** | 🔴 hayır |
| *«euro bazında ciro»* | **[]** | 🔴 hayır |
| *«makine bazında ciro»* | `['makine']` | ✅ evet |
| *«departman bazında ciro»* | `['bolum','departman']` | ✅ evet |

Kural: soruda kataloğun **hiçbir** küpünde boyut adayı yoksa, `bazında` bir kırılım
işareti değildir. Ölçüt kataloğun kendisi — ikinci bir tanıyıcı yazılmıyor
(`ADR-0008` · `KAT-1`).

## ⚠ Bedeli bilinerek ödeniyor

Katalogda hiç karşılığı olmayan **gerçek** bir kırılım isteği (*«şube bazında»*) artık
susar. `§101.1`: bir yanlış-pozitifin bedeli, kapattığı kusurdan ağırdır — ve bu, aynı
fonksiyondaki `gore_donem_mi` kararının birebir aynı takasıdır.

⊙ Para biriminin doğru beyan kanalı bu değil **`§YS`**'dir: *«dolar»* fişe yansımadıysa
onu garson `yok_sayilan` olarak bildirir. Bu satırın işi **kırılımdır**, birim değil.
"""

from __future__ import annotations

import pytest

from app import uyum

_SEMA = {"cubes": [{"name": "parti",
                    "measures": ["toplam_ciro", "toplam_fire_kg"],
                    "dimensions": ["makine", "musteri"],
                    "time_dimensions": ["tarih"],
                    "dimension_synonyms": {"makine": ["makine", "hat"],
                                           "musteri": ["musteri", "alici"]},
                    "measure_synonyms": {"toplam_ciro": ["ciro", "hasilat"]},
                    "synonyms": ["parti", "uretim"]}]}
_CM = _SEMA["cubes"][0]
_CQ = {"cube_query": {"cube": "parti", "measures": ["toplam_ciro"],
                      "dimensions": [], "filters": []}}


def _isaretler(soru: str) -> list[str]:
    return [i.isaret for i in uyum.denetle(soru, _CQ, _CM, _SEMA)]


@pytest.mark.parametrize("soru", ["dolar bazında ciro", "euro bazında ciro",
                                  "dolar bazlı ciro"])
def test_PARA_BIRIMI_KIRILIM_SANILMAZ(soru):
    """🔴 Kusurun ta kendisi: katalogda boyut adayı yoksa `bazında` kırılım değildir."""
    assert "kirilim" not in _isaretler(soru), (
        f"🔴 «{soru}» için hâlâ *«kırılım istedin»* deniyor — kullanıcı bir PARA BİRİMİ "
        "istedi. *Yanlış bir beyan, sessizlikten kötüdür.*")


@pytest.mark.parametrize("soru", ["makine bazında ciro", "müşteri bazında ciro",
                                  "hat bazında ciro"])
def test_GERCEK_KIRILIM_HALA_BEYAN_EDILIYOR(soru):
    """⊘ **Ön koşul — kapsam yutulmadı.** Katalogda karşılığı olan bir kırılım isteği
    taşınamadıysa beyan **kalmalı**; yoksa düzeltme, kapattığı kusurdan pahalı bir
    sessizlik açardı."""
    assert "kirilim" in _isaretler(soru), (
        f"🔴 «{soru}» gerçek bir kırılım isteği ve boyut taşınmadı — beyan SUSMAMALI. "
        "Düzeltme kapsamı yuttu.")


def test_SINONIM_de_ADAY_SAYILIR():
    """`hat` bir sinonimdir; eşleştirici onu tanıyorsa beyan konuşmalı — *bir adayı
    yalnız teknik adıyla aramak, kullanıcının kelimesini görmemektir.*"""
    assert "kirilim" in _isaretler("hat bazında fire")


def test_BOYUT_TASINDIYSA_ZATEN_SUSAR():
    """⊘ Taban: boyut cevapta varsa hiçbir koşulda konuşmaz."""
    cq = {"cube_query": {"cube": "parti", "measures": ["toplam_ciro"],
                         "dimensions": ["makine"], "filters": []}}
    assert "kirilim" not in [i.isaret for i in uyum.denetle("makine bazında ciro", cq,
                                                            _CM, _SEMA)]


def test_SEMA_YOKSA_ESKI_DAVRANIS():
    """⚠ Fail-**open**: şema okunamıyorsa daraltma uygulanmaz — yüklem eski hâline
    döner (susmaya değil, **konuşmaya**).

    *Bir ayrımın hesaplanamaması, ayrımın yokluğu anlamına gelmez.*

    ⊙ İlk yazımımda bu test tersini bekliyordu ve **kod da tersini yapıyordu**: boş
    şemada `any([])` → `False` → sessizlik. İkisi birden düzeltildi."""
    assert "kirilim" in [i.isaret for i in uyum.denetle("dolar bazında ciro", _CQ,
                                                        _CM, {"cubes": None})]
