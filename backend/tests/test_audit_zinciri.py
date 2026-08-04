"""FAZ 1.8 — **AUDIT ZİNCİRİ** kapısı: zincir kopukluğu **tespit ediliyor mu?**

`AuditLog` *"append-only erişim kanıtı"* diyor — ama **append-only bir BEYANDIR**, bir
mekanizma değil: bir satır `DELETE` edilirse geriye **hiçbir iz** kalmaz. *Bir kanıt kaydı,
eksildiğini kendisi söyleyemiyorsa kanıt değildir.*
"""

from __future__ import annotations

import pathlib

import pytest

from app import audit_zinciri as Z

KOK = pathlib.Path(__file__).resolve().parents[1]


def _zincir(n: int = 4) -> list[dict]:
    """Sağlam bir zincir üretir."""
    out: list[dict] = []
    onceki = Z.GENESIS
    for i in range(n):
        k = {"tenant_id": "t", "ts": f"2026-08-04T10:0{i}:00", "action": "query",
             "nl_question": f"soru {i}", "onceki_kayit_hash": onceki}
        k["kayit_hash"] = Z.kayit_hash(k, onceki)
        out.append(k)
        onceki = k["kayit_hash"]
    return out


# ── 1 · SAĞLAM ZİNCİR SESSİZ ────────────────────────────────────────────────

def test_SAGLAM_ZINCIR_BULGU_URETMIYOR():
    """*Gürültüyle ateşleyen bir kapı kapatılır* — sağlam zincir **hiçbir** şey demez."""
    assert Z.zinciri_dogrula(_zincir()) == []


def test_BOS_ZINCIR_SAGLAM():
    assert Z.zinciri_dogrula([]) == []


def test_ILK_KAYIT_GENESIS():
    """`GENESIS` bir **değerdir**, `None` değil: `None` *"hash hesaplanmadı"* ile
    karıştırılırdı; `genesis` *"burası başlangıç"* der."""
    assert Z.GENESIS == "genesis"
    assert _zincir(1)[0]["onceki_kayit_hash"] == Z.GENESIS


# ── 2 · 🔴 SİLME TESPİT EDİLİYOR ────────────────────────────────────────────

def test_SILINEN_KAYIT_ZINCIRI_KOPARIYOR():
    """🔴 **Maddenin kalbi.** Ortadan bir satır silinirse zincir **kopar**."""
    z = _zincir(4)
    del z[1]
    bulgular = Z.zinciri_dogrula(z)
    assert any(b.startswith("KOPUK") for b in bulgular), bulgular
    assert any("SİLİNMİŞ" in b for b in bulgular)


def test_SON_KAYIT_SILINMESI_TESPIT_EDILEMIYOR_ve_YAZILI():
    """⚠ **Zincirin bilinen sınırı:** **son** kaydı silmek zinciri **koparmaz** (ondan
    sonra kimse yok). Bunu *"tespit ediliyor"* diye yazmak, olmayan bir garanti satmak
    olurdu. Harici bir çıpa (dış zaman damgası / WORM) gerekir ve bu maddede **yok**.
    """
    z = _zincir(4)
    del z[-1]
    assert Z.zinciri_dogrula(z) == [], "beklenmedik bulgu — sınır değişmiş olabilir"
    kaynak = (KOK / "app" / "audit_zinciri.py").read_text(encoding="utf-8")
    assert "harici bir çıpa" in kaynak.lower(), "sınır belgede yazılı değil"


# ── 3 · 🔴 DEĞİŞTİRME TESPİT EDİLİYOR ───────────────────────────────────────

def test_DEGISTIRILEN_KAYIT_BOZULMUS_veriyor():
    z = _zincir(3)
    z[1]["nl_question"] = "gizlice değiştirildi"
    bulgular = Z.zinciri_dogrula(z)
    assert any(b.startswith("BOZULMUŞ") for b in bulgular), bulgular


def test_ZAMAN_DAMGASI_DA_HASHE_GIRIYOR():
    """Bir kaydın **zamanını** değiştirmek, kaydı değiştirmektir."""
    assert "ts" in Z.ZINCIR_ALANLARI
    z = _zincir(2)
    z[0]["ts"] = "2020-01-01T00:00:00"
    assert any(b.startswith("BOZULMUŞ") for b in Z.zinciri_dogrula(z))


def test_ID_HASHE_GIRMIYOR():
    """`id` rastgeledir; hash'e katmak zinciri **yeniden üretilemez** kılardı."""
    assert "id" not in Z.ZINCIR_ALANLARI


# ── 4 · ÇATAL AYRI BİR BULGU ────────────────────────────────────────────────

def test_ESZAMANLI_YAZIM_CATAL_olarak_raporlaniyor():
    """⚠ Zincir eşzamanlı yazımları **sıralamaz** — ama çatal **tespit edilir**.
    🔴 Üç bulguyu tek bir *"zincir bozuk"* mesajına indirmek, **hangi** olayın yaşandığını
    gizlerdi — ve **silme** ile **eşzamanlılık** çok farklı şeylerdir."""
    z = _zincir(2)
    catal = dict(z[1])
    catal["nl_question"] = "aynı anda yazıldı"
    catal["kayit_hash"] = Z.kayit_hash(catal, catal["onceki_kayit_hash"])
    bulgular = Z.zinciri_dogrula([z[0], z[1], catal])
    assert any(b.startswith("ÇATAL") for b in bulgular), bulgular


def test_UC_BULGU_SINIFI_AYRI():
    kaynak = (KOK / "app" / "audit_zinciri.py").read_text(encoding="utf-8")
    for sinif in ("KOPUK", "BOZULMUŞ", "ÇATAL"):
        assert sinif in kaynak, sinif


# ── 5 · KANONİKLİK ──────────────────────────────────────────────────────────

def test_ALAN_SIRASI_HASHI_DEGISTIRMIYOR():
    """Alan sırası hash'i değiştirseydi zincir **kendiliğinden** koparıdı ve doğrulama
    gürültüye boğulurdu."""
    a = Z.kayit_hash({"action": "q", "ts": "x", "tenant_id": "t"}, "p")
    b = Z.kayit_hash({"tenant_id": "t", "ts": "x", "action": "q"}, "p")
    assert a == b


def test_DATETIME_VE_UUID_KANONIKLESIYOR():
    """Tip temsili değişirse hash değişir ve zincir **yanlış** koparıdı."""
    import uuid as _u
    from datetime import datetime

    h1 = Z.kayit_hash({"ts": datetime(2026, 8, 4, 10, 0)}, "p")
    h2 = Z.kayit_hash({"ts": "2026-08-04T10:00:00"}, "p")
    assert h1 == h2
    assert Z.kayit_hash({"tenant_id": _u.UUID(int=1)}, "p")  # patlamamalı


# ── 6 · OTel — YENİ KOLON YOK, EŞLEME VAR ───────────────────────────────────

def test_OTEL_ADLARINA_CEVIRIYOR():
    n = Z.otel_nitelikleri({
        "source": "llm:gemini", "kind": "llm", "llm_model": "gemini-flash",
        "llm_input_tokens": 120, "llm_output_tokens": 40, "llm_latency_ms": 900,
        "user_id": "u1"})
    assert n["gen_ai.system"] == "gemini"
    assert n["gen_ai.request.model"] == "gemini-flash"
    assert n["gen_ai.usage.input_tokens"] == 120
    assert n["prov:wasAssociatedWith"] == "u1"


def test_BOS_ALAN_YAYINLANMIYOR():
    """⚠ OTel'de eksik bir nitelik **yokluktur**, `None` değil —
    `gen_ai.usage.input_tokens=null` yayınlamak *"ölçüldü ve sıfırdı"* gibi okunur."""
    n = Z.otel_nitelikleri({"source": "cube", "kind": "cube"})
    assert "gen_ai.request.model" not in n
    assert "gen_ai.system" not in n, "cube yolunda LLM sağlayıcısı YOK, yazılmamalı"


def test_YENI_KOLON_ACILMADI():
    """🔴 Veri **zaten** oradaydı (`llm_model` · `llm_*_tokens` · `llm_latency_ms` ·
    `source`). OTel adlarıyla ikinci bir kolon kümesi, aynı gerçeğin **iki kopyası**
    olurdu ve ikisi zamanla ayrışırdı. Bu bir **çeviricidir**, bir depo değil."""
    modeller = (KOK / "control_plane" / "models.py").read_text(encoding="utf-8")
    assert "gen_ai" not in modeller, "OTel adları TABLOYA kopyalanmış — iki sahip"
    assert "llm_input_tokens" in modeller, "kaynak alan kaybolmuş"


# ── 7 · ŞEMA + YAZMA YOLU ───────────────────────────────────────────────────

def test_AUDITLOG_ZINCIR_KOLONLARI_VAR():
    from control_plane.models import AuditLog

    for alan in ("onceki_kayit_hash", "kayit_hash"):
        assert alan in AuditLog.model_fields, alan


def test_YAZMA_YOLU_ZINCIRI_HESAPLIYOR():
    """Bir modül yazmak yetmez; zincir ancak **yazıldığı yerde** vardır."""
    import ast

    kaynak = (KOK / "control_plane" / "audit.py").read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_persist")
    assert any(isinstance(n, ast.Call) and getattr(n.func, "id", "") == "kayit_hash"
               for n in ast.walk(fn)), "`_persist` zinciri HESAPLAMIYOR — modül ölü"


def test_ZINCIR_HATASI_KAYDI_DUSURMUYOR():
    """🔴 Bir kanıt kaydını *"zincir kurulamadı"* diye **düşürmek**, korumaya çalıştığı
    şeyi yok etmek olurdu — ve eksik hash zaten `zinciri_dogrula`'da **görünür**."""
    kaynak = (KOK / "control_plane" / "audit.py").read_text(encoding="utf-8")
    i = kaynak.index("def _persist")
    govde = kaynak[i:i + 2000]
    assert "except Exception" in govde and "session.add(row)" in govde
    assert govde.index("except Exception") < govde.rindex("session.add(row)"), \
        "zincir hatası kaydı düşürüyor — kanıt, korumasının kurbanı olmamalı"
