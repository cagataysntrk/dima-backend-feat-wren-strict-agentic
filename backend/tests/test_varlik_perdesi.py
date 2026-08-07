"""🔴 `G0b.6` — VARLIK PERDESİ: çözülen bir değer sağlayıcıya HAM gitmez.

## Ölçüm önce yapıldı — ve bir yarısı ZATEN kapalıydı

Endişe: `value_index`'in çözdüğü gerçek katalog adı (*"efe dokma"* → *"efe dokuma"*)
LLM'e sızar mı? ⊙ **Sızmıyor**: `ask.py`'nin ürettiği `corrected_q` yalnız deterministik
yeniden yönlendirmede kullanılıyor; LLM'e giden şey her zaman `body.question`.

🔴 Ama **başka bir kapı açıktı**: `build_catalog` prompt'a boyutların **gerçek
değerlerini** (≤25) yazıyor. Perde oraya kuruldu — sorudaki değer için.

*Bir kapıyı kapalı bulmak, öteki kapıyı aramamak için sebep değildir.*
"""

from __future__ import annotations

import pytest

from app import varlik


@pytest.fixture(scope="module")
def _deger(schema):
    """Katalogda gerçekten bulunan, prompt'a çıkabilen bir boyut değeri."""
    from app.sensitivity import prompt_safe_values

    cols = {c["name"]: c for m in schema.get("models") or [] for c in m.get("columns") or []}
    for c in schema.get("cubes") or []:
        for dim in c.get("dimensions") or []:
            for v in prompt_safe_values(cols.get(dim) or {}) or []:
                if len(str(v).strip()) >= 4:
                    return str(v).strip(), dim
    pytest.skip("⊘ katalogda prompt'a çıkan değer yok — vaka bayat")


def test_SORUDAKI_GERCEK_DEGER_PROMPTA_CIKMIYOR(schema, _deger):
    """🔴 Kapının asıl iddiası: perdelenmiş soruda gerçek ad **hiç geçmiyor**."""
    deger, dim = _deger
    q = f"{deger} için ciro"
    perdeli, harita, kural = varlik.perdele(q, schema)
    assert deger.lower() not in perdeli.lower(), f"🔴 gerçek ad sızdı: {perdeli!r}"
    assert harita and deger in harita.values()
    assert dim in kural or any(dim in k for k in [kural]), (
        "🔴 kural satırı BOYUTU söylemiyor — perde bilgi kaybına dönüşür")


def test_PERDE_BILGI_KAYBI_DEGIL_KAZANCI(schema, _deger):
    """⚠ Ham değer *"bu ne?"* sorusunu açık bırakır; yer tutucu **hangi boyuta ait
    olduğunu söyler**. Deterministik katman zaten çözmüştü."""
    deger, dim = _deger
    _, _, kural = varlik.perdele(f"{deger} cirosu", schema)
    assert "{{ENT_1}}" in kural and f"`{dim}`" in kural


def test_GERI_KOYMA_SORGUYU_ONARIYOR(schema, _deger):
    deger, dim = _deger
    _, harita, _ = varlik.perdele(f"{deger} cirosu", schema)
    cq = {"cube": "x", "filters": [{"dimension": dim, "operator": "eq",
                                    "value": "{{ENT_1}}"}]}
    out = varlik.geri_koy(cq, harita)
    assert out["filters"][0]["value"] == deger


def test_COZULEMEYEN_YUVA_SORGUYU_DUSURUR():
    """🔴 FAIL-CLOSED. Yarım geri konmuş bir filtre `{{ENT_9}}` diye bir değer arardı:
    hiç satır dönmez ve cevap *"veri yok"* olur — kullanıcı bunu bir **bulgu** sanar.
    *Yanlış bir boşluk, görünür bir hatadan beterdir.*"""
    cq = {"cube": "x", "filters": [{"dimension": "d", "operator": "eq",
                                    "value": "{{ENT_9}}"}]}
    assert varlik.geri_koy(cq, {"{{ENT_1}}": "A"}) is None


def test_PERDE_YOKSA_SORU_DEGISMEZ(schema):
    """Katalog değeri geçmeyen bir soru **bayt bayt** aynı kalmalı: perdeleme bir
    dönüşüm değil, bir **koşullu** dönüşümdür."""
    q = "gecen ay toplam ciro"
    perdeli, harita, kural = varlik.perdele(q, schema)
    assert (perdeli, harita, kural) == (q, {}, "")


def test_KISA_DEGER_PERDELENMEZ(schema):
    """*Bir maske, maskelediğinden fazlasını örtüyorsa maske değil sansürdür.* İki
    harflik bir değer cümlenin ortasında tesadüfen geçer."""
    assert varlik._MIN_UZUNLUK >= 3


def test_SUZGECIN_SAHIBI_BU_MODUL_DEGIL():
    """🔴 *"Hangi değer görülebilir"* sorusunun tek sahibi `app/sensitivity.py`.

    İkinci bir politika yazılsaydı iki prompt üreticisi **farklı** değer kümesi görürdü —
    ve bu depoda tam olarak **bir kez oldu** (`build_catalog`'un kendi şerhi: *"eskiden
    iki prompt üreticisi farklı politika uyguluyordu"*)."""
    import inspect

    src = inspect.getsource(varlik.perdele)
    assert "prompt_safe_values" in src, "süzgeç ikinci kez yazılmış"
    assert "VARCHAR" not in src and "whitelist" not in src.lower()


# --- ÖTEKİ KAPI: düzeltilmiş soru LLM'e GİTMEZ (ölçülen durumun kilidi) -----------

def test_DUZELTILMIS_SORU_SAGLAYICIYA_GITMIYOR():
    """⊙ Bu yarı **zaten kapalıydı** ve kapalı kalmalı: `corrected_q` yalnız
    deterministik yeniden yönlendirmenin girdisidir.

    ⚠ Kapı metin tarar çünkü koruduğu şey bir **çağrı şekli**: `_select_consistent`'e
    `corrected_q` geçirmek tek kelimelik bir düzenlemedir ve hiçbir tip denetimi
    yakalamaz."""
    import pathlib

    from app.routers import ask as ask_mod

    src = pathlib.Path(ask_mod.__file__).read_text(encoding="utf-8")
    cagri = src[src.index("_select_consistent(\n"):][:400]
    assert "corrected_q" not in cagri, (
        "🔴 düzeltilmiş soru sağlayıcıya gidiyor — `value_index`'in çözdüğü GERÇEK "
        "katalog adı hava boşluğunu ham geçer")
