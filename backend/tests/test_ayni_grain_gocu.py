"""FAZ 2.4 — **AYNI-GRAIN ÇİFTLERİNİ MERCEĞE İNDİR.** [bayrak: `ayni_grain_gocu`]

`surdurulebilirlik` ile `parti` **aynı `base_object`** üstünde (`partiler`) — iki cube,
tek grain. Yoğunluk ölçüleri `parti` grain'ine ait **metriklerdir**; `surdurulebilirlik`
bir **mercek** olarak yaşamalı.

## 🔴 AMA KİMLİK SİLİNMEZ — ve bu ÖLÇÜLMÜŞ bir karardır

Ham kaynak adlarını `surdurulebilirlik`'in kimliğinden çıkarmak *"yanlış cube 245 → 135"*
getirdi **ama** erişimi **%64 → %56** düşürdü ve `test_eval_gate`'i kırdı — çünkü **ölçü
düzeyinde sahiplik ÇÖZÜLMEDİ**: iki cube da `elektrik` iddia ediyor → `_match_cube`
hiçbirini seçemiyor → `R1`.

*Doğru çözüm bir **SAHİPLİK KARARIDIR**, kimlik silmek değil* — ve o hakem **FAZ 2.2b**'de
indi (`MetrikSahipligi` + `metrik_kaydi.hakem`). Bu madde yalnız **çifti beyan eder**;
çözüm hakemin işidir.
"""

from __future__ import annotations

import pathlib

import yaml

KOK = pathlib.Path(__file__).resolve().parents[1]
_YOL = (KOK / "demo" / "packs" / "sektor" / "boyahane" / "cubes"
        / "surdurulebilirlik" / "metadata.yml")


def _meta() -> dict:
    return yaml.safe_load(_YOL.read_text(encoding="utf-8")) or {}


def test_AYNI_GRAIN_CIFTI_BEYAN_EDILDI():
    """🔴 Çift **görünür** olmalı: iki cube'un aynı grain'de olduğunu hiçbir yerde beyan
    etmemek, tam olarak `ticaret` sürüklenmesinin doğuş biçimiydi."""
    m = _meta()
    assert m.get("ayni_grain") == "parti", "aynı-grain çifti BEYAN EDİLMEMİŞ"
    parti = yaml.safe_load(
        (_YOL.parent.parent / "parti" / "metadata.yml").read_text(encoding="utf-8")) or {}
    assert m.get("base_object") == parti.get("base_object") == "partiler", (
        "beyan ile GERÇEK ayrışmış — beyan var, kod onu tanımıyor")


def test_KIMLIK_SILINMEDI():
    """🔴 **Bu test bir düzeltmeyi değil, bir GERİ ALMAYI korur.** `elektrik` deneyi
    (%64→%56) ikinci kez yapılmamalı. Kardeşi `test_SURDURULEBILIRLIK_kimligi_KORUNUYOR`
    şemadan doğrular; bu, **pack kaynağından**."""
    syn = {str(s).lower() for s in (_meta().get("synonyms") or [])}
    assert "elektrik" in syn, (
        "ham kaynak adı kimlikten çıkarılmış — ÖLÇÜLDÜ ve erişimi düşürdü "
        "(%64→%56, eval_gate kırmızı). Sahipliği çözmeden kimliği silme.")


def test_MERCEK_OLARAK_ISARETLENDI():
    """`departman` alanı, `2.3`'ün merceğinin bu cube'u daraltabilmesi için gerekli —
    **kimliği silmeden** kapsam dışına alınabilmesinin tek yolu budur."""
    assert _meta().get("departman") == "surdurulebilirlik"


def test_COZUM_YOLU_HAKEM_OLARAK_YAZILI():
    """⚠ Bir sonraki tur *"kimliği neden hâlâ silmedik"* diye sormamalı: çözümün **sahiplik
    kararı** olduğu, dosyanın kendisinde yazılı."""
    ham = _YOL.read_text(encoding="utf-8")
    assert "SAHİPLİK KARARIDIR" in ham and "2.2b" in ham


def test_AYRI_BAYRAK():
    """⚠ **Denetim düzeltmesi:** sürüm 1'de bu madde `cekirdek_katman` bayrağını
    paylaşıyordu → `2.4`'ü geri almak `2.1`'i de geri alırdı. Ayrı bayrak."""
    from app.features import FLAG_REGISTRY

    assert "ayni_grain_gocu" in FLAG_REGISTRY
    aciklama = FLAG_REGISTRY["ayni_grain_gocu"]["description"]
    assert "AYRI bayrak" in aciklama, "ayrılığın GEREKÇESİ yazılı değil"


def test_HAKEM_HAZIR_ama_KARAR_VERILMEMIS():
    """🔴 **Zincir tamam ama tetik çekilmedi — ve bu bilinçli.** `elektrik`'in sahibini
    seçmek bir **iş kararıdır** (hangi cube'un metriği?), bir kod kararı değil. Hakem
    hazır (`2.2b`), karar ekranı hazır; sahiplik **boş** olduğu sürece davranış
    **bugünküyle birebir aynı**.

    *Kullanıcının vermesi gereken bir kararı sistemin vermesi, tam olarak bu maddenin
    ölçülmüş kusurudur.*
    """
    from app import metrik_kaydi as mk

    assert mk.hakem("elektrik", []) is None
    assert mk.hakem("elektrik", [{"terim": "elektrik", "adaylar": ["parti", "surdurulebilirlik"],
                                  "sahiplenilen_terimler": []}]) is None
