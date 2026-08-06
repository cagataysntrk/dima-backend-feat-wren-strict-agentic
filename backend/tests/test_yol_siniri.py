"""FAZ F2 — YOL SINIRI: *"yalnız küpün KANITLADIĞI cevapları göster"*.

## Kaynak öneri ve neden AYNEN uygulanmadı

Araştırma raporu bunu *"güven eşiği ayarı"* diye önerdi ve **rakiplerin veremediği fark**
olarak işaretledi: *"yalnız şu yüzdenin üstünde güvenilen cevapları göster."*

Sayısal eşik olarak **UYGULANMADI** — MIMARI'nin açık kararına aykırı:

> *"…kalibre edilmediği sürece o sayı bir güven değil bir **SÜStür**."*

Bizim `1.0 / 0.85 / None` değerleri hesaplanmış bir olasılık **değil**, `_build_explain`'in
**yol etiketidir** (üç değeri var). Bunu "güven eşiği" diye satmak, tam da yasaklanan süs
olurdu.

## Dürüst hâli: MERDİVENİN KENDİSİ

    "deterministik" → yalnız route()            (LLM'e HİÇ gidilmez)
    "llm"           → route + Intent-JSON       (katalogdan SEÇİM; ham SQL yok)
    None / "kesif"  → + Discovery               (bugünkü VARSAYILAN — değişmez)

Aynı kullanıcı değeri (güvene göre süzme), **sıfır uydurma kalibrasyon**. Ve bu ayar
gerçekten kopyalanamaz: rakiplerin **yolu yok**, tek bir kutu var.

## Sessiz kesme YOK

Sınır yüzünden cevapsız kalınırsa **nedeni yazılır**. Aksi hâlde kullanıcı kendi koyduğu
ayarı unutup ürünü yeteneksiz sanır — bu deponun *"sessiz kırpma yok"* disiplini.
"""

from __future__ import annotations

import pytest

SINIRSIZ = [None, "kesif"]


def _sor(client, q, sinir=None):
    from tests.conftest import ask

    return ask(client, q, yol_siniri=sinir) if sinir is not None else ask(client, q)


# --- VARSAYILAN DEĞİŞMEDİ (KURAL B tabanı) -----------------------------------------

@pytest.mark.parametrize("sinir", SINIRSIZ)
def test_SINIRSIZ_davranis_BUGUNKU(client, sinir):
    """`None` ve açık `kesif` aynı olmalı; varsayılan yol hiç değişmemeli.

    ## 🔴 ARAÇ DEĞİŞTİ — ölçüt DEĞİL (2026-08-06)

    Bu test *"Discovery açık mı"*yı **`asdf qwerty zxcv` sorusuna SQL üretiliyor mu**
    diye ölçüyordu. O SQL bir **uydurmaydı**: kural motoru anlamadığı her soruya
    `SELECT COUNT(*) FROM partiler` üretiyordu ve dört farklı anlamsız soru **aynı**
    sayıyı (37 878) döndürüyordu (`tests/test_uydurma_sayi_yok.py`).

    🔴 Yani bu kapı, deponun **en kötü hata sınıfını bir ÖZELLİK sanıp ona
    dayanıyordu** — ve kusur kapatılınca kırmızı verdi.

    ⚠ Ölçüt korunuyor: *sınırsız iki değer AYNI davranmalı.* Değişen yalnız kanıt —
    "SQL var mı" yerine **"ikisi aynı mı"**. *Bir kapının ölçtüğü şey doğruysa, o şeyi
    ölçme biçimi değişebilir; ölçtüğü şey yanlışsa biçimi kurtarmaz.*
    """
    d = _sor(client, "asdf qwerty zxcv", sinir)
    taban = _sor(client, "asdf qwerty zxcv", None)
    assert d.get("source") == taban.get("source"), \
        f"sınır={sinir!r} varsayılandan AYRIŞTI: {d.get('source')} ≠ {taban.get('source')}"
    assert not any("yol sınırı" in (t or "").lower() for t in (d.get("trace") or [])), \
        f"sınır={sinir!r} iken bir yol KESİLDİ — sınırsız olmalıydı"


def test_DETERMINISTIK_cevabi_HER_SEVIYEDE_gelir(client):
    """Kapı fazla geniş olmamalı: `route()`'un çözdüğü soru her seviyede cevaplanır."""
    for sinir in (None, "kesif", "llm", "deterministik"):
        d = _sor(client, "bu yıl makine bazında oee", sinir)
        assert d.get("source") == "cube", f"sınır={sinir!r} → {d.get('source')}"


# --- SEVİYELER GERÇEKTEN KESİYOR ---------------------------------------------------

def test_DETERMINISTIK_LLMe_HIC_gitmiyor(client):
    d = _sor(client, "asdf qwerty zxcv", "deterministik")
    assert not d.get("sql"), "yalnız-küp sınırında ham SQL üretildi"
    assert not str(d.get("source") or "").startswith(("llm", "rule")), \
        f"LLM yoluna düşüldü: {d.get('source')}"


def test_LLM_seviyesi_DISCOVERYi_kesiyor(client):
    """Ara seviye: katalogdan seçim serbest, ham SQL yasak."""
    d = _sor(client, "asdf qwerty zxcv", "llm")
    assert not d.get("sql"), "llm sınırında Discovery yine koştu"


# --- SESSİZ KESME YOK ---------------------------------------------------------------

@pytest.mark.parametrize("sinir", ["deterministik", "llm"])
def test_SINIR_NEDENI_kullaniciya_SOYLENIYOR(client, sinir):
    d = _sor(client, "asdf qwerty zxcv", sinir)
    not_ = (d.get("note") or "").lower()
    assert "yol sınırın" in not_ or "yol sinirin" in not_, \
        f"sınır sessizce kesti (not={d.get('note')!r}) — kullanıcı ayarını unutur"
    assert any("yol sınırı" in (t or "").lower() for t in (d.get("trace") or [])), \
        "trace'te sınır kaydı yok — denetlenemez"


def test_TANINMAYAN_deger_SINIR_SAYILMAZ(client):
    """Bir yazım hatasının kullanıcının cevabını sessizce kesmesi, sınırın kendisinden
    daha zararlıdır → tanınmayan değer varsayılana düşer."""
    d = _sor(client, "asdf qwerty zxcv", "determinstik")   # kasıtlı yazım hatası
    # ⚠ Kanıt "SQL üretildi" DEĞİL (o bir uydurmaydı — yukarıdaki nota bak): tanınmayan
    # değer **varsayılana** düşmeli, yani sınırsız davranışla AYNI olmalı ve hiçbir yol
    # kesilmemeli.
    assert not any("yol sınırı" in (t or "").lower() for t in (d.get("trace") or [])), \
        "tanınmayan sınır değeri bir yolu KESTİ — varsayılana düşmeliydi"
    assert d.get("source") == _sor(client, "asdf qwerty zxcv", None).get("source")


# --- FRONTEND TÜKETİCİSİ (yetim alan kapısı) ---------------------------------------

def test_FRONTEND_TUKETICISI_var():
    """`AskRequest`'e eklenen her alanın bir tüketicisi olmalı — yoksa özellik
    BİTMEMİŞTİR (bu deponun `test_cevap_alani_yetim_degil` disiplini, istek tarafı)."""
    import pathlib

    fe = pathlib.Path(__file__).resolve().parents[2] / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend kaynağı mount edilmemiş")
    metin = "\n".join(f.read_text(encoding="utf-8", errors="ignore")
                      for f in fe.rglob("*.ts*"))
    assert "yol_siniri" in metin, "istek alanı frontend'de HİÇ gönderilmiyor"
    assert "onYolSiniri" in metin, "kullanıcı seçebileceği bir kontrol YOK"
    assert "yalnız küp" in metin, "seviyeler insan-okur etiketle sunulmuyor"


def test_SAYISAL_ESIK_UYGULANMADI():
    """MIMARI kararı: kalibre edilmemiş bir sayı "güven değil süs". Alan adı ya da
    değerleri bir yüzdeye dönerse bu karar sessizce çiğnenmiş olur."""
    from app.schemas import AskRequest

    alan = AskRequest.model_fields["yol_siniri"]
    assert alan.annotation in (str | None, "str | None"), \
        "yol sınırı sayısal bir eşiğe dönüşmüş — MIMARI kararına aykırı"
