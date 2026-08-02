"""FAZ G3 — reçeteli analiz: *"ne yapmalıyız?"*in ölçülebilir yarısı.

## Neden bu modül DAR (ve dar olması bir kusur değil)

Bir "karar matrisi" kolayca uydurulur: seçenekler × kriterler × ağırlıklar tablosu her
zaman bir sayı üretir. Ama o sayıların **ölçülmüş bir zemini yoksa** ürün, kanıtlanabilir
bir BI aracından **kanaat üreten** bir araca dönüşür — ve bu depoda kayıtlı en temel
değişmez *"cevap bir makbuzdur"*dır.

Kullanılan üç boyutun üçü de ölçülmüş ya da **beyan edilmiştir**: etki (`contribution`
deltası) · yön (`lower_is_better` metadata beyanı) · yoğunlaşma (hesaplanmış oran).

**Kasten dışarıda:** kontrol edilebilirlik · uygulama maliyeti · risk. Hiçbiri veride yok
ve tahmin edilemez; bir ağırlık tablosuna konsalardı sıralama **uydurma** olurdu — üstelik
`source="cube"` rozetiyle.

## En önemli çıktı bir öneri değil bir REDDİR

Değişim dağınıksa *"şu segmente odaklan"* **yanlış tavsiyedir**: sorun sistemiktir. Bu
modül o durumda öneri üretmez, **neden üretmediğini söyler** — `contribution`'ın
toplanabilirlik kapısıyla aynı disiplin.
"""

from __future__ import annotations

import pytest

from app import prescribe


def _bulgu(ad: str, delta: float, pay: float | None = None):
    return {"label": ad, "delta": delta, "net_pay": pay,
            "cube_query": {"cube": "parti", "measures": ["m"],
                           "filters": [{"dimension": "d", "operator": "eq", "value": ad}]}}


def _rapor(bulgular, brut=None, net=None):
    b = list(bulgular)
    return {"bulgular": b,
            "brut_hareket": brut if brut is not None else sum(abs(x["delta"]) for x in b),
            "net_degisim": net if net is not None else sum(x["delta"] for x in b)}


# --- ASIL KAPI: dağınık değişimde ÖNERİ ÜRETİLMEZ -------------------------------

def test_DAGINIK_degisimde_oneri_YOK():
    """ASIL KAPI. Beş eşit segment → hiçbiri "sürükleyici" değil. "Şu segmente odaklan"
    demek diğer beşte dördünü görmezden gelmektir; sorun sistemiktir."""
    r = prescribe.recete(_rapor([_bulgu(f"S{i}", 20.0) for i in range(5)]))
    assert r.dagitik and not r.oneriler
    assert "dağınık" in r.gerekce and "sistemik" in r.gerekce
    assert r.yogunlasma == pytest.approx(0.2)


def test_YOGUNLASMIS_degisimde_oneri_VAR():
    r = prescribe.recete(_rapor([_bulgu("A", 90.0), _bulgu("B", 5.0), _bulgu("C", 5.0)]))
    assert not r.dagitik and r.oneriler
    assert r.oneriler[0].segment == "A"
    assert "yoğunlaşmış" in r.gerekce


def test_esik_SINIRINDA_karar():
    """Eşik 1/3: en büyük segment brüt hareketin tam üçte birini açıklıyorsa YOĞUNLAŞMIŞ
    sayılır (sınır dahil) — sınırı dışlamak, eşiği fiilen daha katı yapardı."""
    r = prescribe.recete(_rapor([_bulgu("A", 100.0), _bulgu("B", 100.0), _bulgu("C", 100.0)]))
    assert not r.dagitik, "tam eşikte dağınık sayıldı"


# --- YÖN: beyandan gelir, ad tahmininden DEĞİL ---------------------------------

def test_yon_LOWER_IS_BETTER_beyanindan():
    """Fire artışı KÖTÜ, ciro artışı İYİ — ve bunu ad tahmininden değil BEYANDAN
    biliyoruz. `lower_is_better` `schema()`'da Faz 1'den beri vardı ve MIMARI §13.4'te
    "recommend()'e ulaşıyor ama karara dönüşmüyor" diye kayıtlıydı."""
    art = _rapor([_bulgu("A", 90.0), _bulgu("B", 5.0)])
    assert prescribe.recete(art, lower_is_better=False).oneriler[0].yon == "iyilesti"
    assert prescribe.recete(art, lower_is_better=True).oneriler[0].yon == "kotulesti"


def test_yon_AZALMA():
    azalma = _rapor([_bulgu("A", -90.0), _bulgu("B", -5.0)])
    assert prescribe.recete(azalma, lower_is_better=False).oneriler[0].yon == "kotulesti"
    assert prescribe.recete(azalma, lower_is_better=True).oneriler[0].yon == "iyilesti"


def test_gerekce_TERS_YONDEKILERI_sayar():
    r = prescribe.recete(_rapor([_bulgu("A", 90.0), _bulgu("B", -5.0), _bulgu("C", 5.0)]),
                         lower_is_better=True)
    assert "2 segment ters yönde" in r.gerekce   # A ve C arttı, lower_is_better → kötü


def test_hepsi_ISTENEN_yonde():
    r = prescribe.recete(_rapor([_bulgu("A", 90.0), _bulgu("B", 5.0)]), lower_is_better=False)
    assert "istenen yönde" in r.gerekce


# --- SIRALAMA ve SINIR ----------------------------------------------------------

def test_ETKIYE_gore_siralanir_MUTLAK_deger():
    """Sıralama mutlak etkiye göredir: −100'lük bir segment +10'luk bir segmentten daha
    önemlidir, yönü ne olursa olsun."""
    r = prescribe.recete(_rapor([_bulgu("kucuk", 10.0), _bulgu("buyuk", -100.0)]))
    assert [o.segment for o in r.oneriler] == ["buyuk", "kucuk"]


def test_AZAMI_UC_oneri():
    """Liste uzadıkça "önceliklendirme" iddiası zayıflar: onuncu segment bir gündem
    değil bir DÖKÜMDÜR."""
    r = prescribe.recete(_rapor([_bulgu("A", 500.0)] + [_bulgu(f"S{i}", 1.0) for i in range(9)]))
    assert len(r.oneriler) == 3


def test_pay_NONE_ise_UYDURULMAZ():
    """`net_pay=None` = "net değişim ~0, pay TANIMSIZ". Backend bunu bilerek uydurmuyor;
    reçete de uydurmamalı."""
    r = prescribe.recete(_rapor([_bulgu("A", 90.0, None), _bulgu("B", 5.0, 0.05)]))
    assert r.oneriler[0].pay is None and r.oneriler[1].pay == 0.05


# --- SINIR DURUMLAR -------------------------------------------------------------

def test_BULGU_yoksa_dürüst_ret():
    r = prescribe.recete({"bulgular": [], "brut_hareket": 0, "net_degisim": 0})
    assert not r.oneriler and "bulunamadı" in r.gerekce


def test_cube_query_SIZ_bulgu_elenir():
    """Tıklanamayan bir öneri, öneri değil bir cümledir — ürünün tezi her bulgunun
    doğrulanabilir bir sorgu olmasıdır."""
    r = prescribe.recete(_rapor([{"label": "X", "delta": 100.0, "net_pay": 1.0}]))
    assert not r.oneriler


def test_BRUT_sifirsa_patlamaz():
    r = prescribe.recete(_rapor([_bulgu("A", 0.0)], brut=0.0))
    assert r.yogunlasma is None and not r.dagitik


# --- MAKBUZ ---------------------------------------------------------------------

def test_makbuz_GEREKCEYI_tasir():
    """Reçete de bir karardır: neden bu üç segment, neden daha fazlası değil."""
    import json

    r = prescribe.recete(_rapor([_bulgu("A", 90.0), _bulgu("B", 5.0)]), lower_is_better=True)
    m = r.makbuza()["prescription"]
    assert m["rationale"] and m["diffuse"] is False
    assert m["options"][0]["direction"] == "kotulesti"
    assert json.dumps(m)


def test_makbuz_DAGINIKTA_da_gerekce_tasir():
    """Öneri üretmemek de bir karardır ve gerekçesi kayda geçer."""
    m = prescribe.recete(_rapor([_bulgu(f"S{i}", 20.0) for i in range(5)])).makbuza()
    assert m["prescription"]["diffuse"] is True and m["prescription"]["rationale"]
    assert m["prescription"]["options"] == []


# --- UYDURULMAYAN boyutlar ------------------------------------------------------

def test_UYDURMA_boyut_YOK():
    """Kontrol edilebilirlik / maliyet / risk veride YOK ve tahmin edilemez. Bir ağırlık
    tablosuna konsalardı sıralama uydurma olurdu — üstelik `source="cube"` rozetiyle.
    Bu test o boyutların sessizce geri gelmesini engeller."""
    import inspect

    kaynak = inspect.getsource(prescribe)
    govde = kaynak.replace(prescribe.__doc__ or "", "")
    for uydurma in ("kontrol_edilebilir", "maliyet_skoru", "risk_skoru", "agirlik"):
        assert uydurma not in govde, f"ölçülmemiş boyut eklenmiş: {uydurma}"


# --- UÇTAN UCA: "ne yapmalıyız?" reçete üretiyor mu? ----------------------------

def test_UCTAN_UCA_ne_yapmaliyiz_RECETE_uretir(client):
    """Modül saf ve testli olabilir ama BAĞLANMAMIŞSA hiçbir şey ifade etmez — bu
    oturumda SEKİZ kez ölçtüğüm desen. Bu test HTTP yolundan geçer."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "ne yapmalıyız?", cube_query=ilk["cube_query"], history=[ilk["question"]])
    izler = d.get("trace") or []
    assert any("Reçete:" in t for t in izler), f"reçete izde yok: {izler}"
    # Cevap ya öneri ya DÜRÜST RED taşımalı — ikisi de bir cevaptır, boşluk değil.
    assert d.get("note"), "reçete gerekçesi yok"


def test_UCTAN_UCA_neden_boyle_RECETE_uretmez(client):
    """"Neden böyle?" bir AÇIKLAMA ister, reçete değil. İkisini karıştırmak,
    kullanıcının SORMADIĞI bir tavsiyeyi cevabın yerine koymak olurdu."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"], history=[ilk["question"]])
    assert not any("Reçete:" in t for t in (d.get("trace") or [])), \
        "açıklama sorusuna istenmeyen reçete eklendi"
    assert d.get("contribution"), "açıklama cevabı bozuldu"


# --- UI SÖZLEŞMESİ: reçete YAPILI gelir, düz metne çevrilmez -------------------

def test_recete_YAPILI_govde_tasir(client):
    """ÖLÇÜLEN BOŞLUK. Reçete yalnız `note` metnine çevrilseydi backend'de hesaplanan
    ÜÇ ŞEY de kaybolurdu: segment başına YÖN (`lower_is_better` beyanından), YOĞUNLAŞMA
    oranı ve etki/pay sayıları. Chip yalnız etiket taşır; **yön bir RENK kararıdır ve
    metinden okunmaz** — "fire arttı" kötü haberdir, "ciro arttı" iyi."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "ne yapmalıyız?", cube_query=ilk["cube_query"], history=[ilk["question"]])

    r = d.get("prescription")
    assert r, "reçete yapılı gövde taşımıyor — UI düz metne düşer"
    assert "rationale" in r and "diffuse" in r and "concentration" in r
    for o in r["options"]:
        assert o["direction"] in ("kotulesti", "iyilesti"), o
        assert "impact" in o and "share" in o
        assert o.get("cube_query"), "öneri tıklanabilir DEĞİL — öneri değil bir cümle olur"


def test_aciklama_sorusu_RECETE_tasimaz(client):
    """Gerileme kilidi: "bu neden böyle?" bir AÇIKLAMA ister. Reçete alanı dolarsa
    kullanıcı sormadığı bir tavsiyeyi cevabın yerine görür."""
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    d = ask(client, "bu neden böyle?", cube_query=ilk["cube_query"], history=[ilk["question"]])
    assert not d.get("prescription")


def test_normal_rapor_RECETE_tasimaz(client):
    """Kademeli açılım: istenmeden reçete gösterilmez."""
    from tests.conftest import ask

    assert not ask(client, "bu yıl makine bazında işlenen kg").get("prescription")
