"""FAZ D3 — `_syn_hit` altdizi körlüğü: `_uncovered`'ın kardeşi.

Faz 0.4 `_uncovered`'ın "herhangi bir konumda altdizi" kusurunu düzeltmişti (`kar ⊂ ankara`,
`fire ⊂ firesiz`). **Kardeşi `_syn_hit` aynı hastalıkla kaldı** ve MIMARI §6.1'de açıkça
*"henüz düzeltilmedi — `_uncovered`'dan daha geniş etki alanı var (her boyut/ölçü eşleşmesi
ondan geçiyor)"* diye kayıtlıydı.

## Neden `route()` üstünde görünmüyordu

Ölçüldü (2 Ağustos 2026): `route("aylık ciro önceki ay ile kıyasla")` → `None`. Kusur orada
**kapsam kapısı tarafından maskeleniyordu** — `"kiyasla"` hiçbir tanınan parçanın çekimi
olmadığı için `_coverage_ok` zaten çekiliyordu. Yani `route()`'a bakarak "sorun yok" demek
mümkündü.

## Asıl zarar yüzeyi: kapsam kapısından GEÇMEYEN takip yolları

`deterministic_refine` · `cross_cube_add` · `cross_cube_dim_switch` — hiçbiri `_coverage_ok`
çağırmaz (çağıramaz da: takip sorusu doğası gereği eksik cümledir, "aylık" tek başına
kapsanamaz). Ölçülen sonuç:

| Takip sorusu | Eklenen boyut | Kök |
|---|---|---|
| `"kıyaslama yap"` | `ik.yas_grubu` | `yas` ⊂ `kıyaslama` |
| `"önceki ay ile kıyasla"` | `ik.donem` + `ik.yas_grubu` | `ay` ⊂ …, `yas` ⊂ `kıyasla` |
| `"neden arttı"` | `bakim.mudahale_eden` | `eden` ⊂ `neden` |
| `"detay ver"` | `ik.donem` | `ay` ⊂ `detay` |

Fazla bir GROUP BY kolonu **her hücredeki sayıyı değiştirir** ve cevap `source="cube"`
rozetiyle gelir. Faz 0.5'in `_match_dims` tahkimi bunu kurtaramaz — tahkim *hangi eşleşme
kazanır* sorusunu çözer, *bu eşleşme gerçek mi* sorusunu değil.

## Düzeltme

`_covers`'ın disiplini `_syn_hit`'e taşınır: sinonim **kelime başında** başlamalı ve arkasında
kalan kısım ya boş ya **geçerli bir Türkçe ek zinciri** olmalı (olumsuzluk eki değil). Aynı
mekanizma, tek kaynak — iki fonksiyon `_ek_gecerli()`'yi paylaşır.

Ölçülen kapsam: demo kataloğunda 449 boyut sinoniminin **64'ü** ≤4 harfli ve tam-kelime
işaretsizdi; bunlardan 5'i gerçek Türkçe dolgu kelimelerinde sahte eşleşme üretiyordu.
"""

from __future__ import annotations

import pytest

from app.cube_router import (
    _cube_meta,
    _match_dims,
    _match_measure,
    _norm,
    _syn_hit,
    deterministic_refine,
    route,
)

# --- ASIL KAPI: kelime başı çapası -----------------------------------------------

@pytest.mark.parametrize("syn,kelime", [
    ("yas", "kiyasla"),        # ik.yas_grubu — MIMARI §6.1'de adı geçen vaka
    ("yas", "kiyaslama"),
    ("eden", "neden"),         # bakim.mudahale_eden
    ("ay", "detay"),           # ik.donem
    ("ay", "ayrica"),
    ("hat", "muhattap"),
    ("cari", "mucari"),
])
def test_sinonim_KELIME_ORTASINDA_eslesmez(syn, kelime):
    """Türkçe EKLEMELİ bir dildir: ek SONA gelir. Kelimenin ortasında/sonunda denk gelen
    bir altdizi çekim değil, TESADÜFTÜR."""
    assert not _syn_hit(kelime, syn), f"'{syn}' ⊂ '{kelime}' sahte eşleşmesi sürüyor"


@pytest.mark.parametrize("syn,kelime", [
    ("yas", "yas"),
    ("yas", "yasi"),           # iyelik
    ("renk", "renklerine"),    # ler+i+ne — Faz 0.4'te uzunluk sezgisini düşüren vaka
    ("verim", "verimliligi"),
    ("makine", "makinelerin"),
    ("oee", "oeeyi"),
    ("bolum", "bolumlere"),
    ("fire orani", "fire orani"),
    ("fire orani", "fire oranini"),   # ÇOK KELİMELİ sinonim + son kelimede çekim
])
def test_MESRU_cekim_korunur(syn, kelime):
    """Düzeltme, gerçek çekimleri kesmemeli — Faz 0.4'te iki tasarım denemesi tam burada
    düşmüştü."""
    assert _syn_hit(kelime, syn), f"'{syn}' → '{kelime}' meşru çekimi kayboldu"


@pytest.mark.parametrize("syn,kelime", [
    ("fire", "firesiz"),
    ("sapma", "sapmasiz"),
    ("reddedil", "reddedilmeyen"),
])
def test_OLUMSUZLUK_eki_eslesmez(syn, kelime):
    """`-sIz` / `-mAyAn` anlamı TERSİNE çevirir. "firesiz partiler" fire ölçüsüne eşleşirse
    sorulanın tam tersi metrik döner — sistemin üretebileceği en kötü hata sınıfı."""
    assert not _syn_hit(kelime, syn)


def test_TAM_KELIME_isareti_bozulmadi():
    """Sonu `!` olan sinonim zaten tam-kelime eşleşiyordu; davranışı aynen korunmalı."""
    assert _syn_hit("kar marji", "kar!")
    assert not _syn_hit("karsilastir", "kar!")
    assert not _syn_hit("kargo maliyeti", "kar!")


def test_kelime_basi_NOKTALAMADAN_sonra_da_gecerli():
    """`_norm` her zaman boşlukla ayırmaz; virgül/parantez sonrası da kelime başıdır."""
    assert _syn_hit("ciro, renk bazinda", "renk")
    assert _syn_hit("(makine) duruslari", "makine")


# --- Uçtan uca: kapsam kapısından geçmeyen takip yolları -------------------------

@pytest.mark.parametrize("soru,cube,istenmeyen", [
    ("onceki ay ile kiyasla", "ik", "yas_grubu"),
    ("kiyaslama yap", "ik", "yas_grubu"),
    ("detay ver", "ik", "donem"),
    ("neden artti", "bakim", "mudahale_eden"),
])
def test_takip_sorusu_ALAKASIZ_boyut_eklemez(schema, soru, cube, istenmeyen):
    """ASIL ZARAR. Bu yollar `_coverage_ok`'tan GEÇMEZ (takip sorusu eksik cümledir),
    dolayısıyla `_syn_hit` tek savunmadır."""
    meta = _cube_meta(schema, cube)
    assert meta is not None
    assert istenmeyen not in _match_dims(_norm(soru), meta)


def test_deterministic_refine_REGRESYONU(schema):
    """`deterministic_refine("kıyaslama yap")` → `['yas_grubu']` üretiyordu: kullanıcının
    hiç istemediği bir GROUP BY, `source="cube"` rozetiyle."""
    prev = {"cube": "ik", "measures": ["ort_kidem_yil"], "dimensions": [], "filters": []}
    out = deterministic_refine(prev, _norm("kıyaslama yap"), schema)
    assert "yas_grubu" not in ((out or {}).get("dimensions") or [])


# --- Bozulmadığının kanıtı: çalışan yollar aynen çalışmalı ----------------------

@pytest.mark.parametrize("soru,cube,dim", [
    ("yaş grubu bazında fire", "parti", "yas_grubu"),
    ("bölüm bazında oee bu yıl", "oee", "bolum"),
])
def test_MESRU_yollar_bozulmadi(schema, soru, cube, dim):
    r = route(soru, schema)
    cq = (r or {}).get("cube_query") or {}
    assert cq.get("cube") == cube and dim in (cq.get("dimensions") or [])


def test_olcu_eslesmesi_de_ayni_disipline_tabi(schema):
    """`_match_measure` de `_syn_hit` üstünde çalışır — aynı korumayı almalı."""
    parti = _cube_meta(schema, "parti")
    assert _match_measure(_norm("firesiz partilerin cirosu"), parti)[0] != "toplam_fire_kg"
