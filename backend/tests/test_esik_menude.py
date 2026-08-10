"""🔴🔴 `§EŞ` — **YETENEK VARDI, GARSONUN MENÜSÜNDE YOKTU.**

## Ölçülen kusur (curl turu, 2026-08-10)

    «bu yıl fire oranı %20 üstü olan hatlar»
      → 8 hattın HEPSİ döndü (eşik uygulanmadı)
      → note: «⚠ bir eşik verdin ama filtreye çeviremedim»

Beyan **doğruydu** — ama kullanıcının kuralı gereği *dürüst bir red bir başarı değil,
çözülecek bir borçtur*.

🔴 Ve yetenek **zaten vardı**: `cube_router` `measure_having` üretiyor,
`wren_service.cube_sql` onu HAVING'e çeviriyor, `niyet_tasima` takipte taşıyor. Yani
**route yapabiliyordu, garson bilmiyordu**.

⚠ Alan **beyan edilmişti** ama **yanlış kanalda**: `plan_semasi` şemasında var ve o şema
`llm_sema_kisitli` bayrağına bağlı — o bayrak da aktif sağlayıcıda **NO-OP** (`D7`).
Yani yetenek, garsona **hiç ulaşmayan** bir kanaldan duyuruluyordu.

*Bir menüde olmayan yemek, mutfakta pişebiliyor olsa da sipariş edilemez.*
"""

from app.llm import _cube_select_system

_ISTEM = _cube_select_system("KATALOG")


def test_ESIK_ALANI_SERBEST_JSON_ISTEMINDE():
    """🔴 **Kapının kalbi.** Alan, garsonun **gerçekten okuduğu** kanalda olmalı —
    şemada olması yetmiyor, çünkü o şema bu sağlayıcıda hiç gönderilmiyor."""
    assert "measure_having" in _ISTEM


def test_BICIM_SABLONUNDA_DA_VAR():
    """⚠ Bugün ölçüldü (`C1`/`C3`): model düzyazı talimattan **şablonu** izliyor —
    `eslesen_terim` yalnız düzyazıdaydı ve **hiç** yazılmadı. Alan şablonda da olmalı."""
    i = _ISTEM.find("Biçim:")
    j = _ISTEM.find("\n", i)
    assert "measure_having" in _ISTEM[i:j], "şablon satırında yok — model onu izlemez"


def test_OPERATORLER_KAPALI_KUME():
    """Eşik operatörleri **kapalı**: dört karşılaştırma. Açık bırakmak modelin
    uyduracağı bir operatör demektir ve `cube_sql` onu reddeder."""
    i = _ISTEM.find("EŞİK")
    blok = _ISTEM[i:i + 400]
    for op in ('">"', '">="', '"<"', '"<="'):
        assert op in blok, op


def test_SATIR_SUZGECINDEN_AYRILDIGI_SOYLENIR():
    """🔴 En kritik ayrım: `measure_having` bir **HAVING**'dir, `filters` bir WHERE.
    Karıştırılırsa *«fire oranı %20 üstü»* satır bazında filtrelenir ve **yanlış** sayı
    çıkar. İstem bunu **açıkça** söylemeli."""
    i = _ISTEM.find("EŞİK")
    blok = _ISTEM[i:i + 400]
    assert "SATIR süzgeci değil" in blok and "HAVING" in blok


def test_ESIK_YOKSA_ALAN_YAZILMAZ():
    """⚠ `§V5`'in aynı disiplini: kullanıcı eşik vermediyse alan **hiç** yazılmamalı —
    yoksa her sorguya uydurma bir eşik girer."""
    i = _ISTEM.find("EŞİK")
    assert "eşik vermediyse alanı hiç yazma" in _ISTEM[i:i + 400]
