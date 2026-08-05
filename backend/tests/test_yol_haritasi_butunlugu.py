"""FAZ 0.14 / **D5 — BELGE KAPISI**: kod kapılarıyla aynı disiplinin öteki yüzü.

## Neden

`0.14`'ün `KAPI`'sı: *"kod kapıları ile belge kapısı **aynı disiplinin iki yüzü**."*
Bu operasyonda belgenin kendisi **on beş kusur** taşıdı ve bunların hiçbirini bir test
yakalamadı — çünkü belgeyi ölçen bir kapı yoktu. Sonuçlar ölçüldü:

* *"0.1 İNDİ @`0619bfd`"* — o commit'te araç **yoktu** (`git ls-tree` ile ölçüldü)
* `A6` maddesinin kanıt komutu (*"`grep` boş döner"*) **hiç koşulmamıştı**
* `−1.1` başlığı *"altı satır"* diyordu, tablo **13** satırdı
* Bölüm II'nin **17/18** maddesinde `GERİ AL` bloğu yoktu

## ⚠ Kapının bilinen sınırı — ve neden kabul ediliyor

Yol haritası **git altında değil** (`~/.claude/plans/`). Yani bu kapı **yalnız yerelde**
koşar; temiz bir checkout'ta `skip` eder. Bu bir zayıflık ama **gizlenmiyor**: alternatif
(belgeyi repoya kopyalamak) `feedback_tek_dosya_calisma`'nın açıkça yasakladığı şey —
ikinci bir kopya, ikinci bir doğruluk kaynağıdır.
"""

from __future__ import annotations

import pathlib
import re

import pytest

YOL = pathlib.Path.home() / ".claude" / "plans" / "DIMA-V1-YOL-HARITASI.md"


def _belge() -> str:
    if not YOL.exists():
        pytest.skip(f"yol haritası bulunamadı ({YOL}) — kapı YALNIZ yerelde koşar")
    return YOL.read_text(encoding="utf-8")


def _maddeler(metin: str) -> dict[str, str]:
    """`### <no> · <başlık>` bloklarını no → gövde olarak ayırır."""
    out: dict[str, str] = {}
    parcalar = re.split(r"^### ([0-9]+\.[0-9a-z]*|−?1\.[0-9]+|II-[A-Z]\.[0-9a-z]+) · ",
                        metin, flags=re.M)
    for i in range(1, len(parcalar) - 1, 2):
        out[parcalar[i]] = parcalar[i + 1]
    return out


def test_D5_HER_MADDE_NE_ve_KAPI_tasir():
    """Bir madde `NE` ya da `KAPI` taşımıyorsa o bir **niyet**tir, bir madde değil."""
    maddeler = _maddeler(_belge())
    assert len(maddeler) >= 20, f"madde ayrıştırma bozuk: {len(maddeler)} bulundu"
    eksik = [no for no, govde in maddeler.items()
             if "**NE**" not in govde and "**KAPI**" not in govde]
    assert not eksik, (
        "NE ya da KAPI taşımayan madde(ler): " + ", ".join(sorted(eksik))
        + "\nKapısız inen bir madde 'bitti' sayılmaz — belgenin kendi doktrini.")


@pytest.mark.xfail(strict=True, reason=(
    "🔴 BİLİNEN ve SAHİPLİ BORÇ (açık borç #2): 54 bayraklı maddenin 17'sinde `GERİ AL` "
    "yok — HEPSİ `II-*`, yani **v2/v3** kapsamında ve bu döngünün dışında. Kök neden de "
    "ölçüldü: denetim regex'i `II-X.N` başlıklarını kapsamıyordu, yani kapının KENDİ kör "
    "noktasıydı. `0.14`'ün `GERİ AL` kuralı bu durumu tarif ediyor: *«Kapı testi geri "
    "alınmaz — `xfail` işaretlenir ve gerekçesi yazılır. Bir kapının kırmızısı bir "
    "BİLGİDİR; kaldırıldığında o bilgi de kaybolur.»* `strict=True`: 17'si kapandığı gün "
    "bu test **beklenmedik geçiş** verir ve işaret kaldırılır."))
def test_D5_BAYRAKLI_MADDE_GERI_AL_tasir():
    """`KURAL B`: bayraklı her madde bir **kill-switch** beyan eder. Ölçüldü: Bölüm II'nin
    **17/18** maddesinde `GERİ AL` yoktu ve denetim regex'i `II-X.N` başlıklarını
    kapsamadığı için bunu **göremiyordu** — kapının kendi kör noktası."""
    maddeler = _maddeler(_belge())
    bayrakli = {no: g for no, g in maddeler.items() if "[bayrak:" in g.split("\n")[0]}
    if not bayrakli:
        pytest.skip("bayraklı madde bulunamadı — ayrıştırma çapası değişmiş olabilir")
    eksik = sorted(no for no, g in bayrakli.items() if "**GERİ AL**" not in g)
    assert not eksik, (
        f"BAYRAKLI ama GERİ AL'ı YOK ({len(eksik)}/{len(bayrakli)}): {eksik}\n"
        "Bayrak kapalıyken davranışın birebir aynı olduğu YAZILMALI (KURAL B).")


def test_D5_VAR_DIYE_ANILAN_DOSYA_GERCEKTEN_VAR():
    """🔴 `A6` SINIFI — *"kanıt cümlesi de kanıt ister."*

    ⚠ **Premis düzeltmesi (kapı kurulurken ölçüldü):** ilk sürüm *"anılan HER test dosyası
    var olmalı"* diyordu ve **onlarca** kırmızı verdi. Yanlış premis: yol haritası bir
    **PLANDIR**; gelecekteki fazların üreteceği dosyaları anması **doğrudur**. Ölçüm
    aracının kendisi de bir bağımlılıktır — bu kez teste gömülü **varsayım** kusurluydu.

    Doğru iddia dar ve keskin: belge bir dosyanın **«zaten var» olduğunu söylüyorsa**,
    o dosya **gerçekten var olmalı**. `A6` tam bu yüzden düştü."""
    kok = pathlib.Path(__file__).resolve().parents[1]
    metin = _belge()
    iddia = re.compile(r"`(tests/test_[a-z0-9_]+\.py)`[^\n]{0,80}?"
                       r"(\*\*zaten var\*\*|\(zaten var\)|ZATEN VAR)")
    var_denen = {m.group(1) for m in iddia.finditer(metin)}
    eksik = sorted(y for y in var_denen if not (kok / y).exists())
    assert not eksik, (
        "BELGE «ZATEN VAR» DİYOR ama REPODA YOK:\n  " + "\n  ".join(eksik)
        + "\n\n`A6` bu sınıftan düştü: kanıt cümlesi hiç koşulmamıştı.")


#: Yol haritasının **üreteceği** kapı dosyası sayısı — @`d454cf6` ölçüldü (95 anılan,
#: 22 mevcut, **73 planlanan**). Bu sayı **AZALIR**: her faz indiğinde birkaç dosya
#: gerçeğe döner. **ARTMASI** ise bir uyarıdır — yeni bir kapı vaat edildi demektir ve
#: vaat, plan gözden geçirilmeden büyümemeli.
PLANLANAN_KAPI_TAVANI = 73


def test_D5_PLANLANAN_KAPI_SAYISI_SESSIZCE_ARTMAZ():
    """Yol haritası bir **PLANDIR**: henüz olmayan dosyaları anması doğrudur. Ölçülebilir
    olan şey *"sahiplik"* değil (proza izlenemez — denenip **ölçülerek** bırakıldı),
    **büyüme**dir.

    ⚠ İlk sürüm *"her planlanan dosyanın bir `KAPI` satırı olmalı"* diyordu ve metni
    kovalamaya başladı (73 → 5 yanlış-pozitif, pencere büyüterek). Ölçülemeyen bir
    iddiayı zorlamak, kapıyı **yanlış-kırmızı üretecine** çevirir. İddia daraltıldı."""
    kok = pathlib.Path(__file__).resolve().parents[1]
    anilan = sorted(set(re.findall(r"tests/test_[a-z0-9_]+\.py", _belge())))
    assert anilan, "belge hiç test dosyası anmıyor — çapa kaymış"
    planlanan = [y for y in anilan if not (kok / y).exists()]
    assert len(planlanan) <= PLANLANAN_KAPI_TAVANI, (
        f"PLANLANAN kapı dosyası sayısı ARTTI: {len(planlanan)} > {PLANLANAN_KAPI_TAVANI}.\n"
        + "\n".join(f"  {y}" for y in planlanan[:10])
        + "\n\nYeni bir kapı vaat edildi. Bu bir KARARDIR: tavanı yükseltmek belgeyle "
          "birlikte yapılır, sessizce değil.")


def test_D5_SAYI_BEYANLARI_DAMGALI():
    """`D2`: *"her sayı `<sayı> @<sha> · <komut>` taşır."* En azından **damga** aranır —
    komutun varlığı `A5-KOMUT` kutusunda ayrıca kilitli."""
    metin = _belge()
    assert "A5-KOMUT" in metin, (
        "§C'nin sayılarını üreten komut kutusu (`A5-KOMUT`) YOK — sayılar elle yazılıyor "
        "demektir ve bayatlamaları kaçınılmazdır (D2).")
    assert re.search(r"@`[0-9a-f]{7,40}`", metin), "belgede hiç SHA damgası yok"


# ─────────────────────────────────────────────────────────────────────────────
# FAZ 7.0 — planın **kendi 5 iç boşluğu** kapatılır
#
# 🔴 *Bu, planın kendi boşluklarını kapatan maddenin kendi kapısıdır — kapısız
# bırakılırsa boşluklar **sessizce geri döner**.*
# ─────────────────────────────────────────────────────────────────────────────

def test_7_0_PK_KD_A11Y_atiflari_TANIMLI():
    """🔴 Tanımsız bir atıf, **karşılığı olmayan bir kurala** güven verir.

    *"PK-7'ye uyuyor"* diyen bir madde, `PK-7` hiç tanımlanmamışsa hiçbir şey söylememiş
    olur — ama söylemiş **gibi** okunur.
    """
    import re as _re

    metin = _belge()
    for onek in ("PK", "KD", "A11Y"):
        kullanilan = {int(n) for n in _re.findall(rf"\b{onek}-(\d+)\b", metin)}
        if not kullanilan:
            continue
        aralik = _re.search(rf"{onek}-1\s*[…\-–]+\s*{onek}-(\d+)", metin)
        assert aralik, f"🔴 `{onek}-n` atıfları var ama TANIM ARALIĞI yazılı değil."
        ust = int(aralik.group(1))
        fazla = sorted(n for n in kullanilan if n > ust or n < 1)
        assert not fazla, (
            f"🔴 Tanım dışı `{onek}` atfı: {fazla} (tanımlı: 1…{ust}). Karşılığı olmayan "
            f"bir atıf, olmayan bir kurala güven verir.")


def test_7_0_TASINAN_maddeler_KUTUK_birakmis():
    """*"Kapananlar işaretlenir, silinmez"* — taşınan bir madde yerinde bir iz bırakmalı.

    ⚠ Ölçü **sayı değil varlık**: belge büyüdükçe sayı değişir, ama *hiç iz olmaması*
    taşımaların **sessizce** yapıldığı anlamına gelir.
    """
    import re as _re

    izler = _re.findall(r"kaçmıştı|taşındı|SİLİNMEDİ|geri alındı|DARALDI", _belge())
    assert len(izler) >= 10, (
        f"🔴 Yalnız {len(izler)} taşıma/kapanış izi — maddeler sessizce taşınıyor "
        f"olabilir ve *kapananlar işaretlenir, silinmez* kuralı çürümüş demektir.")


def test_7_0_DOGRULANMADI_damgasi_KULLANILIYOR():
    """🔴 Doğrulanmamış bir iddia **gizlenemez**.

    Bu kapı bir üst sınır koymaz (araştırma sürüyor), **varlığını** ölçer: damga hiç
    yoksa ya her şey doğrulanmıştır (iddialı) ya da **damga kullanılmıyordur** ve
    doğrulanmamışlar doğrulanmış gibi okunur.
    """
    import re as _re

    n = len(_re.findall(r"\[DOĞRULANMADI", _belge()))
    assert n >= 3, f"🔴 Yalnız {n} `[DOĞRULANMADI]` damgası — damga kullanılmıyor olabilir."


def test_7_0_YURURLUKTE_indeksinin_HER_satirinin_TUZAGI_var():
    """⚠ ⟳ satırlarının bir tuzağa bağlanması bir **plan kuralıdır**, yalnız bir test
    detayı değil — ve bu yüzden plan kapısında da ölçülür.

    (Aynı şart `test_beyanlar_curumesin.py`'de kod tarafından da kilitli; iki yerden
    ölçülmesi **çift kayıt değil**, iki farklı sorunun cevabıdır: *"beyan çürüdü mü"* ve
    *"plan kuralı uygulanıyor mu"*.)
    """
    import re as _re
    from pathlib import Path as _P

    kok = _P(__file__).resolve().parents[1]
    mimari = (kok / "MIMARI.md").read_text(encoding="utf-8")
    tuzaklar = (kok / "tests/test_beyanlar_curumesin.py").read_text(encoding="utf-8")
    satirlar = [ln for ln in mimari.splitlines()
                if ln.startswith("| **§") and "⟳ UYGULANMADI" in ln]
    for ln in satirlar:
        bolum = _re.match(r"\|\s*\*\*(§[0-9.]+)\*\*", ln)
        assert bolum, f"⟳ satırı bölüm kimliği taşımıyor: {ln[:60]}"
        assert bolum.group(1) in tuzaklar, (
            f"🔴 `{bolum.group(1)}` ⟳ satırının bir TUZAĞI yok — beyan sessizce çürür.")


def test_7_0_FAZ_SIRASI_bagimliliklari_YAZILI():
    """Bir maddenin ön koşulu varsa **yazılı** olmalı: sırayı bilmeyen bir uygulayıcı
    onu bozar.

    Ölçülen üç bilinen bağımlılık: `4.7←4.8` · `5.6←AJ2` · `6.5/embed←motor-RLS`.
    """
    metin = _belge()
    # ⚠ Belirteç **gerçek metne** göre yazıldı: ilk yazımda
    # `"always_filter tek başına yeterli"` aradım ama belgede araya bir backtick giriyor
    # (`` `always_filter` tek başına yeterli sayılmaz ``). *Bir kapının aradığı dize,
    # aradığı belgeden okunmalıdır — hatırlanandan değil.*
    for ifade in ("ÖN KOŞUL: 4.8", "ÖN KOŞUL: AJ2", "tek başına yeterli sayılmaz"):
        assert ifade in metin, f"🔴 Bağımlılık beyanı kayıp: {ifade!r}"
