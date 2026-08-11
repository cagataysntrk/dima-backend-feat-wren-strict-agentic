"""🔴 `§F5` — *«MOTORDA OLANI YENİDEN YAZAN ~2.000 SATIR»* ÖLÇÜLDÜ VE RAKAM ÇÜRÜDÜ.

## Raporun iddiası (`§16.3` · `§14` F5)

| varlık | büyüklük | rapordaki gerekçe |
|---|---|---|
| `rls.py` | **380** | *«`wren_core.RowLevelAccessControl` + `validate_rlac_rule` motorun içinde duruyor, **hiç kullanılmadı**»* |
| `dataset.py` | **161** | *«`SessionContext.register_csv` / `register_parquet` **var**»* |
| manifest | **~1.490** | `Manifest` · `to_manifest` · `migrate_manifest_json` **var** |

## Ölçüm (2026-08-11)

🔴 **`rls.py` BOŞA GİTMİŞ DEĞİL — TAM TERSİ.** Dosyanın kendi ilk satırı: *«FAZ 1.1 —
**MOTOR-SEVİYESİ RLS.** `always_filter`'ın yerini **motor devralır**»*. Yani bu 380 satır
motorun işini tekrar etmiyor; **işi motora devreden göçün kendisi**. Ve bağlı:
`wren_service.py`'de **sekiz** çağrı yeri (`manifeste_yaz` · `cls_manifeste_yaz` ·
`clac_manifesti` · `rlac_manifesti` · `motorun_devraldigi_cubelar` ·
`en_kisitli_ozellikler` · `KADEMELER` ×2) + `istek_kimligi.py`. İki kapı dosyası var
(`test_motor_rls.py` · `test_motor_rls_onkosul.py`).

⊙ *«`RowLevelAccessControl` sembolü çağrılmamış»* **sembol düzeyinde doğru, yetenek
düzeyinde yanıltıcı**: RLS motora **manifest üzerinden** verilir — motorun kendi belgeli
girdi yolu budur. `rlac_manifesti()` tam olarak onu yapar.

🔴 **`dataset.py`'de `register_csv` FARKLI BİR İŞ YAPIYOR.** 161 satırın dökümü:

    ingest_file    42   ← `register_csv`'nin YAKLAŞTIĞI tek parça
    build_mdl      28   ← oto-MDL/cube üretimi — motorda karşılığı YOK
    _role/_mdl_type/_syns/_slug/_base_type  33  ← kolon ROLÜ + Türkçe sinonim
    build_service   8 · _connect 5

Ve `ingest_file` bile birebir değiştirilemez: **Excel** okur (`read_xlsx`), kolonları
**slug**'lar (docstring'in kendi güvenlik gerekçesi: *«tırnak/enjeksiyon derdi yok»*) ve
açık bir `SELECT` listesi kurar. `register_csv` bunların **hiçbirini** yapmaz.

🔴 **Manifest ~1.490 `F5`'in değil `F12`'nin kalemi** — ve `F12` bir **silme** değil
*«motorun daha fazlasını kullan»* maddesidir.

## Ve raporun kendisi bunu zaten işaretlemiş

`§11.6` sonu: *«§16.4'ün «açıkça boşa giden ~2.000 satır» rakamı bu ışıkta **yeniden
okunmalı**: boşa giden kod değil, **bağlanmamış kod**.»* Bu ölçüm o cümleyi doğruluyor.

## 🔴 F5'İN AÇIĞA ÇIKARDIĞI GERÇEK BORÇ

`rls.py` **ödenmiş, bağlanmış, kapılı** — ama `motor_rls`/`motor_cls` bayrakları
**kapalı** (`features.yml`'nin kendi notu: *«motor-RLS hiç açık değil»*). Yani iki ölçülmüş
baypas (JOIN · Discovery ham SQL) **hâlâ açık**. Bu bir *silme* işi değil, bir
**teslim etme** işidir — ve bir güvenlik sınırı değiştirdiği için kendi ölçülmüş pilotunu
ister (⚠ `shadow` kademesi ölçülmüştü: `shadow ≡ off`).

*Bir kod parçasını «boşa gitmiş» ilan etmek ucuzdur; onun ne yaptığını okumak
pahalıdır — ve bu depoda silme kararı hep ikincisinden çıktı.*
"""

from __future__ import annotations

import ast
import pathlib

APP = pathlib.Path(__file__).parent.parent / "app"


def _kaynak(ad: str) -> str:
    return (APP / ad).read_text(encoding="utf-8")


def test_RLS_BAGLI_silinemez():
    """🔴 Kaza koruması: eskimiş `§16.3` satırına dayanıp `rls.py` silinirse iki ölçülmüş
    baypas (JOIN · Discovery ham SQL) geri açılır. Bu test çağrı yerlerini sayar."""
    ws = _kaynak("wren_service.py")
    cagrilar = [a for a in ("rls.manifeste_yaz", "rls.cls_manifeste_yaz",
                            "rls.clac_manifesti", "rls.rlac_manifesti",
                            "rls.motorun_devraldigi_cubelar", "rls.KADEMELER")
                if a in ws]
    assert len(cagrilar) >= 6, f"rls.py'nin tüketicileri azaldı: {cagrilar}"


def test_RLS_motora_MANIFEST_uzerinden_veriliyor():
    """*«`RowLevelAccessControl` sembolü çağrılmamış»* iddiasının cevabı: RLS motora
    manifest üzerinden verilir ve `rlac_manifesti` tam olarak onu yapar."""
    src = _kaynak("rls.py")
    adlar = {n.name for n in ast.walk(ast.parse(src))
             if isinstance(n, ast.FunctionDef)}
    for f in ("rlac_manifesti", "clac_manifesti", "manifeste_yaz", "cls_manifeste_yaz"):
        assert f in adlar, f"{f} kayboldu — motor-RLS göçü bozulmuş olabilir"


def test_DATASET_register_csvnin_YAPMADIGI_isi_yapiyor():
    """`register_csv` bir CSV'yi tablo olarak kaydeder. `dataset.py` ayrıca **oto-MDL**
    üretir, kolon **rolü** çıkarır, Türkçe **sinonim** yazar ve **Excel** okur."""
    src = _kaynak("dataset.py")
    adlar = {n.name for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef)}
    for f in ("build_mdl", "_role", "_syns", "_slug"):
        assert f in adlar, f"{f} yok — dataset.py'nin motorda karşılığı olmayan kısmı bu"
    assert "read_xlsx" in src, "Excel yolu — `register_csv` bunu yapamaz"


def test_MOTOR_SEMBOL_sayisi_KAYITLI():
    """⚠ Rapor *«`wren_core` 15 sembol»* diyor; ölçülen **14**. Bir sayı, sayıldığı anın
    fotoğrafıdır — ve bu test onu tazeler."""
    import wren_core
    syms = {s for s in dir(wren_core) if not s.startswith("_")}
    assert {"cube_query_to_sql", "SessionContext", "RowLevelAccessControl",
            "ManifestExtractor", "to_manifest", "migrate_manifest_json"} <= syms
    assert len(syms) == 14, f"motor yüzeyi değişti ({len(syms)}) — F5/F12 yeniden okunmalı"
