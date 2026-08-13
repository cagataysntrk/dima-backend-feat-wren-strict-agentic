r"""🔴 `FAZ 3` — **ADAY YAN KANALININ ÖN KOŞULLARI** *(ve sıranın düzeltilmesi)*.

`FAZ 3` bir `ContextVar` yan kanalı (`_aday_var`) açıp `cube_tie_candidates`'in kendi
türetmesini bıraktırmak istiyordu. Ölçüldü (13 Ağustos 2026) ve **sıra düzeltildi**:
kanal **`FAZ 5`'ten sonra** açılır. İki ölçülmüş sebep:

## ① Kanalın YAKIN VADEDE TÜKETİCİSİ YOK — ve bu depo o hatayı BEŞ KEZ ölçtü

Planın kendi bağımlılık satırı: **`FAZ 6` 🔴 `FAZ 5`'e bağlı** (`GET /oneri` öneri
motorunun `Aday[]`'ini döndürür). Yani kanalın gerçek tüketicisi `FAZ 5` gelmeden
doğmuyor. Geriye tek aday tüketici olarak `3.6` kalıyor — ve `3.6` aşağıdaki ② yüzünden
**yapılamaz**. Tüketicisiz bir kanal 🆘 *«yazılmış ama bağlanmamış»*tır; bu depoda o
teşhis **beş kez** ölçüldü.

⊙ Bu bir erteleme değil bir **sıra düzeltmesi**: `FAZ 5` → `FAZ 3`+`FAZ 6` **birlikte**,
kanal **tüketicisiyle doğsun**.

## ② `3.6` İKİ KASITLI TANIMI BİRLEŞTİRİRDİ — `FAZ 2.2` ile aynı sınıf hata

*«Beraberlik»* bu kod tabanında **iki farklı şey** demektir ve ikisi de yazılıdır:

| | nerede | ölçüt |
|---|---|---|
| **kıran** | `_match_cube` | `_longest_syn_hit` üzerinde **marj ≥ 4 harf** |
| **tanımlayan** | `cube_tie_candidates` | `(harf, ölçü-eşleşme)` ikilisinde **TAM EŞİTLİK** |

Fark gerçektir: 2 harflik bir fark `_match_cube` için *«kıramadım»*, ama
`cube_tie_candidates` için *«eşit değil»* → chip **basılmaz**. Ve bu **kasıtlıdır** —
fonksiyonun kendi cümlesi: *«kanıt eşit değil → orta güven → Intent-JSON'ın işi.»*

`3.6` (*«`cube_tie_candidates` `adaylar()`'ı okusun, kendi türetmesini bıraksın»*) bu
ayrımı **silerdi**: yakın-beraberlikler de chip'e dönüşür, garsonun işi elinden alınırdı.
Planın kendisi zaten uyarmıştı: *«`3.6` en riskli… ölçemezsen ayır ve ertele.»* Ölçüldü,
ve ölçüm **ayırmayı** söyledi ㊸.

⚠ Not: `cube_tie_candidates`'in probları ucuz değil (`_TIE_MAX_DENEME = 8`, her deneme
**tam bir `route()` koşusu**) — ama o maliyet *«hangi cube'lar eşit»*i bulmak için değil,
**ayırt eden soruyu** üretmek içindir. Yan kanal onu **ikame edemez**; ederse chip
metinsiz kalır.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

_APP = pathlib.Path(__file__).resolve().parents[1] / "app"


# ── ① PLANIN KENDİ KAPISI: `route()` imzası DOKUNULMAZ ──────────────────────

def test_route_imzasi_DEGISMEDI():
    """🔴 `FAZ 3`'ün `①` kapısı — faz gelince de geçerli kalmalı.

    Yan kanalın **bütün** gerekçesi imzayı değiştirmemekti.
    ⚠ ㊱ **Bu yüklem ilk yazılışında uydurma bir ad taşıyordu** (`q`); ölçülen imza
    `route(question, schema, liste_kirilimi)`. Beklenti koda göre düzeltildi ③.
    """
    from app.cube_router import route

    par = list(inspect.signature(route).parameters)
    assert par == ["question", "schema", "liste_kirilimi"], (
        f"🔴 `route()` imzası değişti: {par} — `FAZ 3`'ün varlık sebebi imzayı "
        "değiştirmemekti; değiştiyse kanal gereksizleşir ve beş çağıran kırılır.")


# ── ② 🔴 İKİ «BERABERLİK» TANIMI KASITLI OLARAK FARKLIDIR ───────────────────

def test_iki_beraberlik_tanimi_AYRI_KALIR():
    """🔴🔴 **`3.6`'nın ⊘ gerekçesi.** Kıran **marj**la, tanımlayan **tam eşitlik**le
    çalışır. İkisi tek tanıma indirilirse yakın-beraberlikler chip'e döner ve garsonun
    işi elinden alınır (*«orta güven → Intent-JSON'ın işi»*).

    🅑 Mutasyon: `esitler` süzgeci bir marj kıyasına çevrilirse bu yüklem kırılır.
    """
    kaynak = (_APP / "cube_router.py").read_text(encoding="utf-8")
    assert "marj=4.0" in kaynak, (
        "🔴 `_match_cube`'un MARJ ölçütü kayboldu — beraberliği kıran kural değişti.")
    assert "esitler = [c for c in hits if _kanit(c) == en_iyi]" in kaynak, (
        "🔴 `cube_tie_candidates`'in TAM EŞİTLİK ölçütü kayboldu — yakın-beraberlikler "
        "artık chip'e dönüyor olabilir; garsonun işi elinden alınmış olur.")


def test_ayirt_eden_SORU_probla_uretilir_kanal_ikame_edemez():
    """⚠ `3.6`'nın ikinci yarısı: prob maliyeti *«hangi cube eşit»* için değil,
    **ayırt eden soru** için ödeniyor. Yan kanal aday listesi taşır, soru **taşımaz**.

    Bu yüklem prob bütçesinin **yerinde** olduğunu kilitler — kaldırılırsa chip
    metinsiz kalır ve `§38.4`'ün *«beyan kültürü»* değişmezi zedelenir.
    """
    from app.cube_router import _TIE_MAX_DENEME, cube_tie_candidates

    assert _TIE_MAX_DENEME == 8
    # dönüş **üçlü**dür: (cube_meta, ayırt_eden_soru, cube_query) 🅬
    kaynak = inspect.getsource(cube_tie_candidates)
    assert "list[tuple[dict, str, dict]]" in kaynak, (
        "🔴 dönüş şekli değişti — chip'in metin taşıyıp taşımadığı yeniden ölçülmeli.")


# ── ③ ㊻ ÖN KOŞUL KAPISI: KANAL TÜKETİCİSİZ DOĞMASIN ────────────────────────

def test_yan_kanal_TUKETICISIZ_ACILAMAZ():
    """🔴🔴 **Bu kapı ertelemeyi kendi kendini uygulanır kılar.**

    `_aday_var` bir gün eklenirse, **aynı demette** bir okuyan da eklenmelidir. Aksi
    hâlde depo altıncı kez 🆘 *«yazılmış ama bağlanmamış»* bir yetenek taşır — ve o
    teşhis burada **beş kez** ölçüldü.

    ⚠ ② `ast` ile sayılır: bir yorumda geçen `_aday_var` kapıyı açmaz 🅞.
    """
    agac = ast.parse((_APP / "cube_router.py").read_text(encoding="utf-8"))
    tanim = any(isinstance(d, ast.Name) and d.id == "_aday_var" and
                isinstance(d.ctx, ast.Store) for d in ast.walk(agac))
    if not tanim:
        return  # kanal henüz yok — erteleme yürürlükte, kapı sessiz
    okuyan = sum(1 for d in ast.walk(agac)
                 if isinstance(d, ast.Attribute) and d.attr == "get"
                 and isinstance(d.value, ast.Name) and d.value.id == "_aday_var")
    assert okuyan >= 1, (
        "🔴 `_aday_var` açıldı ama **hiç okunmuyor** — tüketicisiz bir kanal, bu "
        "deponun beş kez ölçtüğü «yazılmış ama bağlanmamış» hatasının altıncısıdır 🆘.")


def test_sonda_yalitimi_HALA_TEK_DEKORATOR():
    """`3.3`'ün ön koşulu: `KAT-1` gereği **iki dekoratör olmaz**. Kanal gelince
    `_sonda_reddi_korur` **genişletilecek**; bugün tekliğini kilitliyoruz ㊲."""
    kaynak = (_APP / "cube_router.py").read_text(encoding="utf-8")
    assert kaynak.count("def _sonda_") == 1, (
        "🔴 ikinci bir sonda dekoratörü doğdu — `KAT-1`: sonda yalıtımının tek sahibi "
        "olmalı, yoksa biri korunur öteki ezilir (`§41.2` sonda tuzağı).")
