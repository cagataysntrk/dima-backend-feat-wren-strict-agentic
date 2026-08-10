"""GERÇEKÇİ SENARYONUN ÇIKARDIĞI İKİ KUSUR — kapıya çevrilmiş hâli.

Faz X'in deneyim süiti *"üretim müdürünün sabahı"* gibi **gerçek** bir iş akışıyla
koşulunca, hiçbir tek-turluk aracın göremeyeceği iki şey çıktı:

| # | kusur | sınıf |
|---|---|---|
| A | boş sonuç SESSİZ dönüyordu (`satır=0`, not yok) | dürüst iletişim |
| B | takvim yılı ifadesi anlaşılmıyordu (*"2019 yılında"*) | biçimbirim |

(B)'nin belirtisi D1'in absürt-öneri sınıfının aynısıydı:
***"«yilinda» yerine «yield» mi demek istedin?"***
"""

from __future__ import annotations

import pytest

from app import cube_router as cr
from app.llm import _norm
from tests.conftest import ask


# --- A · BOŞ SONUÇ DÜRÜSTÇE SÖYLENİR ----------------------------------------------

def test_A_BOS_SONUC_SESSIZ_DONMEZ(client):
    """Bir *"şirket beyni"*nin verebileceği en kötü cevap sessiz bir boşluktur: okuyucu
    boşluğu KENDİ varsayımıyla doldurur (soru mu yanlış anlaşıldı, veri mi yok, filtre mi
    dar?). Ölçüldü: `satır=0 · not=None · yorum=None`."""
    d = ask(client, "geçen haftada makine bazında oee")
    if (d.get("result") or {}).get("row_count") != 0:
        pytest.skip("bu veri kümesinde geçen hafta DOLU — ölçüm önkoşulu yok (⊘)")
    not_ = d.get("note") or ""
    assert "kayıt bulunamadı" in not_, f"boş sonuç sessiz döndü: {not_!r}"
    assert "2026-" in not_, "hangi aralıkta boş olduğu SÖYLENMİYOR"


def test_A_NOT_UYDURMAZ(client):
    """Not deterministiktir: yalnız sorgunun KENDİ dönem filtresini okur. *"Veri yok"*
    demez — *"bu aralıkta kayıt bulunamadı"* der; ikisi FARKLI iddialardır."""
    d = ask(client, "2019 yılında makine bazında oee")
    not_ = (d.get("note") or "")
    assert "2019-01-01" in not_ and "2019-12-31" in not_, not_
    assert "veri yok" not in not_.lower(), \
        "sistem, ölçemediği bir şeyi (veri hiç yok mu) iddia ediyor"


def test_A_DOLU_SONUCA_NOT_EKLENMEZ(client):
    """KURAL B: dolu bir rapor bugünküyle birebir aynı kalır."""
    d = ask(client, "bu yıl makine bazında oee")
    assert (d.get("result") or {}).get("row_count", 0) > 0
    assert "kayıt bulunamadı" not in (d.get("note") or "")


def test_A_MEVCUT_NOTU_EZMEZ(client):
    """Var olan bir not (netleştirme/konu değişimi) daha bilgilendiricidir — ezilmemeli."""
    import inspect
    import re

    from app.routers import ask as m

    # KOŞULUN KENDİSİ aranır, "yakınında bir yerde" değil: yorum bloğu uzadıkça kayan
    # bir pencere, kapının doğru şeyi ölçtüğünü GARANTİ ETMEZ (bu turda tam olarak oldu).
    # ⟳ **ÇAPA TAŞINDI (`§35`)** — koşul `row_count == 0`'dan `bos_mu`'ya genişledi:
    # gruplamasız bir toplulaştırma boş kümede **bir NULL satır** döndürür, sıfır satır
    # değil, ve eski koşul boşluğun en sık biçimini kaçırıyordu. Çapa silinmedi,
    # yüklemin yeni adına **yeniden çakıldı**; koruduğu şey aynı: mevcut not ezilmemeli.
    #
    # ⟳ **ÇAPA İKİNCİ KEZ TAŞINDI (`§SD`, 2026-08-10).** Yokluğun **iki** biçimi olduğu
    # ölçüldü: toplulaştırma `NULL` döndürür (`bos_mu` görür) ama `COUNT` boş kümede
    # **0** döndürür ve o sıfır bir olgu gibi okunur (*«bu ay hiç parti üretmemişiz»*).
    # İkisinin kararı — ve aralarındaki **öncelik** — `veri_araligi.yokluk_notu`'na
    # toplandı; `ask()`'te kalan yalnız çağrı. Modül büyüme kapısı da bunu istedi.
    #
    # 🔴 **Bu kapının koruduğu şey DEĞİŞMEDİ** ve tam da bu yüzden çapa yeni ada
    # çakılıyor: *mevcut bir not ezilmemeli.* Guard hâlâ çağıranda (`if not resp.note`)
    # çünkü *"zaten bir şey söylendi mi"* sorusunun cevabı **cevabın kendisindedir**,
    # yokluk modülünde değil.
    #
    # *Bir kapıyı bir fonksiyon adına bağlamak, o fonksiyon taşınınca kapıyı kaybetmek
    # demektir — ama çapayı yeniden çakmak, kapıyı gevşetmek değildir: korunan cümle
    # aynı kaldığı sürece adres değişebilir.*
    kaynak = inspect.getsource(m.ask)
    kosul = re.search(r'if ([^\n:]*):\n\s*resp\.note = _va\.yokluk_notu\(', kaynak)
    assert kosul, "boş-sonuç kapısı bulunamadı — desen mi değişti?"
    assert "not resp.note" in kosul.group(1), (
        "boş-sonuç notu mevcut notu EZİYOR: var olan bir not (netleştirme/konu değişimi) "
        "daha bilgilendiricidir")
    # 🔴 `§SD`'nin ikinci yarısı da kapılı: yokluğun **iki** biçimi tek sahipte olmalı.
    # Ayrılırlarsa aralarındaki öncelik iki yerde yazılır ve bir gün yalnız biri
    # güncellenir (`KAT-1`).
    from app import veri_araligi as _va_mod
    _yokluk = inspect.getsource(_va_mod.yokluk_notu)
    assert "bos_mu(" in _yokluk and "donem_disi_notu(" in _yokluk, (
        "🔴 yokluğun iki biçimi tek sahipte değil — öncelik kuralı ikiye bölünmüş")


# --- B · TAKVİM YILI -----------------------------------------------------------------

@pytest.mark.parametrize("q,yil", [
    ("2019 yılında makine bazında oee", 2019),
    ("2019 yılı fire", 2019),
    ("2019'da fire", 2019),
    ("2019 senesinde fire", 2019),
    ("2021 yılındaki fire", 2021),
])
def test_B_TAKVIM_YILI_COZULUR(q, yil, schema):
    r = cr.route(_norm(q), schema)
    assert r is not None, f"{q!r} hâlâ cevapsız"
    f = {(x["operator"], x["value"]) for x in (r["cube_query"].get("filters") or [])}
    assert ("gte", f"{yil}-01-01") in f and ("lte", f"{yil}-12-31") in f, f


@pytest.mark.parametrize("q", ["2019 makine bazında oee", "2019 adet parti",
                               "ilk 2019 satırı göster"])
def test_B_CIPLAK_YIL_BILEREK_KAPSAM_DISI(q, schema):
    """Dört haneli bir sayı bir hesap/şube/TRCODE DEĞERİ de olabilir. En az bir yıl
    işareti aranır — belirsizde dönem SORMAK, uydurmaktan iyidir."""
    r = cr.route(_norm(q), schema)
    if r is None:
        return
    assert not [x for x in (r["cube_query"].get("filters") or [])
                if x.get("dimension") == "tarih"], \
        f"{q!r} çıplak sayıdan dönem UYDURDU: {r['cube_query']}"


def test_B_GORELI_IFADELER_DEGISMEDI(schema):
    """Takvim yılı zincire GÖRELİ ifadelerden SONRA girer — onlar daha spesifiktir."""
    r = cr.route(_norm("geçen yıl fire"), schema)
    f = {(x["operator"], x["value"]) for x in (r["cube_query"].get("filters") or [])}
    assert ("gte", "2025-01-01") in f, f


def test_B_CEYREK_YILDAN_ONCE_gelir(schema):
    """*"2. çeyrek 2019"* → çeyrek kazanmalı; yıl onu ezerse kullanıcı 12 aylık veri alır."""
    r = cr.route(_norm("2. çeyrek 2019 fire"), schema)
    f = {(x["operator"], x["value"]) for x in (r["cube_query"].get("filters") or [])}
    assert ("gte", "2019-04-01") in f and ("lte", "2019-06-30") in f, f
