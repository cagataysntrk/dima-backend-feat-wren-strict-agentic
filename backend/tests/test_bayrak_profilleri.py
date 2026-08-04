"""FAZ 0.20 — **BAYRAK PROFİLLERİ.** Kombinasyonlar da test edilir.

## Ölçülen boşluk

EK E'de **~70 bayrak**; §C/10'un hedefi *"ölü bayrak **0**"*. Her maddenin `GERİ AL`'ı
**tek tek** test ediliyor (*"bayrak `off` iken davranış birebir bugünkü"*) — ama
**kombinasyonlar hiç test edilmiyor**. İki bayrağın birlikte açık olması, ikisinin ayrı
ayrı doğru olmasından **bağımsız** bir davranıştır.

## 🔴 Yaşam döngüsü bu maddenin ASIL işi

`v1-varsayilan`'da **iki sürüm** açık kalan bayrak **SİLİNİR** (kod kalıcılaşır, bayrak
gider). Yoksa *"ölü bayrak 0"* hedefi, sayı büyüdükçe **matematiksel olarak**
tutturulamaz: her yeni özellik bir bayrak ekler, hiçbiri kaldırılmaz.

**Bir bayrak bir KARAR ANIDIR, bir mülk değil.**
"""

from __future__ import annotations

import pytest

from app import bayrak_profilleri as bp


def test_UC_PROFIL_de_KURULABILIYOR():
    for ad in (bp.TABAN, bp.V1_VARSAYILAN, bp.V1_TAM):
        p = bp.profil(ad)
        assert isinstance(p, dict), f"{ad} profili sözlük değil"


def test_TABAN_PROFILI_HEPSI_KAPALI():
    """🔴 `KURAL A`'nın **kod karşılığı**. Bir gerilemenin bayraktan mı yoksa koddan mı
    geldiğini ayıran **tek** ölçüm noktası budur; boş harita = *"hepsi kapalı"*
    (`resolve_for` bir bayrağı ancak sözlükte varsa açık sayar)."""
    assert bp.profil(bp.TABAN) == {}, "taban profili boş DEĞİL — dondurulmuş taban yok"


def test_V1_VARSAYILAN_GERCEK_YAPILANDIRMA():
    """Kapı buna karşı koşmazsa, ölçülen şey **kimsenin kullanmadığı** bir
    yapılandırmadır. Profil `features.yml`'den okunur — ikinci bir varsayılan listesi
    yazmak, iki farklı *"varsayılan"* demekti."""
    p = bp.profil(bp.V1_VARSAYILAN)
    assert p, "v1-varsayilan boş — gerçek yapılandırma okunmuyor"
    acik = [k for k, v in p.items() if v != "off"]
    assert acik, "hiçbir bayrak açık değil — YAML okunamamış olabilir"


def test_V1_TAM_HEDEF_DURUMU_temsil_ediyor():
    """*"Hedef durum bugün çöküyor mu?"* — bir bayrağı açmadan **önce** sorulması
    gereken soru. `prod` olanlar `prod` kalır: onlar zaten **kalıcılaşmış kararlardır**,
    geri çevirmek profili yanıltıcı yapardı."""
    from app.features import FLAG_REGISTRY

    p = bp.profil(bp.V1_TAM)
    assert set(p) == set(FLAG_REGISTRY), "v1-tam kayıttaki her bayrağı kapsamıyor"
    assert all(v != "off" for v in p.values()), "v1-tam'da kapalı bayrak var"


def test_BILINMEYEN_PROFIL_SESSIZCE_BOS_DONMEZ():
    """Bilinmeyen bir profil adı **hata verir**. Sessizce boş sözlük dönmek, kapıyı
    *"taban"* profilinde koşturup **yeşil** raporlardı — sahte güvenin ta kendisi."""
    with pytest.raises(ValueError, match="bilinmeyen profil"):
        bp.profil("olmayan-profil")


def test_OLU_BAYRAK_ENVANTERI_GEREKCELI():
    """§C/10 — *"ölü bayrak 0"*. Bugün **iki** tane var ve ikisi de **kayıtta var,
    YAML'de yok** sınıfından: tanımlı ama hiçbir ortamda çözülmüyor."""
    olu = bp.olu_bayraklar()
    for ad, gerekce in olu.items():
        assert gerekce.strip(), f"`{ad}` gerekçesiz raporlanmış"
        assert "yok" in gerekce, f"`{ad}` gerekçesi SINIFI söylemiyor: {gerekce}"


def test_YASAM_DONGUSU_OLCULMEMIS_BORC_BORC_DEGILDIR():
    """🔴 `⊘` disiplini: *"sürüm"* bu depoda bir **karardır**, otomatik türetilebilir
    bir sayı değil. Uydurmak, **ölçüm gibi görünen bir tahmin** üretirdi."""
    assert bp.yasam_dongusu_borclari() == {}, "ölçülmemiş geçmişten borç UYDURULDU"
    assert bp.yasam_dongusu_borclari({"olmayan_bayrak": 5}) == {}, \
        "YAML'de olmayan/kapalı bir bayrak borç sayıldı"


def test_YASAM_DONGUSU_IKI_SURUM_ACIK_KALANI_YAKALAR():
    """*"Bir bayrak bir KARAR ANIDIR, bir mülk değil."* İki sürüm açık kalan bayrak
    silinmeli — yoksa *"ölü bayrak 0"* hedefi matematiksel olarak tutturulamaz."""
    acik = [k for k, v in bp._yaml_bayraklari().items() if v != "off"]
    assert acik, "açık bayrak yok — test çapası kaymış"
    borc = bp.yasam_dongusu_borclari({acik[0]: 2})
    assert acik[0] in borc, "iki sürümdür açık olan bayrak borç sayılmadı"
    assert bp.yasam_dongusu_borclari({acik[0]: 1}) == {}, \
        "tek sürümlük bayrak borç sayıldı — eşik yanlış"


def test_PROFIL_OZETI_UCUNU_de_RAPORLUYOR():
    o = bp.profil_ozeti()
    assert set(o) == {bp.TABAN, bp.V1_VARSAYILAN, bp.V1_TAM}
    assert o[bp.TABAN]["acik"] == 0
    assert o[bp.V1_TAM]["acik"] >= o[bp.V1_VARSAYILAN]["acik"], \
        "v1-tam, varsayılandan DAHA AZ bayrak açıyor — profil tanımı bozuk"
