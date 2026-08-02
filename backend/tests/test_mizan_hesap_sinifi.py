"""FAZ D1 — `mizan`'ın kırılım boşluğu: hesap SINIFI hiç yoktu.

## Ölçülen boşluk

`mizan` cube'unun TEK kırılımı hesabın kendisiydi:

    dimensions: ['hesap_kodu', 'hesap_adi']      # 27 / 27 farklı — ikisi de AYNI grain

Yani bir muhasebecinin ilk soracağı sorular — *"gider hesaplarının toplamı"*, *"dönen
varlıklar bazında bakiye"*, *"aktif-pasif dengesi"* — deterministik yolda **cevapsızdı**.
Mizan gibi bir raporun asıl ekseni hesap değil hesap **sınıfıdır**; hesap kodu yalnız en
alt yapraktır.

## Neden bu ilişki, neden bu iki kolon

`yevmiye_satirlari → hesap_plani` ilişkisi ZATEN vardı (`hesap_adi` için kullanılıyordu);
eksik olan yalnız `expose:` bildirimiydi. İki kolon ölçülerek seçildi (2 Ağustos 2026):

| kolon | farklı değer | kapı |
|---|---|---|
| `hesap_tipi` | **4** (aktif · pasif · gelir · gider) | ✅ ayırt edici |
| `ana_grup` | **5** (Dönen/Duran Varlıklar, Kısa Vadeli Yab. K., …) | ✅ ayırt edici |
| `hesap_kodu` | 27 — zaten var | — |
| `hesap_adi` | 27 — zaten var | — |

Karşı örnek aynı dosyada kayıtlı: `partiler → tedarikciler` üzerinden `sehir`/`tur`
denenmiş ve **geri çekilmişti** (bu veri setinde kardinalite 1 — hiçbir şeyi ayırt etmiyor,
yalnız router'ın arama uzayını büyütüyor). Boyut eklemek bedava değildir.

Fan-out sertifikası (Faz D2) bu ilişki için `saglikli`: 27/27 benzersiz, 0 NULL, 0 öksüz.
"""

from __future__ import annotations

import pytest

from app.cube_router import route

YENI = ("hesap_tipi", "ana_grup")


def test_mizan_hesap_SINIFI_kirilimlarini_kazandi(schema):
    cube = next(c for c in schema["cubes"] if c["name"] == "mizan")
    for d in YENI:
        assert d in cube["dimensions"], f"{d} üretilmedi"


@pytest.mark.parametrize("soru,dim,olcu", [
    ("mizan hesap tipine göre bakiye", "hesap_tipi", "bakiye"),
    ("yevmiye hesap türüne göre alacak", "hesap_tipi", "toplam_alacak"),
    ("mizanda ana gruba göre borç", "ana_grup", "toplam_borc"),
    ("hesap grubuna göre mizan bakiyesi", "ana_grup", "bakiye"),
])
def test_deterministik_yolda_CEVAPLANIYOR(schema, soru, dim, olcu):
    """ASIL KAZANÇ: bu sorular eskiden `route()`'tan `None` dönüp LLM'e düşüyordu."""
    cq = (route(soru, schema) or {}).get("cube_query") or {}
    assert cq.get("cube") == "mizan", f"cube eşleşmedi: {cq.get('cube')}"
    assert cq.get("dimensions") == [dim]
    assert cq.get("measures") == [olcu]


def test_uretilen_SQL_ilişki_kolonunu_kullanir():
    """Boyut ilişki-türevidir: SQL `hesap_plani`'ndan gelen calc kolonu kullanmalı —
    cube derleyicisi JOIN YAZMAZ, kolon MDL'de hazır olmalıdır (MIMARI §3.2)."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    sql = svc.cube_sql({"cube": "mizan", "measures": ["bakiye"],
                        "dimensions": ["hesap_tipi"], "filters": []})
    assert "hesap_plani_hesap_tipi" in sql
    assert "join" not in sql.lower(), "cube derleyicisi JOIN üretmemeli"


def test_koken_SERTIFIKALI(schema):
    """Yeni boyutlar Faz D2 sertifikasını taşımalı — kırılım güveni ölçülmüş olmalı."""
    cube = next(c for c in schema["cubes"] if c["name"] == "mizan")
    org = cube.get("dimension_origin") or {}
    for d in YENI:
        assert d in org, f"{d} köken taşımıyor"
        assert org[d].get("relationship") == "yevmiye_satirlari_hesap_plani"
        assert org[d].get("certified") in ("olculdu:saglikli", "olculmedi")


def test_ETIKET_mevcut_sozlugu_CALMADI(schema):
    """ADR-0018 LABEL ⊆ SYNONYM: etiket kelimelerine ayrılıp sinonim doğurur. `hesap tipi`
    yazmak `hesap` sinonimi üretir ve mizan'ın MEVCUT `hesap_kodu`/`hesap_adi` sözlüğüyle
    çakışırdı (aynı soru iki boyut eşleştirir, GROUP BY bölünür). Bu yüzden etiketler TEK
    KELİME; çok kelimeli ifadeler `synonyms:` altındadır (onlar bölünmez)."""
    cube = next(c for c in schema["cubes"] if c["name"] == "mizan")
    syn = cube.get("dimension_synonyms") or {}
    for d in YENI:
        assert "hesap" not in (syn.get(d) or []), \
            f"{d} çıplak 'hesap' sinonimi doğurdu — hesap_kodu/hesap_adi ile çakışır"
    from app.cube_router import _match_dims, _norm

    assert _match_dims(_norm("hesap kodu bazında bakiye"), cube) == ["hesap_kodu"], \
        "yeni boyutlar mevcut hesap kırılımını böldü"
