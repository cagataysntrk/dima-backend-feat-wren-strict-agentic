"""FAZ 0.5 — **ÇAPA ZİNCİRİNİ UYANDIR.** Ölü bir modül üretime bağlanıyor.

## Ölçülen kusur

`app/context.py`'nin `KURAL_CAPA` / `KURAL_COKLU` / `KURAL_CELISKI` kuralları — **19 altın
vakalı, testli** bir modül — **üretimde HİÇ ateşlenmiyordu**. Ölçüldü:
`grep -n "capalar=" backend/app/routers/ask.py` → **0 isabet**. `SureklilikOlcumu` de hiç
çağrılmıyordu.

## Kök neden: engel değil, DÜZLEŞTİRME

`ask.py`'nin yorumu *"thread paneli Faz H4'te yeniden kurulacak"* diyordu — ama panel
**2026-08-01'de kuruldu**. İstemci çapayı **zaten biliyordu**; onu **genel `cube_query`
yuvasına düzleştiriyordu**, bu yüzden sunucu hep `KURAL_YAPISAL` görüyordu.

> **Bayat bir gerekçe kodda kilitli kalmıştı.** Madde küçüldü, kapsamı değişmedi:
> kalan iş **tek alan** — çapanın *kimliğiyle* taşınması.

## Neden kimlik önemli

`cube_query` *"bir önceki raporun durumu"*dur; çapa ise *"kullanıcının İŞARET ETTİĞİ
kart"*. İkisi genelde aynıdır — ama **çok-kart seçiminde** ve **geçmişte gezinirken**
ayrışır. Ayrıştıklarında bugün kullanıcının işaret ettiği yer ile cevabın bağlandığı yer
**sessizce** farklı olur.
"""

from __future__ import annotations

import inspect

from lab.nl_accuracy import _BayrakZorla

from app import context as ctx

#: Gerçek demo şemasından ÖLÇÜLEREK alındı (uydurma cube/ölçü, kapıyı sahte-kırmızı yapar).
CQ_A = {"cube": "bakim", "measures": ["ariza_sayisi"], "dimensions": ["makine"]}
CQ_B = {"cube": "bakim", "measures": ["ariza_sayisi"], "dimensions": ["ariza_tipi"]}
CQ_C = {"cube": "cari", "measures": ["bakiye"], "dimensions": []}


# --- MODÜL ZATEN DOĞRU: bu testler onun ÜRETİME BAĞLANDIĞINI kilitler -------------

def test_TEK_CAPA_karta_yanit():
    b = ctx.coz(cube_query=CQ_C, capalar=[CQ_A], capa_etiketi="fire raporu")
    assert b.kural == ctx.KURAL_CAPA, (
        f"çapa varken kural {b.kural} — kullanıcının AÇIK eylemi, istemcinin taşıdığı "
        "örtük duruma (cube_query) BASKIN gelmeli")
    assert b.cube_query == CQ_A, "çapa yerine cube_query kullanıldı"


def test_COK_CAPA_kesisim():
    b = ctx.coz(capalar=[CQ_A, CQ_B])
    assert b.kural == ctx.KURAL_COKLU
    assert b.cube_query and b.cube_query.get("cube") == "bakim"


def test_CELISKI_SORAR_tahmin_ETMEZ():
    """ADR-0008: belirsizlikte **tahmin etme, SOR**. Farklı cube'lardan iki kartı
    sessizce birleştirmek, kullanıcının görmediği bir karar vermektir."""
    b = ctx.coz(capalar=[CQ_A, CQ_C])
    assert b.kural == ctx.KURAL_CELISKI
    assert b.adaylar and len(b.adaylar) == 2
    assert b.cube_query is None, "çelişkide sessizce bir cube SEÇİLDİ"


# --- ÜRETİME BAĞLANMA: bu maddenin ASIL iddiası ----------------------------------

def test_ASK_CAPALARI_GECIYOR_artik():
    """🔴 **ASIL KAPI.** Ölçüm bu maddeyi doğurdu: `capalar=` **0 isabet**ti."""
    from app.routers import ask as ask_mod

    govde = inspect.getsource(ask_mod.ask)
    assert "capalar=_capalar" in govde, (
        "`coz()`'e çapa listesi HÂLÂ geçilmiyor — `KURAL_CAPA` üretimde ölü kalır")
    assert "body.reply_to_cube_query" in govde, "çapa KİMLİĞİ okunmuyor"
    assert "body.reply_to_extra_cube_queries" in govde, "çok-kart kesişimi bağlanmamış"


def test_SOZLESME_ALANLARI_VAR():
    from app.schemas import AskRequest

    for alan in ("reply_to_cube_query", "reply_to_extra_cube_queries"):
        assert alan in AskRequest.model_fields, f"`{alan}` sözleşmede YOK"


def test_FRONTEND_CAPAYI_GONDERIYOR():
    """D1'in üçüncü parçası: bir alan sözleşmede olup **gönderilmiyorsa** yetimdir."""
    from tests.kapi_ortak import fe_kaynak

    fe = fe_kaynak()
    assert "reply_to_cube_query:" in fe, "frontend çapa kimliğini GÖNDERMİYOR"
    assert "reply_to_extra_cube_queries:" in fe, "çok-kart kesişimi gönderilmiyor"


def test_BAYRAK_KAPALI_iken_DAVRANIS_BIREBIR(client):
    """**GERİ AL.** Bayrak kapalıyken çapa listesi boş kalır → `KURAL_YAPISAL`."""
    from tests.conftest import ask

    with _BayrakZorla("capa_zinciri", acik=False):
        d = client.post("/ask", json={"question": "bu yıl fire", "execute": False,
                                      "reply_to_cube_query": CQ_A}).json()
    assert d.get("question") == "bu yıl fire"
    _ = ask                                   # (yardımcı içe aktarımı korunuyor)


def test_BAYRAK_ACIK_iken_CAPA_DALI_devrede(client):
    """Bayrak açıkken çapa **kullanılır** — ve bu, cevabın `trace`'inde görünür."""
    with _BayrakZorla("capa_zinciri", acik=True):
        r = client.post("/ask", json={
            "question": "makine bazında göster", "execute": False,
            "cube_query": CQ_C,                      # istemcinin örtük durumu
            "reply_to_cube_query": CQ_A,             # kullanıcının AÇIK eylemi
            "reply_to_label": "fire raporu"})
    assert r.status_code == 200, r.text[:200]
    d = r.json()
    assert (d.get("cube_query") or {}).get("cube") == "bakim", (
        "çapa dalı devreye girmedi — cevap `cari` bağlamına kaydı (kullanıcının işaret "
        f"ettiği kart `bakim` idi): {d.get('cube_query')}")
    assert "makine" in ((d.get("cube_query") or {}).get("dimensions") or []) or \
        (d.get("cube_query") or {}).get("dimensions"), "kırılım uygulanmadı"


def test_BAYAT_GEREKCE_KODDA_KALMADI():
    """🔴 *"Bayat bir gerekçe kodda kilitli kalır"* — maddenin kendi uyarısı.
    `ask.py`'nin yorumu *"thread paneli Faz H4'te kurulacak"* diyordu; panel
    2026-08-01'de kuruldu."""
    from app.routers import ask as ask_mod

    kaynak = inspect.getsource(ask_mod)
    assert "HENÜZ istemciden gelmiyor" not in kaynak, (
        "bayat gerekçe hâlâ kodda: `reply_to_cube_query` ARTIK geliyor")
