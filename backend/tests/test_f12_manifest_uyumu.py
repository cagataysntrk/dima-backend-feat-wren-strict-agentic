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


def test_SERVIS_EDILEN_manifest_UYUMLU_kalir(manifest_b64):
    """Bugün **servis edilen** manifest (`off`/`shadow`) v2-uyumlu — ve öyle kalmalı.

    ⚠ Bu test `on`'u **artık kapsamıyor**; sebebi aşağıdaki testte ölçüldü."""
    import json

    from wren_core import is_backward_compatible

    from app import rls
    ham = base64.b64decode(manifest_b64)
    for kademe in ("off", "shadow"):
        islenmis, n = rls.manifeste_yaz(ham, kademe=kademe)
        assert n == 0, f"{kademe} kademesi manifeste YAZMAMALI — {n} kural yazdı"
        b = islenmis if isinstance(islenmis, bytes) else islenmis.encode()
        json.loads(b)                                   # bozulmamış JSON
        assert is_backward_compatible(base64.b64encode(b).decode()) is True, kademe


def test_RLAC_ENJEKSIYONU_v2_UYUMUNU_BOZUYOR(manifest_b64):
    """🔴🔴 **⑦ `motor_rls` AÇILAMAZ — ve bu artık bir tahmin değil, ÖLÇÜM.**

    ## Bu kapı neden KÖRDÜ

    Önceki sürüm (`test_RLS_UYGULANMIS_manifest_de_UYUMLU`) `shadow` **ve** `on` için
    `True` iddia ediyordu ve yeşildi. Ama **boş bir yeşildi**: varsayılan tenant
    (`demo-boyahane`) hiçbir cube'da `always_filter` beyan etmiyor, yani `manifeste_yaz`
    her iki kademede de **bayt bayt aynı** manifesti döndürüyordu. Test *«RLS uygulanmış
    manifest»* diyordu ama RLS **hiç uygulanmamıştı**.

    ⊙ Ve `app/rls.py`'nin kendi docstring'i bu körlüğü **zaten adlandırmıştı**:
    *«801 yeşil test bunu YAKALAMADI… `alwaysFilter` yalnız gulteks'te var (logo-3
    tenant'ı) ve süit o tenant'ın ham SQL yolunu ölçmüyor.»*

    ## Ölçüm (2026-08-12) — izole, taze derlenmiş **gulteks** projesi

    | manifest | kural | `is_backward_compatible` |
    |---|---|---|
    | ham | 0 | ✅ `True` |
    | `shadow` | 0 | ✅ `True` |
    | 🔴 **`on`** | **3** (`cari`·`mal`·`ticaret`, hepsi `CANCELLED = 0`) | 🔴 **`False`** |

    Kontrol izole: **aynı** manifest, yalnız enjeksiyon farkı. Ve kusur **varsayılan**
    manifestte de yeniden üretiliyor (tek yapay `always_filter` → 1 kural → `False`) —
    yani bulgu tenant'a değil **enjeksiyonun kendisine** bağlı.

    ## 🔴 SONUÇ: borç ⑦'nin şekli ÜÇÜNCÜ KEZ değişti

    | ne zaman | iddia |
    |---|---|
    | ilk | *«bayrak kapalı, açılmalı»* |
    | ikinci | *«eksik olan bayrak değil KURAL»* (⊘ — kural gulteks'te **var**) |
    | 🔴 **üçüncü, ölçülmüş** | kural **var**, bayrak **`shadow`**; ama açmak manifesti **v2-uyumsuz** yapıyor |

    ⚠ Ve bu tam olarak F12 kartının *«bir gün RLS enjeksiyonu manifesti v2-uyumsuz hâle
    getirirse kapı **bayrağı açmadan önce** konuşur»* cümlesinin gerçekleşmesidir. Kapı
    konuşamamıştı çünkü **kural olmayan tek tenant'a** bakıyordu.

    > *Bir ön koşul kapısını, koşulun oluşamadığı yerde koşmak; kapıyı kurmakla onu
    > kurmamak arasındaki farkı yok eder.*

    ## Bu test bir kusuru DONDURMUYOR

    `False` bugünkü **ölçülmüş** gerçektir. `True` olduğu gün bu test kırılır ve o gün
    ⑦'nin engeli kalkmış demektir — pilot o zaman anlamlıdır.
    """
    import json

    from wren_core import is_backward_compatible

    from app import rls

    man = json.loads(base64.b64decode(manifest_b64))
    modeller = {m.get("name") for m in man.get("models") or []}
    hedef = next((c for c in (man.get("cubes") or [])
                  if (c.get("base_object") or c.get("baseObject")) in modeller), None)
    assert hedef is not None, (
        "⊘ ölçüm tabanı çöktü: manifestte modele bağlı hiçbir cube yok — bu test o hâlde "
        "hiçbir şey ölçmüyor demektir.")
    hedef["always_filter"] = "1 = 1"

    islenmis, n = rls.manifeste_yaz(
        json.dumps(man, ensure_ascii=False).encode(), kademe="on")
    assert n >= 1, "⊘ enjeksiyon çalışmadı — kapı yine kör olurdu"

    uyum = is_backward_compatible(base64.b64encode(islenmis).decode())
    assert uyum is False, (
        "✅ RLAC enjeksiyonu artık v2 uyumunu BOZMUYOR — `motor_rls` borcunun (⑦) "
        "ölçülmüş engeli kalktı.\n"
        "Sıradaki adım: `motor_rls: \"on\"` pilotu. Ölçülmesi gerekenler:\n"
        "  ① `demo-boyahane` bayt bayt AYNI kalır (0 kural — KURAL B)\n"
        "  ② `gulteks`te JOIN ve Discovery ham-SQL baypasları KAPANIR\n"
        "  ③ `_inject_always_filter` devrettiği cube'larda yüklemi İKİ KEZ yazmaz\n"
        "Ve bu testin iddiası ölçümle güncellensin — bir kayıt, ölçümü değişince yenilenir.")


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
        f"🔴 VARSAYILAN tenant'ta RLS artık {n} kural enjekte ediyor (önce 0'dı).\n"
        "⚠ Bu, kuralın *hiç yokluğu* demek DEĞİLDİR ve öyle okunmamalıdır: ölçüldü "
        "(2026-08-12), `gulteks` (logo-3) üç cube'da `always_filter` beyan ediyor ve "
        "`rls(on)` orada **3 kural** yazıyor. Buradaki `0` yalnız `demo-boyahane`nin "
        "kataloğunun bir özelliğidir.\n"
        "Borç ⑦'nin gerçek engeli `test_RLAC_ENJEKSIYONU_v2_UYUMUNU_BOZUYOR`'da yazılı.")
