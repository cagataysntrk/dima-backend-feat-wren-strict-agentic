"""🔴 `§C1` — İKİ KAYIT VAR, AMA **BİRİ CANLI BİRİ UYKUDA**; BİRLEŞTİRME ŞİMDİ DEĞİL.

## Raporun isteği

> `FIIL_ANLAMI` **`tools.py`'den üretilir** (plan-bestelenebilir araçlar süzülerek).
> Kapalı `enum` **korunur** — yalnız artık **türetilmiş** olur. Kazanç: tek kayıt
> (`KAT-1`).

İlke doğru ve bu depoda bağlayıcı. Soru **ne zaman** ödeneceği.

## Ölçüm (2026-08-12)

| | ölçülen |
|---|---|
| `FIIL_ANLAMI` | **15 fiil** — ✅ raporla aynı |
| `tools` kaydı | **25 araç** — ✅ raporla aynı |
| `FIIL_ANLAMI` **canlı mı** | 🔴 **EVET**: `plan_garson.py:284` her planlayıcı çağrısında `plan_json_schema(index)` kuruyor; `plan_tuketici.py:1216` anlamları makbuza yazıyor |
| `tools` kaydı **canlı mı** | ⊘ **HAYIR (plan yolunda)**: tek iki tüketicisi `mcp.py` (`mcp_yuzeyi: "off"` → 404) ve `Planlayici.sec()` (`agent_plan_secimi: "off"`) |
| adlar örtüşüyor mu | 🔴 **HAYIR**: `SORGU`/`AYRISTIR`/`GORSEL` ↔ `route`/`contribution.decompose`/`viz.recommend` |

⚠ **Raporun *«örtüşme %73»* rakamına DOKUNMUYORUZ:** o **anlamsal** bir eşleştirmedir
(*«15 fiilin 11'inin araç ikizi var»*), ad benzerliği değil. Kaba bir ad eşlemesi %26
verdi ve bu **raporu çürütmez, yalnız o aracın anlamsal eşleştirmeyi ölçemediğini
gösterir**. *Kaba bir ölçü, ölçemediği bir iddiayı çürütemez* — bu turda yedinci kez.

## 🔴 KARAR: ŞİMDİ YAPILMIYOR — ve gerekçe üç ölçüme dayanıyor

1. **Canlı kaydı uykudaki kayıttan türetmek olurdu.** `tools.py`'nin plan yolundaki iki
   tüketicisi de bayrakla **kapalı**. Riski canlı yol taşır, faydayı kapalı yol taşır.
2. **Kullanıcı hiçbir şey hissetmez** — kartın kendi notu: `KURAL B` gereği davranış
   **bayt bayt** aynı kalacak. Kullanıcının bu oturumdaki uyarısı: *«ölçüm/altyapı
   tesisatı ürün değildir»*.
3. **Adlar örtüşmediği için türetim bir EŞLEME TABLOSU ister** — yani iki kayıt yerine
   **üç** şey: fiiller, araçlar, ve aralarındaki eşleme. `KAT-1` adına yapılan bir işin
   üçüncü bir kaydı doğurması, ilkeyi ilkenin adıyla çiğnemek olurdu.
   ⊙ Doğru biçim: her araç **kendi fiilini beyan eder** (`fiil` alanı) ve `FIIL_ANLAMI`
   ondan türetilir. Ama o beyan, araçların **canlı** olduğu gün yazılmalı.

## ⚠ VE BORÇ KENDİNİ TOPLUYOR

Aşağıdaki test, iki bayraktan biri açıldığı gün **kırmızı** olur. O gün iki kayıt da canlı
olacak ve ayrışmaları gerçek bir risk hâline gelecek — `C1` tam o anda ödenmeli.

*Bir borcu ertelemek, onu unutmak değildir — eğer erteleme kendi alarmını kuruyorsa.*
"""

from __future__ import annotations

import pathlib

import yaml

from app import tools
from app.plan_semasi import FIIL_ANLAMI

_PACK = pathlib.Path(__file__).parent.parent / "demo" / "packs" / "features.yml"


def _bayrak(ad: str) -> str:
    d = yaml.safe_load(_PACK.read_text(encoding="utf-8")) or {}
    for blok in (d.values() if isinstance(d, dict) else []):
        if isinstance(blok, dict) and ad in blok:
            return str(blok[ad])
    return str((d.get(ad) if isinstance(d, dict) else None) or "")


def test_IKI_KAYIT_bugun_de_AYRI():
    """Ölçümün tabanı: birleşme olmadı, sayılar kayıtlı."""
    assert len(FIIL_ANLAMI) == 15
    assert len(tools.KAYIT if hasattr(tools, "KAYIT") else tools.llm_araclari(None)) >= 15


def test_FIIL_KAYDI_CANLI():
    """`FIIL_ANLAMI` her planlayıcı çağrısında okunuyor — riski canlı yol taşır."""
    g = (pathlib.Path(__file__).parent.parent / "app" / "plan_garson.py").read_text(
        encoding="utf-8")
    t = (pathlib.Path(__file__).parent.parent / "app" / "plan_tuketici.py").read_text(
        encoding="utf-8")
    assert "plan_json_schema" in g, "fiil şeması artık kurulmuyor mu?"
    assert "FIIL_ANLAMI" in t, "fiil anlamları artık makbuza yazılmıyor mu?"


def test_BORC_KENDINI_TOPLUYOR():
    """🔴 **C1'in vadesi budur.** `tools` kaydının plan yolundaki iki tüketicisi de bugün
    bayrakla kapalı; biri açıldığında **iki kayıt da canlı** olur ve ayrışmaları gerçek
    bir risk hâline gelir. O gün bu test kırılır ve `C1` ödenir.

    ⚠ Ödeme biçimi kartta yazılı: her araç **kendi fiilini beyan eder**, `FIIL_ANLAMI`
    ondan **türetilir**, ve türetilmiş liste bugünküyle **bayt bayt** aynı çıkar
    (`KURAL B`; bayrak yok, çünkü davranış değişmemeli)."""
    acik = [ad for ad in ("mcp_yuzeyi", "agent_plan_secimi") if _bayrak(ad) != "off"]
    assert not acik, (
        f"🔴 {acik} AÇILDI — artık `tools` kaydı da canlı yolda.\n"
        "İki yetenek kaydı aynı anda canlı olamaz (`KAT-1`): `C1`'i şimdi öde —\n"
        "  ① her araca `fiil` alanı ekle (araç kendi fiilini BEYAN etsin)\n"
        "  ② `FIIL_ANLAMI`'nı ondan TÜRET\n"
        "  ③ türetilmiş liste bugünkü 15 fiille BAYT BAYT aynı çıksın (KURAL B)\n"
        "Gerekçe: bu ertelemeyi bir ölçüm verdi (`tests/test_c1_tek_yetenek_kaydi.py`),\n"
        "ve ertelemenin şartı tam olarak bu bayrakların kapalı kalmasıydı.")
