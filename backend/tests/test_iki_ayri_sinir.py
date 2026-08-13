"""🔴 `§70` — **İKİ AYRI SINIR VAR** ve biri ötekinin yerine geçmez.

## Ölçüm (`§68`'de bulundu, `§70`'te karara bağlandı)

| sabit | değer | ne demek |
|---|---|---|
| `plan_semasi.AZAMI_ADIM` | **12** | şemanın izin verdiği **uzunluk** |
| `plan_kosucu.AZAMI_SORGU` | **8** | koşumun ödeyebileceği **iş** |

Bir plan **tavanın altında olup bütçeyi aşabilir** (9–12 adımı `SORGU` olan plan).
Eski şerh *«aynı sayı olması tesadüf değil»* diyordu — **bayat bir iddiaydı** ⑳.

## 🔴 Kullanıcı kararı (2026-08-13): *«sayılar kalsın, yalnız beyan düzelsin»*

Kör hizalama **yapılmadı** ㊸ — hangisinin doğru olduğu bir **ürün kararıdır** ve
kullanıcı *«dokunma, açıkla»* dedi. Bu kapı o kararı **kilitler**: sayılar değişirse
kırmızı verir ve değiştiren kişi kararı yeniden almak zorunda kalır ㉕.

## Bu kapının beş yüklemi

| # | savunulan |
|---|---|
| 1 | sayılar **kararlaştırıldığı gibi** (12 · 8) |
| 2 | bütçeyi aşan plan **koşmaz** ve redde **iki sınır ayrı ayrı** yazılır |
| 3 | red **koşumdan önce** gelir (model çağrıldıktan sonra sessiz düşüş değil) |
| 4 | 🆃 geçerli planın satırı **kısa kalır** — açıklama yalnız karışıklığın doğduğu yerde |
| 5 | ⊘ geçerli bir notta *«sorgu > bütçe»* **görünemez** (kendini yalanlayan cümle yok) |
"""

from __future__ import annotations

import pytest

from app import plan_kosucu, plan_tuketici as pt
from app.plan_semasi import AZAMI_ADIM

_CQ = {"cube": "oee", "measures": ["ort_oee"]}


def _plan(n: int) -> dict:
    return {"adimlar": [{"fiil": "SORGU", "cube_query": _CQ} for _ in range(n)]}


def test_SAYILAR_KARARLASTIRILDIGI_GIBI():
    """🔴 ㉕ — kullanıcı *«kalsın»* dedi; değişirse karar **yeniden** alınmalı."""
    assert AZAMI_ADIM == 12, (
        f"🔴 adım tavanı {AZAMI_ADIM} — 2026-08-13 kararı **12**'ydi. Değiştiriyorsan "
        "`ONGORU-DURUM.md §70`'i güncelle ve kullanıcıya sor: bu bir ürün kararı.")
    assert plan_kosucu.AZAMI_SORGU == 8, (
        f"🔴 sorgu bütçesi {plan_kosucu.AZAMI_SORGU} — 2026-08-13 kararı **8**'di.")


def test_BUTCEYI_ASAN_PLAN_REDDINDE_IKI_SINIR_AYRI():
    """Kullanıcı hangi sınıra çarptığını **ve** ötekinin ne olduğunu görmeli."""
    with pytest.raises(plan_kosucu.PlanHatasi) as e:
        plan_kosucu.dogrula(_plan(9))
    metin = pt.onizleme_notu(_plan(9), e.value)
    assert "koşulamaz" in metin, f"🔴 red açıkça söylenmiyor: {metin!r}"
    assert "bütçe" in metin and "tavan" in metin, f"🔴 iki sınır ayrı yazılmamış: {metin!r}"
    assert "İki ayrı sınır" in metin, (
        "🔴 sınırların **ayrı** olduğu söylenmiyor — kullanıcı onları tek bütçe sanar")


def test_RED_KOSUMDAN_ONCE():
    """㊴ Bütçe kapısı `dogrula`'da, yani **koşumdan önce**: 9. sorguda çökmek yerine
    hiç başlamamak."""
    with pytest.raises(plan_kosucu.PlanHatasi, match="bütçe"):
        plan_kosucu.dogrula(_plan(12))


def test_ZIT_OLCUT_GECERLI_PLANIN_SATIRI_KISA():
    """🆃 Kapının kurbanı: açıklamayı **her** nota koymak da yeşil bırakırdı — ve her
    önizlemeyi bir ders kitabına çevirirdi."""
    normal = pt.onizleme_notu(_plan(3))
    assert "İki ayrı sınır" not in normal, f"🔴 geçerli plan da uzun ders alıyor: {normal!r}"
    assert normal.endswith("koşmadan önce gözden geçir."), f"🔴 satır bozuldu: {normal!r}"


def test_KENDINI_YALANLAYAN_CUMLE_URETILEMEZ():
    """⊘ Geçerli bir planda `sorgu ≤ bütçe`'dir; yani *«12 sorgu (bütçe 8)»* satırı
    **geçerli** bir önizlemede asla görünemez.

    ⚠ Yüklem yapıya bağlandı ⑭: metni değil, **doğrulayıcıyı** sorar.
    """
    for n in range(1, AZAMI_ADIM + 1):
        p = _plan(n)
        try:
            plan_kosucu.dogrula(p)
        except plan_kosucu.PlanHatasi:
            continue                      # geçersiz → notu zaten red metnidir
        assert plan_kosucu.sorgu_sayisi(p) <= plan_kosucu.AZAMI_SORGU, (
            f"🔴 {n} adımlık plan geçerli sayıldı ama bütçeyi aşıyor — önizleme kendini "
            "yalanlayan bir satır basardı")
