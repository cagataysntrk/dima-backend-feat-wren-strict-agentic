"""🔴 `§38.2 D7` — PLAN ÇALIŞTIRICISI **SALT-OKUNUR**; yetki boşluğu YOK.

## Raporun vaadi ve ölçüm

`§38.2 D7` şöyle diyordu: *«plan fiilleri `authorize()` GÖRMÜYOR → kayıt birleşince
yetki süzgeci plana bedava gelir»*. Bir denetim ajanı bunu bir **eksik** olarak
bildirdi (`grep authorize app/plan_semasi.py app/plan_kosucu.py` → **0**).

⊙ Ölçüm doğruladı: plan fiilleri `Planlayici.calistir()`'den **geçmiyor**;
`plan_kosucu.kos` onları doğrudan sevk ediyor (`if fiil == "SORGU": …`).

## 🔴 AMA BU BİR YETKİ BOŞLUĞU DEĞİL — ve sebebi yapısal

Ölçüldü (2026-08-12), her fiilin ne yaptığı:

| fiil | ne yapar | yetki riski |
|---|---|---|
| `SORGU` | `sorgu_kos` — isteğin **zaten yetkilendirilmiş** servisi | yok |
| `BAGLA`·`HESAPLA`·`MATRIS`·`SIRALA`·`KIR`·`SUZ`… | **koşmuş satırlar** üstünde saf dönüşüm | yok |
| `PANO` | **YAZMAZ** — `pano_taslagi` döndürür; kalıcılaştırma onayla, dışarıda | yok |
| `RAPOR`·`ANLAT` | metin üretir | yok |

⊙ Yani çalıştırıcı **salt-okunur ve idempotent**; bir plan, kullanıcının kendi
isteğiyle erişemeyeceği hiçbir şeye ulaşamaz. `authorize()` çağrısının yokluğu bir
**boşluk değil**, gereksizlik.

> *Bir kapının yokluğu ancak arkasında bir şey varsa boşluktur.*

## 🔴 GERÇEK DEĞİŞMEZ BUYDU — ve yalnız bir YORUMDA duruyordu

`plan_kosucu.py`'nin `PANO` dalı şunu yazıyor: *«🔴 **YAZMAZ.** Çalıştırıcı salt-okunur
ve idempotent kalıyor; **ilk yan etkili fiil bu değişmezi kırardı** (yarım pano ·
ikilenen pano · geri alınamayan yazma).»*

⚠ O cümle doğru ama **kapısızdı**: yarın yan etkili bir fiil eklenirse `authorize()`
yokluğu **gerçek** bir boşluğa döner ve hiçbir kırmızı konuşmaz.

✅ Bu dosya o değişmezi ölçüyor. *Yazılmış ama korunmayan bir değişmez, bir temennidir.*
"""

from __future__ import annotations

import ast
import pathlib

_APP = pathlib.Path(__file__).parent.parent / "app"
_KOSUCU = _APP / "plan_kosucu.py"


def _agac() -> ast.AST:
    return ast.parse(_KOSUCU.read_text(encoding="utf-8"))


def test_CALISTIRICI_ROUTER_ITHAL_ETMIYOR():
    """🔴 Yazma yüzeyi `app/routers/*`tadır. Çalıştırıcı oraya **dokunmaz**.

    ⚠ Yüklem `ast` ile kurulu (kaba `grep` docstring'leri de yakalardı — bu deponun
    ölçülmüş dersi)."""
    ithal = set()
    for n in ast.walk(_agac()):
        if isinstance(n, ast.Import):
            ithal |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            ithal.add(n.module)
    kacak = sorted(x for x in ithal if x.startswith("app.routers"))
    assert not kacak, (
        f"🔴 `plan_kosucu` bir ROUTER ithal ediyor: {kacak}. Çalıştırıcı salt-okunur "
        "olmalı; yazma yüzeyi onay akışının (`POST /ask/eylem`) arkasındadır.")


def test_YAZMA_ARACLARI_CALISTIRICIDA_ANILMIYOR():
    """Yazma araçlarının adı bile çalıştırıcıda geçmemeli — geçiyorsa bir gün çağrılır."""
    kaynak = _KOSUCU.read_text(encoding="utf-8")
    from app import eylem as _e

    yazma_adlari = {b.uc.split(".")[-1] for b in _e.EYLEM_KAYIT}
    kacak = sorted(a for a in yazma_adlari if a and a in kaynak)
    assert not kacak, (
        f"🔴 çalıştırıcıda yazma fonksiyonu adı geçiyor: {kacak}. "
        "*İlk yan etkili fiil, salt-okunurluk değişmezini kırar.*")


def test_PANO_TASLAK_DONDURUYOR_KALICILASTIRMIYOR():
    """`PANO` bir **taslaktır**; kalıcılaştırma onay akışının işidir.

    ⊙ Bu, `§F13`'ün kararıyla aynı: ajan **önerir**, kullanıcı **onaylar**."""
    kaynak = _KOSUCU.read_text(encoding="utf-8")
    i = kaynak.index('if fiil == "PANO"')
    govde = kaynak[i:i + 500]
    assert "pano_taslagi" in govde, (
        "🔴 `PANO` artık taslak döndürmüyor — kalıcılaştırıyor olabilir.")
    assert "YAZMAZ" in govde, "salt-okunurluk beyanı silinmiş"


def test_DEGISMEZ_YAZILI_ve_GEREKCELI():
    """Beyan kültürü: değişmez **yazılı** olmalı ki bir gün kırılırsa fark edilsin."""
    kaynak = _KOSUCU.read_text(encoding="utf-8")
    assert "salt-okunur" in kaynak and "idempotent" in kaynak, (
        "🔴 salt-okunurluk değişmezi metinden silinmiş — bir değişmez, yazılı "
        "değilse bir alışkanlıktır.")


def test_SORGU_DISINDA_HICBIR_FIIL_YENI_SORGU_ACMIYOR():
    """⚠ Paralelleştirme yalnız `SORGU` için; ötekiler **koşmuş satırlar** üstünde
    çalışır. Bir dönüşüm fiili yeni sorgu açarsa hem bütçe hem yetki varsayımı bozulur.

    Yüklem yapısal: `sorgu_kos` yalnız `SORGU` dalında çağrılmalı.
    """
    kaynak = _KOSUCU.read_text(encoding="utf-8")
    # `sorgu_kos(` çağrılarının tamamı `SORGU` dalının içinde mi — SAYARAK ölç
    # (bu oturumun ⑲ numaralı dersi: «tek X var» iddiası sayılarak doğrulanır).
    cagrilar = [i for i in range(len(kaynak)) if kaynak.startswith("sorgu_kos(", i)]
    assert cagrilar, "⊘ ölçüm tabanı çöktü: `sorgu_kos(` çağrısı yok"
    sorgu_dali = kaynak.index('if fiil == "SORGU"')
    bagla_dali = kaynak.index('if fiil == "BAGLA"')
    disarida = [c for c in cagrilar if not (sorgu_dali < c < bagla_dali)]
    assert not disarida, (
        f"🔴 `sorgu_kos` `SORGU` dalının DIŞINDA çağrılıyor ({len(disarida)} yer) — "
        "bir dönüşüm fiili yeni sorgu açıyor demektir; bütçe ve yetki varsayımı bozulur.")
