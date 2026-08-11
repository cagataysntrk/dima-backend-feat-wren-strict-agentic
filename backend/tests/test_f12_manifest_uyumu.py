"""🔴 `§F12` — MOTORUN MANİFEST API'Sİ: BİRİ **İŞE YARIYOR**, ÖTEKİ **SORUNSUZ**.

## Kartın vaadi

> `Manifest` · `to_manifest` · `migrate_manifest_json` · `is_backward_compatible` —
> `compose.py` + `mdl_writer.py`'nin manifest kısmı (**~1.490 satır**). ⊙ Özellikle
> **`migrate_manifest_json`** — pack sürümü değişince **göç bedava**.

## Ölçüm (2026-08-12, canlı manifest 197.734 bayt)

| API | sonuç |
|---|---|
| **`is_backward_compatible`** | ✅ **`True`** — hem temiz hem **RLS uygulanmış** manifestte |
| `migrate_manifest_json` | ⊘ *«Cannot migrate to layout version 5: maximum supported version is 4»*, base64'te de *«JSON error»* — **girdi biçimi tutarsız** |
| beş projenin `schema_version` | **hepsi 5** — göçülecek bir **sürüm farkı YOK** |

⚠ Ve `wren_project.yml`'deki `schema_version: 5` ile motorun *«layout version»*'ı **aynı
şey olmayabilir**; ikisini denk saymak ölçülmemiş bir eşitlik kurmak olurdu. Bu yüzden
`migrate_manifest_json` için **hiçbir iddia yazılmadı**.

## 🔴 KARAR: göç YAPILMIYOR — çözecek bir sorun yok

*«Göç bedava»* ancak **göçülecek bir şey varsa** bir kazançtır. Beş proje de tek
sürümde; API'nin girdi biçimi belgesizce çelişiyor. Ölçüye dayanan **on üçüncü**
*«yapma»*. ⊙ Bir gün motor layout'u yükseltirse bu karar yeniden okunur — kapı
sürümlerin **tekliğini** kilitliyor, yani ayrışma sessizce olamaz.

## ✅ AMA YARISI HEMEN DEĞERLİ — ve açık bir borca bağlanıyor

`is_backward_compatible` *«erişim denetimi kuralları varsa v2 çekirdek bunu
kullanabilir mi»* sorusunu cevaplıyor — yani **`motor_rls` borcunun** (⑦) ön koşulu.
Bugün `True`; bir gün RLS enjeksiyonu manifesti v2-uyumsuz hâle getirirse kapı
**bayrağı açmadan önce** konuşur.

## 🔴 VE ÖLÇÜM `motor_rls` BORCU HAKKINDA BİR ŞEY DAHA SÖYLEDİ

    rls(shadow) → 0 kural · rls(on) → 0 kural

Demo katalogda RLS **hiç kural enjekte etmiyor**. Yani `motor_rls`'i açmak bu tenant'ta
**hiçbir şey değiştirmezdi** — daha önce ölçülen *«`shadow ≡ off`»* bulgusunun sebebi de
budur. ⊙ Borç ⑦ kapanmadı ama **şekli değişti**: eksik olan bayrak değil, **kural**.
*Bir korumayı açmadan önce, koruyacak bir şeyi olduğunu ölçmek gerekir.*
"""

from __future__ import annotations

import base64
import pathlib

import pytest
import yaml

_DEMO = pathlib.Path(__file__).parent.parent / "demo"


@pytest.fixture(scope="module")
def manifest_b64(schema) -> str:  # noqa: ARG001 — şema fikstürü derlemeyi garanti eder
    from app.config import get_settings
    from app.wren_service import WrenService
    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    return base64.b64encode(svc._mdl_bytes()).decode()


def test_MANIFEST_v2_cekirdekle_UYUMLU(manifest_b64):
    """✅ `motor_rls` borcunun ön koşulu. Bugün `True`; bozulursa bayrak açılmadan önce
    bu kapı konuşur."""
    from wren_core import is_backward_compatible
    assert is_backward_compatible(manifest_b64) is True


def test_RLS_UYGULANMIS_manifest_de_UYUMLU(manifest_b64):
    """Enjeksiyonun kendisi uyumu bozmamalı — *bir korumanın bedeli, korumanın
    kullanılamaz hâle gelmesi olamaz.*"""
    import json

    from wren_core import is_backward_compatible

    from app import rls
    ham = base64.b64decode(manifest_b64)
    for kademe in ("shadow", "on"):
        islenmis, _ = rls.manifeste_yaz(ham, kademe=kademe)
        b = islenmis if isinstance(islenmis, bytes) else islenmis.encode()
        json.loads(b)                                   # bozulmamış JSON
        assert is_backward_compatible(base64.b64encode(b).decode()) is True, kademe


def test_TUM_PROJELER_TEK_SURUMDE():
    """🔴 Göç kararının dayanağı: ayrışma **yok**. Bir gün ayrışırsa bu kapı kırılır ve
    `migrate_manifest_json` kararı **yeniden okunur**."""
    surumler = {}
    for p in _DEMO.rglob("wren_project.yml"):
        d = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        if "schema_version" in d:
            surumler.setdefault(str(d["schema_version"]), []).append(p.parent.name)
    assert surumler, "hiç proje dosyası bulunamadı"
    assert len(surumler) == 1, (
        f"🔴 proje sürümleri AYRIŞTI: {surumler}\n"
        "`§F12`'nin *«göç yapılmıyor»* kararı **çözecek bir sorun yok**a dayanıyordu; "
        "artık var. `migrate_manifest_json` yeniden değerlendirilmeli.")


def test_RLS_KURAL_SAYISI_kayitli(manifest_b64):
    """🔴 Borç ⑦'nin **şeklini** kilitler: bugün demo katalogda RLS **sıfır** kural
    enjekte ediyor — yani `motor_rls`'i açmak burada hiçbir şey değiştirmezdi.
    Kural yazıldığı gün bu test konuşur ve pilot gerçekten ölçülebilir hâle gelir."""
    from app import rls
    ham = base64.b64decode(manifest_b64)
    _, n = rls.manifeste_yaz(ham, kademe="on")
    assert n == 0, (
        f"🔴 RLS artık {n} kural enjekte ediyor (önce 0'dı).\n"
        "Borç ⑦ ölçülebilir hâle geldi: `motor_rls` pilotu ARTIK ANLAMLI — "
        "`is_backward_compatible` yeşilken kademeli aç ve JOIN + Discovery baypaslarını "
        "canlı curl ile doğrula.")
