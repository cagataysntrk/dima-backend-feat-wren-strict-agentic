"""FAZ G5 — bağlam çözücü: sunucunun ARTIK bir bağlam modeli var ve GEREKÇESİ kanıtlı.

## Neden bu dosya var

Ölçüldü (2 Ağustos 2026): `thread_id` ve `reply_to_label` sunucuda **salt echo**,
`is_new_topic` yalnız `not is_followup`'tan türeyen bir boolean. Yani sunucunun bir bağlam
modeli **YOKTU** — hangi soru hangi bağlama ait, istemciye güveniliyordu. Agentic ve
konuşma katmanlarının ikisi de bunun üstüne oturacağı için burası taşıyıcı kolondur.

Ve mantık `ask()` closure'larının içinde olduğu için **izole test edilemiyordu**: 1180
satırlık bir fonksiyonun içinden tek bir kararı ayıklayamazsın. `app/context.py` saf bir
fonksiyondur; bu dosya onun girdi→çıktı davranışını altın vakalarla kilitler.

## Korunan değişmez

**Thread bir UI gruplamasıdır, SEMANTİK SINIR DEĞİLDİR.** Sunucu bir soruyu "yeni konu"
ilan ederek bağlamı sessizce koparamaz — `taze` dönebilir ama **her zaman bir kuralla**
ve o kural makbuza yazılır.
"""

from __future__ import annotations

import pytest

from app import context as ctx

PARTI = {"cube": "parti", "measures": ["toplam_ciro"], "dimensions": ["makine"], "filters": []}
PARTI2 = {"cube": "parti", "measures": ["toplam_ciro", "toplam_fire_kg"],
          "dimensions": ["makine", "renk"], "filters": []}
OEE = {"cube": "oee", "measures": ["ort_oee"], "dimensions": [], "filters": []}


# --- öncelik sırası: AÇIK eylem örtük durumu EZER --------------------------------

def test_CAPA_yapisal_baglami_EZER():
    """ASIL KAPI. Kullanıcı bir karta yanıt verirken istemci hâlâ EN SON raporun
    cube_query'sini taşıyor olabilir. Çapa kazanmazsa cevap, kullanıcının işaret
    ettiğinden BAŞKA bir yere bağlanır — ve bu SESSİZCE olur."""
    b = ctx.coz(cube_query=OEE, capalar=[PARTI], capa_etiketi="mart cirosu")
    assert b.kural == ctx.KURAL_CAPA
    assert b.cube_query["cube"] == "parti"
    assert b.capa_etiketi == "mart cirosu"


def test_yapisal_HAM_takibi_ezer():
    b = ctx.coz(cube_query=PARTI, prev_sql="SELECT 1", history=["önceki soru"])
    assert b.kural == ctx.KURAL_YAPISAL and b.cube_query["cube"] == "parti"


def test_ham_takip_CAPA_ve_YAPISAL_yokken():
    b = ctx.coz(prev_sql="SELECT 1", history=["önceki soru"])
    assert b.kural == ctx.KURAL_HAM
    assert b.cube_query is None, "ham zincirde yapısal bağlam YOKTUR — uydurulmamalı"


def test_capasiz_soru_TAZE_ama_GEREKCELI():
    """Thread bir UI gruplamasıdır: `taze` dönmek serbesttir, GEREKÇESİZ dönmek değil."""
    b = ctx.coz()
    assert b.taze and b.kural == ctx.KURAL_TAZE
    assert b.makbuza()["context_rule"] == ctx.KURAL_TAZE


# --- çoklu seçim: kesişim, çelişkide SOR -----------------------------------------

def test_coklu_capa_KESISIM_kurar():
    """Kullanıcı iki karta işaret ettiğinde "ikisinde de olan"ı kasteder. BİRLEŞİM
    alsaydık seçilmemiş bir ölçü sessizce rapora girerdi."""
    b = ctx.coz(capalar=[PARTI, PARTI2])
    assert b.kural == ctx.KURAL_COKLU
    assert b.cube_query["measures"] == ["toplam_ciro"]
    assert b.cube_query["dimensions"] == ["makine"]


def test_CELISKIDE_sessizce_secmez_SORAR():
    """Farklı cube'lar farklı GRAIN'lerdir; sessizce birleştirmek fan-out'un diyalog
    seviyesindeki karşılığı olurdu — sayı değişir, kimse fark etmez.
    (ADR-0008: belirsizlikte SOR; Faz 3.1 cube-beraberlik chip'inin diyalog eşi.)"""
    b = ctx.coz(capalar=[PARTI, OEE])
    assert b.celiskili and b.kural == ctx.KURAL_CELISKI
    assert b.cube_query is None, "çelişkide bir bağlam SEÇİLMİŞ olmamalı"
    assert len(b.adaylar) == 2, "adaylar kullanıcıya sorulmak üzere taşınmalı"


def test_tek_elemanli_coklu_CAPA_sayilir():
    assert ctx.coz(capalar=[PARTI]).kural == ctx.KURAL_CAPA


def test_bos_capalar_yok_sayilir():
    """`[None]` / `[]` bir seçim DEĞİLDİR — çelişki üretmemeli."""
    assert ctx.coz(capalar=[None], cube_query=PARTI).kural == ctx.KURAL_YAPISAL
    assert ctx.coz(capalar=[]).kural == ctx.KURAL_TAZE


# --- kullanılmış eksenler --------------------------------------------------------

def test_kullanilmis_eksenler_BOYUT_ve_GRANULERLIK():
    """"Peki ya makine bazında?" sorusunda aynı ekseni ikinci kez önermemek için."""
    cq = {**PARTI, "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    b = ctx.coz(cube_query=cq)
    assert b.kullanilmis_eksenler == ("makine", "tarih__month")


def test_eksenler_TEKILLESIR():
    cq = {"cube": "p", "dimensions": ["makine", "makine", "renk"]}
    assert ctx.coz(cube_query=cq).kullanilmis_eksenler == ("makine", "renk")


# --- makbuz: "neden bu bağlam?" cevaplanabilir olmalı ----------------------------

def test_makbuz_GEREKCEYI_tasir():
    """Kanıtlı olmanın somut karşılığı: cevap, çözdüğü bağlamı VE gerekçesini makbuzuna
    yazar. "Neden bu sayı?" sorusunun yanında "neden bu bağlam?" da cevaplanır."""
    b = ctx.coz(capalar=[PARTI], capa_etiketi="mart", kok_makbuz="c-abc123")
    m = b.makbuza()
    assert m["context_rule"] == ctx.KURAL_CAPA
    assert m["resolved_context"] == {
        "cube": "parti", "root_contract": "c-abc123", "anchor": "mart",
        "used_axes": ["makine"], "candidates": 0,
    }


def test_makbuz_CELISKIDE_aday_sayisini_yazar():
    m = ctx.coz(capalar=[PARTI, OEE]).makbuza()
    assert m["context_rule"] == ctx.KURAL_CELISKI
    assert m["resolved_context"]["candidates"] == 2
    assert m["resolved_context"]["cube"] is None


def test_makbuz_JSON_serilesebilir():
    import json

    for b in (ctx.coz(), ctx.coz(cube_query=PARTI), ctx.coz(capalar=[PARTI, OEE])):
        assert json.dumps(b.makbuza())


def test_TUM_kurallar_farkli_ve_makbuza_yaziliyor():
    """Kural adları DIŞARIDAN okunur (denetçi, destek, altın vaka) — çakışmamalı."""
    adlar = [ctx.KURAL_CAPA, ctx.KURAL_COKLU, ctx.KURAL_CELISKI,
             ctx.KURAL_YAPISAL, ctx.KURAL_HAM, ctx.KURAL_TAZE]
    assert len(set(adlar)) == len(adlar)
    assert all(":" in a for a in adlar), "kural adı 'aile:durum' biçiminde olmalı"


def test_BAGLAM_degismez():
    """Çözülmüş bağlam sonradan değiştirilemez — makbuza yazılan ile kullanılan ayrışamaz."""
    b = ctx.coz(cube_query=PARTI)
    with pytest.raises(Exception):
        b.kural = "baska"  # type: ignore[misc]


# --- süreklilik ölçümü -----------------------------------------------------------

def test_sureklilik_KOPMAYI_sayar():
    """Takip bekleniyorken `taze` dönmek = bağlam SESSİZCE koptu."""
    o = ctx.SureklilikOlcumu()
    o.kaydet(ctx.coz(cube_query=PARTI), takip_bekleniyordu=True)   # korundu
    o.kaydet(ctx.coz(), takip_bekleniyordu=True)                   # KOPTU
    o.kaydet(ctx.coz(), takip_bekleniyordu=False)                  # yeni soru — sayılmaz
    assert (o.korunan, o.kopan, o.toplam) == (1, 1, 3)
    assert o.oran == 0.5
    assert o.kurallar[ctx.KURAL_TAZE] == 2


def test_sureklilik_TAKIP_yoksa_oran_NONE():
    """`0.0` "hep koptu" demektir; `None` "bu soru sorulamaz". Ölçülemeyeni kötü
    göstermek, ölçmemekten daha yanıltıcıdır (aynı ayrım `stats.z_skorlari`'nda)."""
    o = ctx.SureklilikOlcumu()
    o.kaydet(ctx.coz(), takip_bekleniyordu=False)
    assert o.oran is None and o.toplam == 1


# --- UÇTAN UCA: gerekçe gerçekten MAKBUZA yazılıyor mu? --------------------------

def test_UCTAN_UCA_makbuz_baglam_kuralini_tasir(client):
    """`app/context.py` saf ve testli olabilir ama BAĞLANMAMIŞSA hiçbir şey ifade etmez —
    bu turda ölçülen dört "beyan var, tüketici yok" vakasının aynısı olurdu
    (`consistency_k`, `expose:` üreteci, fan-out ölçümü, `_select_consistent`).

    Bu test HTTP yolundan geçer ve `contract_log.provenance_json` içinde `context_rule`
    alanını arar: cevap, çözdüğü bağlamı VE gerekçesini kanıtına yazmış olmalı.
    """
    import json

    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import ContractLog
    from tests.conftest import ask

    d = ask(client, "bu yıl makine bazında işlenen kg")
    cid = d.get("contract_id")
    assert cid, f"makbuz üretilmedi: {d.get('note')!r}"

    with Session(engine) as ses:
        row = ses.exec(select(ContractLog).where(ContractLog.id == cid)).first()
    assert row is not None, "makbuz DB'ye yazılmadı"
    assert row.provenance_json, "köken bloğu boş — bağlam gerekçesi kaydedilmemiş"
    prov = json.loads(row.provenance_json)
    assert prov.get("context_rule") in (ctx.KURAL_TAZE, ctx.KURAL_YAPISAL, ctx.KURAL_HAM), \
        f"tanınmayan kural: {prov.get('context_rule')!r}"
    assert "resolved_context" in prov, "çözülmüş bağlam kaydedilmemiş"


def test_UCTAN_UCA_takip_YAPISAL_kurala_baglanir(client):
    """Takip sorusu `taze` DÖNMEMELİ — bağlam sessizce kopmuş olurdu."""
    import json

    from sqlmodel import Session, select

    from control_plane.db import engine
    from control_plane.models import ContractLog
    from tests.conftest import ask

    ilk = ask(client, "bu yıl makine bazında işlenen kg")
    takip = ask(client, "aylık", cube_query=ilk["cube_query"], history=[ilk["question"]])
    cid = takip.get("contract_id")
    assert cid, f"takip makbuz üretmedi: {takip.get('note')!r}"

    with Session(engine) as ses:
        row = ses.exec(select(ContractLog).where(ContractLog.id == cid)).first()
    prov = json.loads(row.provenance_json or "{}")
    assert prov.get("context_rule") == ctx.KURAL_YAPISAL, (
        f"takip sorusu {prov.get('context_rule')!r} kuralına düştü — bağlam koptu")
    assert prov["resolved_context"]["cube"] == ilk["cube_query"]["cube"]
