r"""🔴 `FAZ 5` — **ÖNERİ MOTORU KAPISI** (`app/oneri.py`).

Planın kapı listesi (`§42 · FAZ 5`) beş madde ister. Bu dosya `①`, `③` ve `⑤`'i
kilitler; `②` (`p95 < 300 ms`) ve `④` (bayat indeks beyanı) **indeks üreteciyle**
(`5.7`) birlikte gelir — o gelmeden ölçülecek bir indeks yoktur 🅗.

🔴 **`①` bu fazın tek güvenlik kalemidir** ve buradaki en ağır yüklemdir: bir öneri
listesi **envanterdir**; yetkisiz bir ölçünün **adı** bile sızmamalıdır.
"""

from __future__ import annotations

from app.oneri import ara, terimler

# ── Fikstür: iki küp, ikisi ayrı MDL modeline dayanıyor 🅬 ───────────────────
_SEMA = {
    "cubes": [
        {"name": "parti", "base_object": "partiler",
         "measure_synonyms_display": {"toplam_ciro": "ciro",
                                      "fire_orani_yuzde": "fire oranı",
                                      "toplam_fire_kg": "fire"}},
        {"name": "maas", "base_object": "bordro",
         "measure_synonyms_display": {"toplam_brut_maas": "brüt maaş",
                                      "ort_brut_maas": "ortalama brüt maaş"}},
    ]
}


# ── ① 🔴🔴 YETKİ SÜZMESİ SIRALAMADAN ÖNCE (envanter sızıntısı) ──────────────

def test_YETKISIZ_KUPUN_ADI_BILE_SIZMAZ():
    """🔴🔴 **Fazın tek güvenlik kalemi.** Dar yetkili principal `bordro`'yu
    görmüyorsa, *«maaş»* yazınca **hiçbir** maaş terimi dönmemeli.

    Yanlış tasarım şöyle olurdu: önce sırala, sonra süz — o zaman sıralama yetkisiz
    terimleri **görür** ve kesme (`limit`) yüzünden yetkili terimler **dışarıda kalır**.
    Yani süzmenin **yeri** güvenliğin kendisidir ㊴.

    🅑 Mutasyon: `terimler()`'deki `continue` kaldırılırsa bu yüklem kırılır.
    """
    izinli = {"partiler"}  # `bordro` YOK
    hepsi = terimler(_SEMA, izinli)
    assert hepsi and all(a.cube == "parti" for a in hepsi), (
        f"🔴 ENVANTER SIZINTISI: yetkisiz küpün terimleri listede — {[a.kimlik for a in hepsi]}")
    assert not ara("maaş", _SEMA, izinliler=izinli), (
        "🔴 yetkisiz ölçü öneri olarak sunuldu — koşturulamasa bile **adı** sızdı.")


def test_YAPILANDIRILMAMIS_ile_BOS_ALLOWLIST_ayni_degil():
    """🆋 `katman_b`'nin ayrımı **çağrılarak** korunuyor, kopyalanarak değil (`KAT-1`).

    `None` → Katman B kurulmamış → hepsi görünür. Boş küme → allowlist **aktif ve
    boş** → hiçbiri görünmez. İkisini aynı saymak, yapılandırılmamış bir tenant'ta
    öneriyi **tamamen** kapatırdı (ya da tersi: sızdırırdı).
    """
    assert len(terimler(_SEMA, None)) == 5
    assert terimler(_SEMA, set()) == []


# ── ③ GÖMÜCÜ SOĞUKKEN LEKSİK — ÇÖKME YOK ────────────────────────────────────

def test_gomucu_SOGUKKEN_leksik_calisir_cokme_yok():
    """`5.8` — `DIMA_VQR_EMBEDDER=off` altında (testlerin varsayılanı) `_embedder()`
    `None` döner. Motor **çökmemeli**, leksik ayakla cevap vermeli ve `kip` bunu
    **beyan etmeli** 🅖.
    """
    out = ara("fire", _SEMA, izinliler=None)
    assert out, "🔴 gömücü yokken hiçbir öneri dönmedi — leksik ayak düşmüş."
    assert all(a.kip == "leksik" for a in out), (
        f"🔴 kip yanlış beyan ediliyor: {[a.kip for a in out]}")
    assert out[0].etiket == "fire", (
        f"🔴 birebir önek eşleşmesi başa gelmedi: {[a.etiket for a in out]}")


def test_onek_esitlikte_KISA_ETIKET_once():
    """*«fire»* yazan kullanıcı önce `fire`'ı, sonra `fire oranı`'nı görmeli —
    ikisi de önek eşleşmesidir, ayıran şey **uzunluk**tur (daha az varsayım)."""
    out = [a.etiket for a in ara("fire", _SEMA, izinliler=None)]
    assert out[:2] == ["fire", "fire oranı"], f"🔴 sıra: {out}"


# ── ⑤ HER ADAY TEMSİL EDİLEBİLİR ────────────────────────────────────────────

def test_her_aday_KUP_ve_KIMLIK_tasir():
    """`⑤`'in bu fazdaki karşılığı: bir öneri, tıklanınca **hangi küpün hangi ölçüsü**
    olduğunu söyleyebilmeli. Taşımıyorsa süs olur 🆈 — `FAZ 6` onu sorguya çeviremez.

    ⚠ JOIN gerektiren adayların elenmesi `FAZ 6`'nın işidir (sorgu orada kurulur);
    burada **temsil edilebilirliğin ön koşulu** kilitlenir 🅗.
    """
    for a in ara("ciro", _SEMA, izinliler=None):
        assert a.cube and "." in a.kimlik and a.kimlik.startswith(a.cube + ".")


def test_bos_ve_ANLAMSIZ_girdi_PATLAMIYOR():
    """🅡 Naif girdi — typeahead her tuşta çağrılır; boş dize en sık gelen girdidir."""
    assert ara("", _SEMA, izinliler=None) == []
    assert ara("   ", _SEMA, izinliler=None) == []
    assert ara("zzzzqqq", _SEMA, izinliler=None) == []
    assert ara("fire", {"cubes": []}, izinliler=None) == []


def test_limit_TAVANI_asilmaz():
    """`FAZ 6.4`: **≤7** öneri. Kaydırma yok — görünmeyen bir öneri, olmayan bir
    öneridir (`FAZ 4`'te ölçüldü)."""
    from app.oneri import VARSAYILAN_LIMIT

    assert VARSAYILAN_LIMIT == 7
    assert len(ara("a", _SEMA, izinliler=None, limit=2)) <= 2


# ── ⚠ MUTLAK EŞİK YASAĞI — `FAZ 0`'ın bulgusu koda bağlanıyor ───────────────

def test_MUTLAK_KOSINUS_ESIGI_YOK():
    """🔴 `FAZ 0`: gürültü *«vardya»* kosinüs **0,851** aldı — *«skor > X ⇒ iyi aday»*
    **çalışmaz**. Vektör ayağı yalnız **sıra** üretmeli.

    🅑 Mutasyon: `_vektor_sira`'ya bir `skor > 0.8` süzgeci eklenirse bu yüklem kırılır.
    """
    import inspect

    from app import oneri

    kaynak = inspect.getsource(oneri._vektor_sira)
    assert "argsort" in kaynak, "🔴 vektör ayağı artık sıra üretmiyor olabilir."
    for kotu in (">= 0.", "> 0.", "ESIK", "esik"):
        assert kotu not in kaynak, (
            f"🔴 vektör ayağında mutlak eşik izi ({kotu!r}) — `FAZ 0` bunu ölçtü ve "
            "reddetti (gürültü 0,851).")


# ── `5.7` İNDEKS — bayatlık BEYAN edilmez, İMKÂNSIZ kılınır 🅐 ───────────────

def test_indeks_gomucu_kapaliyken_KAPALI_der():
    """`④`'ün ilk hâli: gömücü yoksa vektör ayağı hiç çalışmaz ve bu **söylenir**.

    Sessizce leksik'e düşen bir liste, düşmediğini sandıran bir listedir 🅖.
    """
    from app.oneri import indeks_durumu

    d = indeks_durumu({"version": "v1"})
    assert d == {"durum": "kapali", "surum": "v1"}


class _SahteGomucu:
    """Sayan bir gömücü. **Yük taşıyan yol budur** — `DIMA_VQR_EMBEDDER=off` altında
    gerçek gömücü `None` döner ve vektör ayağı **hiç koşmaz**; o hâlde önbelleği
    ölçmek isteyen bir yüklem, ölçtüğünü sandığı şeye **hiç dokunmaz** 🆎."""

    def __init__(self) -> None:
        self.cagri = 0

    def embed(self, metinler):
        ms = list(metinler)
        self.cagri += len(ms)
        # Deterministik, birbirinden ayrı vektörler (uzunluk + ilk harf kodu).
        return [[float(len(m)), float(ord(m[-1]) if m else 0), 1.0] for m in ms]


def test_indeks_SURUM_ANAHTARLI_bayat_hal_YOK(monkeypatch):
    """🔴🔴 **`5.7`'nin özü** — ve kapının **ısırdığı** hâli.

    Plan bir *«tazelik damgası»* istiyordu; damga bayatlığı **beyan eder**. Burada
    anahtar **şema sürümünün kendisi**dir: sürüm değişince eski girdi **okunamaz**,
    yani *bayat* diye bir hâl **doğmaz** 🅐.

    ⚠ 🅑 **İlk yazılışım ısırmıyordu:** `_INDEKS`'e elle bir girdi koyup yalnız
    `indeks_durumu`'nu okuyordu — gömücü kapalı olduğu için `_vektor_sira` **hiç
    koşmuyordu** ve iki mutasyon da **hayatta kaldı**. Yüklem, yükü taşıyan yolu
    koşturacak şekilde yeniden yazıldı.

    🅑 Mutasyonlar: ⓐ anahtardan sürümü düşür → sürüm değişince **yeniden gömmez**
    ⓑ kimlik hizası kontrolünü düşür → farklı aday kümesi **eski matrisi** kullanır.
    """
    from app import oneri, vqr

    sahte = _SahteGomucu()
    monkeypatch.setattr(vqr, "_embedder", lambda: sahte)
    oneri._INDEKS.clear()

    s1 = {**_SEMA, "version": "v1"}
    oneri.ara("fire", s1, izinliler=None)
    ilk = sahte.cagri
    assert ilk >= 5, "🔴 aday gömmeleri hiç yapılmadı — vektör ayağı koşmamış."
    assert oneri.indeks_durumu(s1)["durum"] == "taze"

    # ① Aynı sürüm, aynı havuz → **yeniden gömme YOK** (yalnız sorgunun kendisi).
    oneri.ara("ciro", s1, izinliler=None)
    assert sahte.cagri - ilk == 1, (
        f"🔴 önbellek ıskalandı: {sahte.cagri - ilk} ek gömme (yalnız 1 sorgu bekleniyordu)")

    # ② 🔴 Şema sürümü değişti → **yeniden gömülmeli** (eski matris okunamaz).
    onceki = sahte.cagri
    oneri.ara("fire", {**_SEMA, "version": "v2"}, izinliler=None)
    assert sahte.cagri - onceki >= 6, (
        "🔴 sürüm değişti ama YENİDEN GÖMÜLMEDİ — anahtar sürümü taşımıyor, "
        "yani bayat bir matris kullanılıyor.")

    # ③ 🔴🔴 **AYNI SAYIDA ama FARKLI KİMLİKLİ** havuz — anahtarın tek başına
    # yetmediği hâl. ⚠ İlk denemem bunu **yalıtamamıştı**: allowlist daralınca aday
    # SAYISI da değişiyordu, yani anahtar zaten ıskalıyordu ve mutasyon **hayatta
    # kaldı** ㉘. Ayırt edici vaka, iki küpün **eşit sayıda** ölçü taşımasıdır.
    esit = {"cubes": [
        {"name": "a", "base_object": "ma",
         "measure_synonyms_display": {"m1": "fire", "m2": "fire oranı"}},
        {"name": "b", "base_object": "mb",
         "measure_synonyms_display": {"m3": "fire kg", "m4": "fire yüzdesi"}},
    ], "version": "vX"}
    oneri._INDEKS.clear()
    oneri.ara("fire", esit, izinliler={"ma"})       # havuz: a'nın 2 terimi
    onceki = sahte.cagri
    ikinci = oneri.ara("fire", esit, izinliler={"mb"})  # havuz: b'nin 2 terimi — AYNI SAYI
    assert sahte.cagri - onceki >= 3, (
        "🔴 aday kümesi DEĞİŞTİ (aynı sayı, farklı kimlikler) ama eski matris "
        "kullanıldı — skorlar YANLIŞ ADAYA atanır (sessiz hizasızlık).")
    assert all(a.cube == "b" for a in ikinci), (
        f"🔴 yetkisiz küpün adayı döndü: {[a.kimlik for a in ikinci]}")
    oneri._INDEKS.clear()


def test_indeks_DISKTE_ARTEFAKT_URETMIYOR():
    """⑪ Bu depo bir kez *«gitignore'lu bir derleme artefaktından okuyan ölçüm»*
    yüzünden aynı kaynakta **farklı sayı** gördü. Öneri indeksi o sınıfa girmez:
    bellekte yaşar, süreçle ölür — okunacak bayat bir dosya **yoktur**.
    """
    import inspect

    from app import oneri

    kaynak = inspect.getsource(oneri)
    for yasak in ("open(", "Path(", "np.save", "np.load", "json.dump"):
        assert yasak not in kaynak, (
            f"🔴 `oneri.py` diske dokunuyor ({yasak!r}) — indeks bir **artefakt**a "
            "dönüşürse bayatlık sınıfı geri gelir ⑪.")
