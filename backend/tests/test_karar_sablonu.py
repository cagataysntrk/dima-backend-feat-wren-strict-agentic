"""FAZ 5.8 kapısı — **kaydet/şablonlaştır**. [bayraksız]

## İki farklı soru, iki farklı alan

| alan | cevapladığı soru |
|---|---|
| `contract_ids` | *"O gün hangi sayıya baktık?"* — **donmuş kanıt** |
| `sablon` | *"Aynı analizi BUGÜN koşsak ne çıkar?"* — **tekrar** |

Biri ötekinin yerine geçmez. Makbuz **geçmişi**, şablon **tekrarı** taşır.

## 🔴 Şablon hash'e DAHİLDİR

Dışarıda bırakmak, kaydın *"hangi analizi tekrarlanabilir kıldığı"* kısmının **sessizce
değiştirilebilmesi** demekti — ve o değişiklik `verified: True` ile birlikte görünürdü.
*Kurcalama tespiti, ancak tespit ettiği alan kadar geniştir.*
"""

from __future__ import annotations

import json

import pytest

from app import decision

_SABLON = {"cube_query": {"cube": "parti", "measures": ["toplam_fire_kg"],
                          "dimensions": ["makine"]},
           "parametreler": ["period"]}


class _Satir:
    """DB satırı taklidi — `oku_satir` saf bir dönüştürücüdür, DB gerektirmez."""

    def __init__(self, **kw):
        self.id = kw.get("id", "d-1")
        self.ts = None
        self.session_id = None
        self.question = kw.get("question")
        self.chosen_json = kw.get("chosen_json")
        self.options_json = kw.get("options_json")
        self.rationale = kw.get("rationale")
        self.note = kw.get("note")
        self.contract_ids_json = kw.get("contract_ids_json", "[]")
        self.content_hash = kw.get("content_hash")
        self.supersedes = None
        self.sablon_json = kw.get("sablon_json")


def _hash(sablon, surum="v2"):
    return decision.hash_of({"question": "s", "chosen": None, "options": None,
                             "rationale": None, "note": None, "contract_ids": [],
                             "sablon": sablon}, surum)


def test_SABLON_hash_e_DAHIL():
    """🔴 Şablon değişirse `verified` **False** olmalı."""
    satir = _Satir(question="s", sablon_json=json.dumps(_SABLON),
                   content_hash=_hash(_SABLON))
    assert decision.oku_satir(satir)["verified"] is True

    # Şablon kurcalandı → hash TUTMAMALI.
    bozuk = dict(_SABLON, cube_query={"cube": "cari", "measures": ["bakiye"]})
    satir2 = _Satir(question="s", sablon_json=json.dumps(bozuk),
                    content_hash=_hash(_SABLON))
    assert decision.oku_satir(satir2)["verified"] is False, (
        "🔴 Şablon hash'in DIŞINDA — kaydın 'hangi analizi tekrarlanabilir kıldığı' "
        "kısmı sessizce değiştirilebilir ve değişiklik `verified: True` ile görünür.")


def test_SABLONSUZ_ESKI_v1_kayit_DOGRULANIR():
    """⚠ Alanı hash'e eklemek, **eski kayıtları toptan kırmamalı**.

    Aksi hâlde her eski kayıt `verified: False` olurdu ve kurcalama tespiti **kendi
    gürültüsünde boğulurdu** — gerçek bir kurcalama artık fark edilmezdi. Kodun kendi
    uyarısı da bunu istiyordu: *"liste genişletilirken sürümleme gerekir."*
    """
    satir = _Satir(question="s", sablon_json=None, content_hash=_hash(None, "v1"))
    r = decision.oku_satir(satir)
    assert r["verified"] is True and r["sablon"] is None
    assert r["hash_surumu"] == "v1", "hangi sürümle doğrulandığı GÖRÜNMELİ"


def test_YENI_kayit_v2_ile_yazilir():
    assert decision.HASH_SURUMU == "v2"
    assert "sablon" in decision._HASH_ALANLARI["v2"]
    assert "sablon" not in decision._HASH_ALANLARI["v1"]


def test_KURCALANMIS_kayit_HICBIR_surumde_tutmaz():
    """⚠ İki sürüm denemek kurcalama tespitini **zayıflatmaz**: saldırgan ikisinden
    hiçbirini tutturamaz."""
    satir = _Satir(question="BASKA SORU", sablon_json=None, content_hash=_hash(None, "v1"))
    r = decision.oku_satir(satir)
    assert r["verified"] is False and r["hash_surumu"] is None


def test_SABLON_okumada_gorunur():
    r = decision.oku_satir(_Satir(question="s", sablon_json=json.dumps(_SABLON)))
    assert r["sablon"]["cube_query"]["cube"] == "parti"
    assert r["sablon"]["parametreler"] == ["period"]


def test_BOZUK_sablon_json_kaydi_COKERTMEZ():
    """Bozuk bir JSON, kararın **okunmasını** engellememeli — kayıt bir tutanaktır."""
    r = decision.oku_satir(_Satir(question="s", sablon_json="{bozuk"))
    assert r["sablon"] is None and r["question"] == "s"


# --- Yeniden koşum ucu -------------------------------------------------------------

class _P:
    tenant_id = "t1"
    user_id = "u1"
    is_superadmin = False


class _Req:
    class state:                                             # noqa: N801
        principal = _P()


def _kayit(sablon_json, tenant="t1"):
    s = _Satir(question="s", sablon_json=sablon_json)
    s.tenant_id = tenant
    return s


def test_SABLONSUZ_kayit_409_doner(monkeypatch):
    """⚠ **404 değil 409**: kayıt VAR ama şablonsuz. *"Bulunamadı"* demek, kullanıcıya
    **yanlış bir teşhis** verirdi."""
    from fastapi import HTTPException

    from app.routers import decisions as r

    monkeypatch.setattr(r, "Session", lambda *a, **k: _FakeSession(_kayit(None)))
    with pytest.raises(HTTPException) as e:
        r.kos_sablon(_Req(), "d-1", {})
    assert e.value.status_code == 409


def test_PARAMETRE_EZMESI_DAR(monkeypatch):
    """🔴 Yalnız şablonun **kendi beyan ettiği** parametreler ezilebilir.

    Serbest ezme, kaydedilmiş bir kararı **başka bir analize** çevirip yine o kararın
    kimliğiyle sunmak olurdu — *bir şablon, bir imzanın altını doldurmaz.*
    """
    from app.routers import decisions as r

    monkeypatch.setattr(r, "Session",
                        lambda *a, **k: _FakeSession(_kayit(json.dumps(_SABLON))))
    out = r.kos_sablon(_Req(), "d-1", {"period": "2026", "cube": "cari",
                                       "measures": ["bakiye"]})
    assert out["cube_query"]["period"] == "2026", "beyan edilen parametre ezilmedi"
    assert out["cube_query"]["cube"] == "parti", (
        "🔴 Beyan EDİLMEMİŞ bir alan ezildi — kayıt başka bir analize çevrildi.")
    assert out["cube_query"]["measures"] == ["toplam_fire_kg"]


def test_BASKA_TENANT_404(monkeypatch):
    """403 DEĞİL 404: *"yetkin yok"* cevabı kaydın **var olduğunu** sızdırır."""
    from fastapi import HTTPException

    from app.routers import decisions as r

    monkeypatch.setattr(r, "Session",
                        lambda *a, **k: _FakeSession(_kayit(json.dumps(_SABLON), "t2")))
    with pytest.raises(HTTPException) as e:
        r.kos_sablon(_Req(), "d-1", {})
    assert e.value.status_code == 404


def test_SQL_TASINMAZ():
    """🔴 Donmuş bir SQL, şema değişince **sessizce yanlış** çalışır.

    `cube_query` ise güncel MDL'de derlenir ve uyuşmazlık **patlar** — sessiz-yanlış
    yerine gürültülü-doğru.
    """
    import ast
    from pathlib import Path

    kaynak = (Path(__file__).resolve().parents[1] / "app/routers/decisions.py").read_text(
        encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(kaynak))
              if isinstance(n, ast.FunctionDef) and n.name == "kos_sablon")
    sabitler = {n.value for n in ast.walk(fn)
                if isinstance(n, ast.Constant) and isinstance(n.value, str)}
    assert "sql" not in sabitler, "🔴 Şablon `sql` taşıyor — donmuş SQL sessizce yanlışlar."


class _FakeSession:
    def __init__(self, kayit):
        self._k = kayit

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def exec(self, *_a, **_k):
        k = self._k

        class _R:
            def first(self):
                return k
        return _R()
