r"""🔴🔴 `§T6` — **KISITLAMA UYGULANDI, «UYGULAYAMADIM» DENDİ: YANLIŞ UYARI.**

## Canlıda ölçülen (curl, 2026-08-12) — ve kusur sandığımın TERSİ çıktı

```
çapa                : filters=[{tarih, gte, 2026-01-01}]
«sadece son 3 ayı»  → filters=[{tarih, gte, 2026-05-12}]      ← DARALDI, doğru
note                : «kısıtlama taşıyamadım — sayı TÜM kayıtları kapsıyor»   ← YALAN
```

Teşhisim *«dönem daraltması çalışmıyor»*du. **Ölçüm çürüttü:**
`cube_router.deterministic_refine` işini **doğru yapıyor** — `sadece son 3 ayi` ·
`son 3 ay` · `sadece son 3 ayini goster`, üçü de `tarih gte 2026-05-12` üretiyor.

🔴 Kusur **beyanda**: `uyum.denetle`'nin `sadece` yüklemi tarih boyutunu ve `gte`/`lte`
operatörünü **kasten saymıyordu**. O dışlama, **miras** bir tarih süzgecinin *«kısıtlama
uygulandı»* sanılmasını önlemek içindi — ama kullanıcının **bu turda** çözdürdüğü bir
dönemi de eliyordu.

## Neden bu, eksik bir özellikten DAHA KÖTÜ

Cümle yalnız yanıltmıyor, **veri hakkında yanlış bir şey** söylüyor: *«sayı **tüm**
kayıtları kapsıyor»* — oysa sayı son üç ayı kapsıyor. Kullanıcı doğru bir sayıyı
**yanlış** sanıp atar.

> ㉜ *Yanlış bir uyarı, uyarısızlıktan pahalıdır.*

## Ayrım nereden geliyor — ikinci çözücü YOK

`niyet.donemler` **bu ifadeden** çözülen aralıkları taşır (`sadece son 3 ayi` →
**1**). Doluysa ve sorgu bir tarih kısıtı taşıyorsa kısıtlama **uygulanmıştır**.
İkinci bir dönem çözücü yazılmadı (`KAT-1`).
"""

from __future__ import annotations

_ANCAK_TARIH = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"],
                "filters": [{"dimension": "tarih", "operator": "gte",
                             "value": "2026-05-12"}]}
_FILTRESIZ = {"cube": "oee", "measures": ["ort_oee"], "dimensions": ["makine"]}


def _isaretler(q, cq, schema):
    from app import uyum
    return {i.isaret for i in uyum.denetle(q, cq, None, schema)}


def test_OLCUM_TABANI_DONEM_COZULUYOR(schema):
    """⊘ **Boş yeşil avı.** *«sadece son 3 ayı»* dönemi çözülmüyorsa aşağıdaki yüklem
    bir şey ölçmez — düzeltmenin dayanağı **tam olarak** bu çözümdür."""
    from app.niyet import coz

    n = coz("sadece son 3 ayi", schema)
    assert n.donemler, (
        f"⊘ ölçüm tabanı: dönem çözülemedi (sayı={n.donem_sayisi}) — bu vaka artık "
        "`§T8`'in konusudur, `§T6`'nın değil.")


def test_KISITLAMA_UYGULANDIYSA_YANLIS_UYARI_BASILMIYOR(schema):
    """🔴🔴 **ASIL KAPI.** Dönem çözüldü **ve** sorguya girdi → *«taşıyamadım»* demek
    bir **yanlış uyarıdır**, üstelik veri hakkında yanlış bir cümledir."""
    assert "kisitlama" not in _isaretler("sadece son 3 ayi", _ANCAK_TARIH, schema), (
        "🔴 YANLIŞ UYARI: sorgu `tarih gte 2026-05-12` taşıyor ve dönem bu ifadeden "
        "çözüldü, buna rağmen «kısıtlama taşıyamadım — sayı TÜM kayıtları kapsıyor» "
        "deniyor. Doğru bir sayı, yanlış bir cümlede hâlâ yanlıştır 🅫.")


def test_KISITLAMA_GERCEKTEN_TASINAMADIYSA_HALA_SOYLENIYOR(schema):
    """⚠ **Ters yön — kapı dişsizleşmesin** 🆊. Uygulanamayan bir kısıtlama hâlâ
    **söylenmeli**; düzeltme yalnız *«uygulandığı hâlde söylenen»* vakayı susturur."""
    isaret = _isaretler("sadece Siyah renk", _FILTRESIZ, schema)
    assert "kisitlama" in isaret, (
        f"🔴 KAPI DİŞSİZLEŞTİ: hiçbir kısıtlama taşınmadığı hâlde susuyor — {isaret}")


def test_DONEM_COZULMEDIYSE_TARIH_FILTRESI_TEK_BASINA_YETMEZ(schema):
    """⚠ **Miras süzgeç tuzağı** — orijinal dışlamanın var oluş sebebi. Çapadan gelen
    bir tarih süzgeci, kullanıcının *«sadece …»* isteğini karşılamış **saymaz**;
    dönem **bu ifadeden** çözülmüş olmalı."""
    assert "kisitlama" in _isaretler("sadece kirmizi olanlar", _ANCAK_TARIH, schema), (
        "🔴 MİRAS SÜZGEÇ KISITLAMA SAYILDI: soru bir dönem adlamıyor, sorgudaki tarih "
        "çapadan geliyor — yine de «kısıtlama uygulandı» sanılıyor.")
