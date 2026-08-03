"""FAZ X — DENEYİM SÜİTİNİN BULDUĞU KUSURLAR, kapıya çevrilmiş hâli.

Deneyim süiti (`lab/deneyim.py`) bir konuşmanın **tamamını** ölçer ve ilk koşumunda
tek turluk araçların göremediği **dört** kusur çıkardı. Hepsi burada kilitlenir.

| # | kusur | sınıf |
|---|---|---|
| A | takip düzenlemesi TABAN soruyu VQR'da değiştiriyordu | sessiz-yanlış |
| B | *"geçen yılla kıyasla"* takipte cevapsız | kimlik asimetrisi |
| C | `compare_mode` çekim varyantlarını elle sayıyordu | elle-sayım (ADR-0008) |
| D | dönem ifadesinin YER-DURUM eki cevabı öldürüyordu | biçimbirim |
"""

from __future__ import annotations

import pytest

from app import cube_router as cr
from app.llm import _norm
from tests.conftest import ask


# --- A · ÖĞRENME TAMAMLAMADIR, GENİŞLETME DEĞİL -------------------------------------

def test_A_TAKIP_TABAN_SORUYU_DEGISTIRMEZ(client):
    """Ölçülen kusur (canlı, Faz X):

        1) "bu yıl makine bazında oee"  → dim=['makine']            ✅
        2) takip: "vardiya bazında"     → dim=['makine','vardiya']  ✅
        3) AYNI taban soru tekrar       → source=vqr, ['makine','vardiya']  ❌

    Kullanıcının makine kırılımı isteyen sorusu, bir daha sorulduğunda SORMADIĞI ikinci
    kırılımı getiriyordu; her hücredeki sayı değişiyordu — üstelik `source=vqr` rozetiyle.
    """
    taban = ask(client, "bu yıl makine bazında oee")
    assert (taban.get("cube_query") or {}).get("dimensions") == ["makine"]
    ask(client, "vardiya bazında", cube_query=taban["cube_query"],
        history=["bu yıl makine bazında oee"])
    tekrar = ask(client, "bu yıl makine bazında oee")
    assert (tekrar.get("cube_query") or {}).get("dimensions") == ["makine"], (
        "taban soru KİRLENDİ — takip düzenlemesi onun cevabını değiştirdi: "
        f"{tekrar.get('cube_query')}")


def test_A_GERCEK_TAMAMLAMA_HALA_OGRENILIR(client, schema):
    """Kapı fazla geniş olmamalı — ilk düzeltmem tam da bu yüzden İKİ ALTIN TESTİ
    düşürdü ve kaydı burada duruyor.

    Ayıran ölçüt `route()` DEĞİL **cevaplanabilirlik**tir: `route()` bir şekil döndürse
    bile dönem eksikse ürün *"hangi dönem?"* diye SORAR, yani soru cevaplanmamıştır ve
    kullanıcının onu tamamlaması GERÇEK bir tamamlamadır.

        "kumaş türlerine göre fire oranı" → şekil VAR, dönem YOK → tamamlama ✅ öğrenilir
        "bu yıl makine bazında oee"       → şekil VAR, dönem VAR → GENİŞLETME ❌ öğrenilmez
    """
    konulu_dönemsiz = "kumaş türlerine göre fire oranı"
    hit = cr.route(_norm(konulu_dönemsiz), schema)
    assert hit and cr.needs_period(hit["cube_query"], _norm(konulu_dönemsiz)), (
        "ölçüm önkoşulu: bu soru şekil üretmeli AMA dönem sormalı")
    prev = {"cube": "parti", "measures": ["fire_orani_yuzde"],
            "dimensions": ["kumas_cinsi"],
            "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    d = ask(client, "bu yıl", cube_query=prev, history=[konulu_dönemsiz])
    izler = " ".join(d.get("trace") or [])
    assert "chip-onaylı" in izler, (
        "gerçek chip-tamamlaması artık ÖĞRENİLMİYOR — kapı fazla geniş: " + izler)


# --- B · KIYAS TAKİPTE DE ÇALIŞIR (kimlik asimetrisi) -------------------------------

@pytest.mark.parametrize("q", [
    "geçen yılla kıyasla", "geçen yıla göre", "geçen yılla karşılaştır",
    "önceki yılla kıyasla", "yoy karşılaştır",
])
def test_B_KIYAS_TAKIPTE_CALISIR(client, q):
    """Mekanizma TAZE dalda vardı, kardeşi olan TAKİP dalında YOKTU — bir analistin en
    doğal ikinci cümlesi dürüst rette kalıyordu."""
    taban = ask(client, "bu yıl makine bazında oee")
    d = ask(client, q, cube_query=taban["cube_query"],
            history=["bu yıl makine bazında oee"])
    assert d.get("source") == "cube", f"{q!r} → {d.get('source')} / {d.get('note')!r}"
    assert (d.get("cube_query") or {}).get("compare") == "yoy", d.get("cube_query")


def test_B_TEK_GOVDE_IKI_CAGIRAN():
    """Düzeltirken gövde KOPYALANMADI — iki dal aynı fonksiyonu çağırmalı, aksi hâlde
    zamanla ayrışırlardı (bu deponun bir numaralı kusur sınıfı)."""
    import ast
    import pathlib

    src = pathlib.Path(__file__).resolve().parents[1] / "app" / "routers" / "ask.py"
    agac = ast.parse(src.read_text(encoding="utf-8"))
    cagri = sum(1 for n in ast.walk(agac)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                and n.func.id == "_kiyas_cevabi")
    assert cagri >= 2, f"_kiyas_cevabi yalnız {cagri} yerden çağrılıyor — asimetri sürüyor"
    assert sum(1 for n in ast.walk(agac) if isinstance(n, ast.FunctionDef)
               and n.name == "_kiyas_cevabi") == 1, "ikinci bir gövde doğmuş"


# --- C · compare_mode YAPISAL (çekim varyantı sayılmaz) -----------------------------

@pytest.mark.parametrize("q,beklenen", [
    ("geçen yılla kıyasla", "yoy"), ("geçen yıla göre", "yoy"),
    ("geçen yılla karşılaştır", "yoy"), ("önceki yılla kıyasla", "yoy"),
    ("geçen yıl ile bu yıl", "yoy"), ("yoy karşılaştır", "yoy"),
    ("geçen aya göre", "mom"), ("önceki ayla kıyasla", "mom"),
    # …ve KIYAS OLMAYANLAR (yanlış-pozitif koruması)
    ("geçen yıl ciro", None), ("geçen ay fire", None),
    ("bu yıl makine bazında oee", None), ("son 4 aya göre yap", None),
])
def test_C_COMPARE_MODE(q, beklenen):
    assert cr.compare_mode(_norm(q)) == beklenen, q


def test_C_BITISIKLIK_SARTI_KRITIK():
    """`gore` cümlede geçiyor diye kıyas sayılamaz — *"geçen yıl makineye GÖRE fire"*
    sıradan bir kırılım sorusudur. Bitişiklik şartı olmasaydı bu soru YoY sanılırdı."""
    assert cr.compare_mode(_norm("geçen yıl makineye göre fire")) is None
    assert cr.compare_mode(_norm("geçen yıla göre fire")) == "yoy"


def test_C_STRIP_COMPARE_TABANI_BIRAKIR():
    assert cr.strip_compare(_norm("geçen yıla göre makine bazında oee")) == "makine bazinda oee"


# --- D · DÖNEM İFADESİNİN ÇEKİM EKİ ------------------------------------------------

@pytest.mark.parametrize("q", [
    "son 6 ayda fire", "son 3 ayda ciro", "son 2 yılda ciro",
    "geçen ayda fire", "önceki ayda fire", "geçen haftada fire",
    "bu ayda fire", "ocak ayında fire",
])
def test_D_YER_DURUM_EKI_CEVABI_OLDURMEZ(q, schema):
    """Türkçede en doğal söyleyiş buydu ve HEPSİ cevapsız kalıyordu:

        "son 6 ay fire"    → route VAR ✅
        "son 6 ayDA fire"  → route YOK ❌

    Kök neden iki katmanlı: `_REL_DATE`/`_PREV_RE` kökü yakalıyordu, `_uncovered` ise
    bilinen kelimeleri `len >= 3` ile süzüyordu → `ay` elenir, kendi çekimini kapsayamaz.
    """
    assert cr.route(_norm(q), schema) is not None, f"{q!r} hâlâ cevapsız"


@pytest.mark.parametrize("q", ["son 6 ayakkabı fire", "geçen ayakkabı fire"])
def test_D_KAZARA_DENK_GELEN_DEVAM_DONEM_SAYILMAZ(q, schema):
    """`_ek_gecerli` tek kaynak: `akkabi` geçerli bir ek zinciri değildir."""
    r = cr.route(_norm(q), schema)
    if r is None:
        return
    assert not (r["cube_query"].get("filters") or []), \
        f"{q!r} sahte dönem filtresi üretti: {r['cube_query']}"


def test_D_UYDURMA_DONEM_YOK(schema):
    """Düzeltme kapsamı genişletmemeli: dönem GEÇMEYEN soru dönem filtresi almamalı."""
    r = cr.route(_norm("makine bazında oee"), schema)
    if r:
        assert not [f for f in (r["cube_query"].get("filters") or [])
                    if f.get("dimension") == "tarih"], r["cube_query"]
