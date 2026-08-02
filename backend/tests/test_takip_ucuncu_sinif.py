"""FAZ G1 — takip sorusunun ÜÇÜNCÜ sınıfı: "cevap üstünde konuşma".

## Ölçülen boşluk (2 Ağustos 2026, canlı `/ask` üzerinden)

Bir `parti` raporu üstünde sorulan altı sorunun **altısı da** duvara çarpıyordu:

    "bu neden böyle?"          → "Bu takip mesajını önceki raporla ilişkilendiremedim."
    "normal mi?"               → aynı ölü uç
    "ne yapmalıyız?"           → aynı ölü uç
    "şu düşüş ne?"             → "«dusus» kısmını anlayamadım"
    "bunu nasıl iyileştiririz?"→ "«bunu» yerine «gunu» mi demek istedin?"   ← anlamsız
    "sence iyi mi?"            → aynı ölü uç

Çünkü takip soruları **iki** sınıfa ayrılıyordu: sorguyu düzenle, ya da yeni ham SQL yaz.
*"Verdiğin cevap hakkında konuş"* diye bir sınıf yoktu.

## Bu sınıfın tanımı ve neden Discovery'ye DÜŞMEMELİ

Konuşma sınıfı **yeni bir cevap üretmez, var olanı açar**. Discovery'ye düşerse bağlamsız
ham SQL yazılır ve ölü tablo döner — ölçülen sorun tam olarak budur. Bir soru *"bu cevap
hakkında"* ise cevabı zaten elimizdedir; yeni SQL yazmak yanlış araçtır.
"""

from __future__ import annotations

import pytest

from app import followup as fu


def _s(soru: str, baglam_var: bool = True):
    return fu.sinifla(soru, baglam_var=baglam_var)


# --- ASIL KAPI: ölçülen altı soru artık konuşma sınıfında -----------------------

@pytest.mark.parametrize("soru,tur", [
    ("bu neden böyle?", fu.TUR_NEDEN),
    ("normal mi?", fu.TUR_NORMAL),
    ("ne yapmalıyız?", fu.TUR_NE_YAPMALI),
    ("şu düşüş ne?", fu.TUR_ISARET),
    ("bunu nasıl iyileştiririz?", fu.TUR_NE_YAPMALI),
    ("sence iyi mi?", fu.TUR_NORMAL),
])
def test_OLCULEN_ALTI_soru_konusma_sinifinda(soru, tur):
    """Bu altı soru canlı sistemde ölü uca çarpıyordu — ölçüldü, kayda geçti."""
    n = _s(soru)
    assert n.konusma, f"{soru!r} hâlâ {n.sinif!r} sınıfında (kural={n.kural})"
    assert n.tur == tur, f"{soru!r} → {n.tur} (beklenen {tur})"
    assert n.kanit, "hangi kalıbın eşleştiği kaydedilmemiş"


@pytest.mark.parametrize("soru", [
    "niçin arttı?", "niye?", "sebebi ne?", "bu nereden geliyor?",
    "bu sonuç olağan mı?", "endişelenmeli miyiz?", "burada bir sorun var mı?",
    "ne önerirsin?", "hangi aksiyonu almalıyız?", "bunu nasıl azaltırız?",
    "şu sıçrama ne?", "buradaki anomali ne?",
])
def test_konusma_dagarcigi(soru):
    assert _s(soru).konusma, f"{soru!r} konuşma sınıfına girmedi"


# --- YAPISAL ÖNCELİĞİ ------------------------------------------------------------

@pytest.mark.parametrize("soru", [
    "aylık", "makine bazında", "en yüksek 5", "renk kırılımı",
    "grafik ver", "çeyreklik göster", "sırala",
])
def test_yapisal_duzenleme_KONUSMA_degil(soru):
    """Bunlar sorguyu DEĞİŞTİRİR — konuşma sınıfına girerse kullanıcı beklediği yeni
    sayıları alamaz ve bunun yerine eski sonucun yorumunu görür."""
    assert _s(soru).sinif == fu.SINIF_YAPISAL, soru


def test_KARISIK_soruda_yapisal_KAZANIR():
    """"aylık neden düştü?" hem düzenleme hem konuşma gibi görünür. Öncelik yapısaldadır:
    kullanıcı yeni sayılar bekliyorsa önce onları vermek gerekir — konuşma bir sonraki
    turda hâlâ mümkündür, ama YANLIŞ SAYI geri alınamaz."""
    n = _s("aylık neden düştü?")
    assert n.sinif == fu.SINIF_YAPISAL and n.kanit == "aylik"


# --- BAĞLAM KAPISI ---------------------------------------------------------------

def test_baglam_YOKSA_konusma_TANIMSIZ():
    """Konuşulacak bir cevap yoksa "cevap üstünde konuşma" tanımsızdır. Bu kapı olmadan
    "bu neden böyle?" diye BAŞLAYAN bir oturum konuşma sınıfına düşer ve çapalanacağı
    bir makbuz bulamaz."""
    n = _s("bu neden böyle?", baglam_var=False)
    assert n.sinif == fu.SINIF_YENI and n.kural == "baglam-yok"


# --- YANLIŞ POZİTİF: yeni konular konuşma sanılmamalı ---------------------------

@pytest.mark.parametrize("soru", [
    "peki ciro?", "bu yıl fire", "makine listesi", "merhaba",
    "operatör bazında rework kg", "geçen ay oee",
])
def test_yeni_konu_KONUSMA_degil(soru):
    n = _s(soru)
    assert not n.konusma, f"{soru!r} yanlışlıkla konuşma sınıfına düştü (kanıt={n.kanit!r})"


def test_UZUN_neden_sorusu_ZAMIR_ister():
    """"neden" tek başına YENİ bir soru da olabilir ("fire neden yüksek olur?"). Uzun
    cümlelerde soruyu eldeki cevaba bağlayan bir işaret zamiri aranır."""
    assert not _s("fire oranı neden yüksek olur genel olarak").konusma
    assert _s("bu fire oranı neden yüksek?").konusma


def test_KISA_soru_zamir_ISTEMEZ():
    """"neden?" / "niye?" zaten eldeki cevaba dairdir — zamir aramak en doğal konuşma
    biçimini kapı dışında bırakırdı."""
    for q in ("neden?", "niye?", "sebebi?"):
        assert _s(q).konusma, q


# --- kelime sınırı disiplini (Faz D3'ün dersi) ----------------------------------

@pytest.mark.parametrize("soru", ["bedenler bazında", "gunu goster"])
def test_kelime_ORTASINDA_eslesmez(soru):
    """`_syn_hit` disiplini burada da geçerli: "neden" kalıbı "beden"i, "gunu" kalıbı
    başka bir şeyi yakalamamalı. Kural YENİDEN YAZILMAZ — `cube_router._syn_hit` çağrılır."""
    n = _s(soru)
    assert n.tur != fu.TUR_NEDEN, f"{soru!r} sahte 'neden' eşleşmesi verdi"


def test_bos_soru():
    assert _s("").sinif == fu.SINIF_YENI
    assert _s("   ").sinif == fu.SINIF_YENI


# --- makbuz ----------------------------------------------------------------------

def test_makbuz_KARARI_tasir():
    """"Neden bu cevap bu biçimde geldi?" — sınıflandırma kararı da kanıtın parçasıdır."""
    import json

    m = fu.makbuza(_s("bu neden böyle?"))
    assert m["followup_class"] == fu.SINIF_KONUSMA
    assert m["followup_kind"] == fu.TUR_NEDEN
    assert m["followup_rule"] == "konusma:neden" and m["followup_evidence"]
    assert json.dumps(m)


def test_NIYET_degismez():
    n = _s("normal mi?")
    with pytest.raises(Exception):
        n.sinif = "baska"  # type: ignore[misc]


def test_turler_TEKIL_ve_kapali():
    turler = {fu.TUR_NEDEN, fu.TUR_NORMAL, fu.TUR_NE_YAPMALI, fu.TUR_ISARET}
    assert len(turler) == 4
    siniflar = {fu.SINIF_YAPISAL, fu.SINIF_KONUSMA, fu.SINIF_YENI}
    assert len(siniflar) == 3


# --- UÇTAN UCA: ölü uç GERÇEKTEN kapandı mı? ------------------------------------

@pytest.mark.parametrize("soru", [
    "bu neden böyle?", "normal mi?", "ne yapmalıyız?",
    "şu düşüş ne?", "bunu nasıl iyileştiririz?", "sence iyi mi?",
])
def test_UCTAN_UCA_olu_uc_kapandi(client, soru):
    """ASIL KANIT. Sınıflandırıcı saf ve testli olabilir ama BAĞLANMAMIŞSA hiçbir şey
    ifade etmez. Bu test HTTP yolundan geçer ve ölçülen ölü uç metinlerinin ARTIK
    dönmediğini doğrular."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    assert ilk.get("cube_query"), f"ilk cevap kurulamadı: {ilk.get('note')!r}"

    d = ask(client, soru, cube_query=ilk["cube_query"], history=[ilk["question"]])
    note = (d.get("note") or "").lower()
    assert "ilişkilendiremedim" not in note, f"{soru!r} hâlâ ölü uçta"
    assert "demek istedin" not in note, f"{soru!r} anlamsız yazım önerisi aldı"
    # Ya bir sonuç ya tıklanır bulgu — ikisi de yoksa cevap boştur.
    assert d.get("result") or d.get("next_steps"), f"{soru!r} boş cevap döndü"


def test_UCTAN_UCA_konusma_DISCOVERYYE_dusmez(client):
    """Kritik: konuşma sınıfı Discovery'ye düşerse bağlamsız ham SQL yazılır ve ölü
    tablo döner — ölçülen sorun tam olarak buydu."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"],
            history=[ilk["question"]])
    assert not (d.get("source") or "").startswith("llm:"), "konuşma Discovery'ye düştü"
    assert any("cevap üstünde konuşma" in t for t in (d.get("trace") or [])), \
        f"çapalanma izde görünmüyor: {d.get('trace')}"


def test_UCTAN_UCA_yapisal_takip_BOZULMADI(client):
    """Gerileme kilidi: üçüncü sınıf, yapısal düzenlemenin önüne geçmemeli."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "aylık", cube_query=ilk["cube_query"], history=[ilk["question"]])
    assert d.get("result"), f"yapısal takip bozuldu: {d.get('note')!r}"
    assert d.get("source") == "cube"
