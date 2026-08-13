r"""🔴🔴 `§18.7` KAPISI — **GÖMÜLEN ŞEY ALAN ADI DEĞİL, ÇOK GÖRÜNÜMLÜ TEMSİLDİR.**

## Neden bu dosya var — ölçülmüş bir kusur, tahmin değil

Canlı curl turu (2026-08-13) ölçtü:

```
q=fi → fire·oee, fire·parti, fırsat adedi, fire oranı, su·surdurulebilirlik, set·enerji_tesis
                                                        ^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^^
```

Son iki aday **alakasız**. Sebep `§18.6`'nın işaret ettiği boşluk: `toplam_su_lt`'nin
görünen etiketi `"su"`, `set_tep_ton`'unki `"set"` — ve motor o **çıplak** etiketi
gömüyordu. İki karakterlik bir sorgu (`fi`) ile iki karakterlik bir etiket (`su`)
arasındaki kosinüs, alanın **anlamından** değil kelimenin **kısalığından** gelir.

## 🔴 Ve altında daha ağır bir bulgu vardı: **ÖLÇÜM ÜRETİMDE KOŞMUYORDU** 🅕

`FAZ 0` (`lab/oneri_olcum.py::gorunumler`) `Recall@3 = %89,5`'i **çok görünümlü** bir
havuzla ölçtü. Üretimdeki `app/oneri.py` ise ölçü başına **tek** metin gömüyordu.
Aynı etiketli küme (`lab/oneri_olcum.py::VAKALAR`, payda **19**) `ara()` boru hattının
tamamıyla koşuldu:

| temsil | `Recall@1` | `Recall@3` | `MRR` |
|---|---|---|---|
| çıplak etiket *(önceki üretim)* | %68,4 | **%68,4** | 0,703 |
| **çok görünümlü** *(bu hâl)* | %89,5 | **%89,5** | **0,895** |

`§13.1`'in karar tablosunda **%68,4 «🔴 DUR» bandıdır** (`< %70`). Yani ölüm şartı
yayınlanmış sayıya göre sağlanıyordu, **koşan koda** göre değil.

## ⚠ Bu dosyanın SINIRI — ve neden sahte gömücü

`tests/conftest.py:26` `DIMA_VQR_EMBEDDER=off` **zorlar**: hiçbir pytest koşumunda
gerçek gömücü yoktur. O hâlde `e5`'in sayılarını burada **tekrar edemeyiz** ve
etmiyoruz 🆆. Bunun yerine iki ayrı şey tutulur:

* **mekanizma** — hangi metinlerin gömülmeye gittiği (`gorunumler`); bu **deterministik**
* **davranış** — kısa-ad gürültüsünün düşmesi; `_UzunlukGomucu` ile, yani `§18.6`'nın
  tarif ettiği **kusur sınıfını** (kısa metinler birbirine yakın düşer) açıkça
  modelleyen bir sahte gömücüyle

⚠ 🅖 Sahte gömücü `e5` **değildir** ve öyleymiş gibi de sunulmuyor: yalnız *«çıplak
kısa ad gömülürse kısa sorgu onu çeker»* önermesini yalıtır. Gerçek sayı yukarıdaki
tabloda ve o tablo **gerçek gömücüyle** üretildi.
"""

from __future__ import annotations

import pytest

from app import oneri
from app.oneri import Aday, _anahtar, _gorunumler, ara, terimler

# ── Fikstür: ölçülen kusurun birebir kurulumu ───────────────────────────────
#
# `surdurulebilirlik.toplam_su_lt` ve `enerji_tesis.set_tep_ton` gerçek kataloğun
# etiketlerini taşır (`su` · `set` — ikisi de `label` yok, ilk sinonimden türemiş);
# `parti` tarafı sorgunun **gerçek** hedefidir 🅬.
_SEMA = {
    "version": "v18.7",
    "cubes": [
        {"name": "parti", "base_object": "partiler", "display": "parti",
         "measure_synonyms_display": {"toplam_fire_kg": "fire",
                                      "fire_orani_yuzde": "fire oranı",
                                      "toplam_ciro": "ciro"},
         "measure_synonyms": {"toplam_fire_kg": ["fire", "zayiat", "kayıp"],
                              "fire_orani_yuzde": ["fire oranı", "fire yüzdesi"],
                              "toplam_ciro": ["ciro", "hasılat"]},
         "units": {"toplam_fire_kg": "kg", "fire_orani_yuzde": "%",
                   "toplam_ciro": "₺"}},
        {"name": "surdurulebilirlik", "base_object": "partiler",
         "display": "sürdürülebilirlik",
         "measure_synonyms_display": {"toplam_su_lt": "su"},
         "measure_synonyms": {"toplam_su_lt": ["su", "su tüket", "toplam su"]},
         "units": {"toplam_su_lt": "lt"}},
        {"name": "enerji_tesis", "base_object": "enerji_tesis",
         "display": "tesis enerji (ISO-50001)",
         "measure_synonyms_display": {"set_tep_ton": "set"},
         "measure_synonyms": {"set_tep_ton": ["set", "spesifik enerji"]},
         "units": {"set_tep_ton": "ton"}},
    ],
}


class _UzunlukGomucu:
    """🔴 `§18.6`'nın kusur sınıfını **yalıtan** sahte gömücü.

    Vektör: `[1, len(metin)/10]`. Kosinüs iki metnin **uzunluğu yakınsa** büyür —
    yani anlam hiç taşınmaz, yalnız *«kısa metinler birbirine yakın düşer»* önermesi
    taşınır. `q=fi` ile `su` arasındaki gerçek yakınlığın kaynağı da budur (`§12.1`
    ölüm şartı bu yüzden **ölçülmeden** kabul edilemezdi).

    ⚠ 🅕 Bu gömücünün sayısı `e5`'e **taşınmaz** ve taşınıyormuş gibi kullanılmıyor:
    burada sınanan şey bir *skor* değil, **hangi metinlerin gömüldüğüdür**.
    """

    def __init__(self) -> None:
        self.gorulen: list[str] = []

    def embed(self, metinler):
        out = []
        for m in metinler:
            self.gorulen.append(m)
            out.append([1.0, len(m) / 10.0])
        return out


@pytest.fixture(autouse=True)
def _temiz_indeks():
    oneri._INDEKS.clear()
    yield
    oneri._INDEKS.clear()


# ── (a) 🔴🔴 ÇIPLAK KISA AD GÖMÜLMEZ — ölçülen kusurun kapısı ───────────────

def test_CIPLAK_KISA_AD_GOMULMEYE_GITMIYOR():
    """🔴 **Mekanizma yüklemi** — deterministik, gömücüye borçlu değil.

    `su` (2 harf) ve `set` (3 harf) hiçbir görünümde **yalnız başına** durmamalı;
    küp bağlamına füzelenmiş olmalı. `fire` (4 harf) ise kendi başına durabilir —
    o bir kısaltma değil, ölçünün **adı**dır.

    🅑 Mutasyon: `_gorunumler`'deki `_KISA_ESIK` dalı kaldırılırsa (etiket her hâlde
    çıplak gömülürse) bu yüklem kırılır.
    """
    havuz = {a.kimlik: a for a in terimler(_SEMA, None)}
    su = havuz["surdurulebilirlik.toplam_su_lt"].gorunumler
    st = havuz["enerji_tesis.set_tep_ton"].gorunumler
    fire = havuz["parti.toplam_fire_kg"].gorunumler

    assert "su" not in su, (
        f"🔴 ÇIPLAK KISA AD GÖMÜLÜYOR: {su} — `§18.7` tam bunu yasaklıyor; `q=fi` "
        "turunda `su·surdurulebilirlik` böyle geldi.")
    assert "set" not in st, f"🔴 çıplak `set` gömülüyor: {st}"
    assert "fire" in fire, (
        f"🔴 kendi başına duran bir ad da bağlama gömüldü: {fire} — kural kısa ada "
        "özeldir, her ada değil (aksi hâlde `fire` yazan kullanıcı da kaybederdi).")
    # Alan **kaybolmadı**: kısa etiket bağlamıyla hâlâ havuzda.
    assert any("su" in _norm_basit(g) for g in su), f"🔴 alan temsilsiz kaldı: {su}"
    assert any("set" in _norm_basit(g) for g in st), f"🔴 alan temsilsiz kaldı: {st}"


def _norm_basit(s: str) -> str:
    return str(s).lower()


#: Şeridin **darlığı** kusurun kendisidir: canlı turda `su`/`set` **7 yerin ikisini**
#: yemişti. Fikstür 5 adaylıdır, yani `7` tavanı burada hiçbir şeyi kesmez — o hâlde
#: kesme oranı korunur (`5` adayda `3`'lük şerit ≈ `136` adayda `7`'lik şerit) 🅫.
#: ⚠ Sayıyı fikstüre göre seçmek, ölçülen kusuru **taşınabilir** kılmak içindir.
_SERIT = 3


def test_KISA_AD_GURULTUSU_SERITTEN_DUSUYOR(monkeypatch):
    """🔴🔴 **Davranış hâli** — mekanizma yüklemi metin ölçüyordu, bu onu **koşturur** 🅯.

    `_UzunlukGomucu` altında `query: fi` (9 karakter) en çok `query: su` (9) ve
    `query: set` (10) ile yakınlaşır — ölçülen kusurun tam kopyası. Çok görünümlü
    temsille bu iki alanın **hiçbir** görünümü o kısalıkta değildir; şeritten düşerler
    ve yerlerini gerçek hedefler (`fire*` · `ciro`) alır.

    ⚠ Yüklem *«su/set hiç dönmesin»* **demiyor** — bunlar hâlâ havuzdadır ve `su`
    yazan kullanıcı onları bulur. Söylediği şey **şeritte yer kaplamasınlar**: vektör
    ayağı bir **sıralayıcıdır**, bir süzgeç değil (`test_oneri_motoru`'nun
    `test_VEKTOR_AYAGI_HICBIR_ADAYI_ELEMİYOR` yüklemi); eleme **kesmenin** işidir 🅗.
    """
    from app import vqr

    monkeypatch.setattr(vqr, "_embedder", lambda: _UzunlukGomucu())
    serit = [a.kimlik for a in ara("fi", _SEMA, izinliler=None, limit=_SERIT)]
    hepsi = [a.kimlik for a in ara("fi", _SEMA, izinliler=None)]

    for gurultu in ("surdurulebilirlik.toplam_su_lt", "enerji_tesis.set_tep_ton"):
        assert gurultu not in serit, f"🔴 kısa-ad gürültüsü hâlâ şeritte: {serit}"
        assert gurultu in hepsi, (
            f"🔴 alan ELENDİ ({gurultu}) — istenen şey düşürmek değil **geri plana "
            f"almaktı**; vektör ayağı süzgece dönmüş olabilir: {hepsi}")
    assert serit[0] == "parti.toplam_fire_kg", (
        f"🔴 `fi` sorgusunun gerçek hedefi başa gelmedi: {serit}")
    assert hepsi.index("parti.toplam_ciro") < hepsi.index(
        "surdurulebilirlik.toplam_su_lt"), (
        f"🔴 alakasız kısa ad, aynı küpteki gerçek bir ölçünün önünde: {hepsi}")


def test_ONCEKI_TEMSIL_AYNI_GOMUCUDE_GURULTUYU_GETIRIYORDU(monkeypatch):
    """🅑 **Karşı-kanıt (kontrol grubu).** Bir üstteki yüklem, düzeltmenin değil
    fikstürün eseri olabilir — bu yüklem onu çürütür: **aynı** sahte gömücü, **aynı**
    şema, **aynı** şerit; yalnız havuz eski usul (**çıplak etiket**) kurulur ve `su`
    şeride **geri gelir**.

    ⊙ Yani ölçülen fark temsilden geliyor, kurulumdan değil ㊳. *Bir düzeltmenin
    kanıtı, düzeltilmemiş hâlin aynı koşulda başarısız olmasıdır.*
    """
    from app import vqr

    monkeypatch.setattr(vqr, "_embedder", lambda: _UzunlukGomucu())
    eski = [Aday(kimlik=a.kimlik, etiket=a.etiket, cube=a.cube, kip="leksik",
                 gorunumler=(a.etiket,))                      # ← `§18.7` ÖNCESİ hâl
            for a in terimler(_SEMA, None)]
    monkeypatch.setattr(oneri, "terimler", lambda *_a, **_k: list(eski))

    serit = [a.kimlik for a in ara("fi", _SEMA, izinliler=None, limit=_SERIT)]
    assert "surdurulebilirlik.toplam_su_lt" in serit, (
        f"🔴 kontrol grubu kusuru ÜRETMEDİ ({serit}) — o hâlde bir üstteki yüklemin "
        "yeşilliği düzeltmenin kanıtı değildir; sahte gömücü kusur sınıfını "
        "modellemiyor ya da şerit yanlış seçilmiş demektir.")
    sira = oneri._vektor_sira("fi", eski, "eski")
    assert {eski[i].kimlik for i in sira[:2]} == {
        "surdurulebilirlik.toplam_su_lt", "enerji_tesis.set_tep_ton"}, (
        "🔴 çıplak temsilde vektör ayağının ilk iki sırası kısa adlar DEĞİL — "
        f"kusur sınıfı modellenmemiş: {[eski[i].kimlik for i in sira[:2]]}")


# ── (b) SİNONİM GÖRÜNÜMÜ — «zayiat» → toplam_fire_kg ───────────────────────

def test_SINONIM_GORUNUMU_ALANI_GETIRIYOR():
    """🔴 `§18.7`'nin `②` görünümü: sinonimler **cube_synonyms.yml**'de zaten var.

    *«zayiat»* katalogda hiçbir **etiket** değildir — yalnız `toplam_fire_kg`'nin
    sinonimidir. Çıplak-etiket temsilinde bu kelime alana **hiç** ulaşamıyordu
    (ölçüldü: gerçek gömücüyle `zayiat` → `bakiye, bakiye, kimyasal, set…`).

    ⊙ Ve bu ulaşma **gömücüye borçlu değildir**: yüklem `DIMA_VQR_EMBEDDER=off`
    altında koşar, yani leksik ayak sinonim görünümünde öneki bulur (`5.8`) 🅖.

    🅑 Mutasyon: `_leksik_sira` görünümler yerine `a.etiket`'e dönerse kırılır.
    """
    out = ara("zayiat", _SEMA, izinliler=None)
    assert out, "🔴 sinonim hiçbir aday getirmedi."
    assert out[0].kimlik == "parti.toplam_fire_kg", (
        f"🔴 sinonim görünümü alana bağlanmadı: {[a.kimlik for a in out]}")
    assert out[0].etiket == "fire", (
        "🔴 kullanıcıya sinonim gösteriliyor — eşleşen **görünüm** iç temsildir, "
        f"görünen ad katalogdaki etikettir: {out[0].etiket!r}")


def test_BIRIM_ve_KUP_BAGLAMI_GORUNUMLERI_KURULUYOR():
    """`③` ve `④` — üç kaynağın üçü de katalogda (`§18.7`: *«ek yazım işi yok»*)."""
    g = _gorunumler("fire", ["fire", "zayiat"], "parti", "kg")
    assert "fire" in g                        # ① görünen etiket
    assert "fire, zayiat" in g                # ② sinonim cümlesi
    assert "parti · fire" in g                # ③ küp bağlamı
    assert "fire (kg)" in g                   # ④ birim
    # Birim yoksa görünüm de yok — *«birim 0»* ile *«birim yok»* karıştırılmaz.
    assert not any("(" in x for x in _gorunumler("fire", [], "parti", ""))


# ── (c) TEKİLLEŞTİRME — aynı alan iki görünümden gelirse TEK aday ───────────

def test_AYNI_ALAN_IKI_GORUNUMDEN_GELSE_DE_TEK_ADAY(monkeypatch):
    """🔴 **Temsili zenginleştirmek, alanı birden çok kez saymak değildir.**

    `fire` sorgusu `parti.toplam_fire_kg`'nin **üç** görünümüne birden vurur
    (`fire` · `fire, zayiat, kayıp` · `parti · fire`). Naif bir kurulum havuzu
    görünüm başına kursaydı ⓐ aynı alan şeritte **üç kez** görünür ⓑ RRF onu görünüm
    ×3 ödüllendirir ⓒ `≤7` tavanı üç yeri **tek alana** harcardı 🆈.

    🅑 Mutasyon: `_vektor_sira`'daki `max` indirgemesi düşerse (görünüm sıraları
    doğrudan dönerse) ya da havuz görünüm başına kurulursa bu yüklem kırılır.
    """
    from app import vqr

    monkeypatch.setattr(vqr, "_embedder", lambda: _UzunlukGomucu())
    hedef = next(a for a in terimler(_SEMA, None)
                 if a.kimlik == "parti.toplam_fire_kg")
    assert len(hedef.gorunumler) >= 3, (
        f"🔴 fikstür yükü taşımıyor — hedefin {len(hedef.gorunumler)} görünümü var; "
        "tekilleştirme sınanamaz.")

    kimlikler = [a.kimlik for a in ara("fire", _SEMA, izinliler=None)]
    assert kimlikler.count("parti.toplam_fire_kg") == 1, (
        f"🔴 aynı alan şeritte birden çok kez: {kimlikler}")
    assert len(kimlikler) == len(set(kimlikler)), f"🔴 mükerrer aday: {kimlikler}"

    # Vektör ayağı da **alan** indeksi döndürür — görünüm indeksi değil.
    havuz = terimler(_SEMA, None)
    sira = oneri._vektor_sira("fire", havuz, "vX")
    assert len(sira) == len(set(sira)) <= len(havuz), (
        f"🔴 vektör ayağı görünüm indeksi döndürüyor olabilir: {sira} "
        f"(aday sayısı {len(havuz)})")
    assert all(0 <= i < len(havuz) for i in sira), f"🔴 sınır dışı indeks: {sira}"


def test_HAVUZ_BOYU_ALAN_BASINA_BIR_KALDI():
    """⑤'in koruması: görünüm zenginliği **envanteri şişirmemeli** — bir alan bir
    adaydır. (`test_oneri_motoru::test_YAPILANDIRILMAMIS…` bunu 5 sayısıyla ayrıca
    kilitliyor; burada gerekçesi yazılı duruyor.)"""
    havuz = terimler(_SEMA, None)
    assert len(havuz) == 5, f"🔴 havuz boyu değişti: {[a.kimlik for a in havuz]}"
    assert len({a.kimlik for a in havuz}) == 5
    assert all(a.gorunumler for a in havuz), "🔴 görünümsüz aday — temsil kurulmamış."


# ── (d) ÖNBELLEK ANAHTARI GÖRÜNÜM KÜMESİNİ TAŞIR ───────────────────────────

def test_ANAHTAR_GORUNUM_DEGISINCE_DEGISIYOR():
    """🔴 **`5.7`'nin üçüncü boyutu.** Matrisin satırları artık **görünümler**dir.

    Şema sürümü ve kimlikler **aynı** kalıp bir etiket/sinonim/birim değişirse (fikstür,
    kiracı-içi düzeltme, sinonim ekleme) eski matris yeni havuza **uymaz**. Anahtar
    bunu taşımazsa skorlar **yanlış görünüme** atanır: sessiz hizasızlık ㊴.

    🅑 Mutasyon: `_anahtar`'dan `gorunumler` parametresi düşürülürse kırılır.
    """
    assert _anahtar("v1", ("a",), ("fire",)) != _anahtar("v1", ("a",), ("zayiat",)), (
        "🔴 aynı kimlik, FARKLI görünüm → aynı anahtar; bayat bir matris okunur.")
    assert _anahtar("v1", ("a",), ("fire",)) == _anahtar("v1", ("a",), ("fire",))
    assert _anahtar("v1", ("a",), ("x", "y")) != _anahtar("v1", ("a",), ("xy",)), (
        "🔴 görünüm sınırı yutuluyor — `('x','y')` ile `('xy',)` ayrışmalı.")
    # ⚠ Geriye uyum: eski iki argümanlı çağrı (mevcut kapı) hâlâ ayrıştırıyor.
    assert _anahtar("v1", ("a", "b")) != _anahtar("v1", ("c", "d"))


def test_GORUNUM_DEGISINCE_YENIDEN_GOMULUYOR(monkeypatch):
    """🅯 Bir üstteki yüklem anahtarın **kendi özelliğini** ölçüyor; bu, yükü taşıyan
    yolu **koşturur** — çünkü ölçüldü ki yalnız anahtarı sınayan bir yüklem, anahtarın
    `_vektor_sira`'da **kullanılmamasını** göremez 🆎.
    """
    from app import vqr

    sahte = _UzunlukGomucu()
    monkeypatch.setattr(vqr, "_embedder", lambda: sahte)

    ara("fire", _SEMA, izinliler=None)
    ilk = len(sahte.gorulen)
    ara("ciro", _SEMA, izinliler=None)
    assert len(sahte.gorulen) - ilk == 1, (
        f"🔴 önbellek ıskalandı: {len(sahte.gorulen) - ilk} ek gömme (yalnız sorgu "
        "bekleniyordu) — anahtar her çağrıda değişiyor olabilir.")

    # 🔴 Aynı sürüm, aynı kimlikler — yalnız bir SİNONİM eklendi.
    zengin = {**_SEMA, "cubes": [
        {**_SEMA["cubes"][0],
         "measure_synonyms": {**_SEMA["cubes"][0]["measure_synonyms"],
                              "toplam_ciro": ["ciro", "hasılat", "gelir"]}},
        *_SEMA["cubes"][1:],
    ]}
    onceki = len(sahte.gorulen)
    ara("ciro", zengin, izinliler=None)
    assert len(sahte.gorulen) - onceki > 1, (
        "🔴 katalog metni DEĞİŞTİ (sürüm ve kimlikler aynı) ama YENİDEN GÖMÜLMEDİ — "
        "anahtar görünüm kümesini taşımıyor, bayat matris kullanılıyor.")


# ── ⊘ SINIR BEYANI — bu kapının ÖLÇMEDİĞİ ──────────────────────────────────

def test_SINIR_GERCEK_GOMUCU_BURADA_KOSMUYOR():
    """🅖 *Eksiği yayına yaz.* Bu dosyanın hiçbir yükleminde `e5` koşmaz
    (`conftest.py` `DIMA_VQR_EMBEDDER=off` zorlar). Yani buradaki yeşil, `%89,5`
    erişiminin **kanıtı değildir**; o sayı `lab/oneri_olcum.py` ile gerçek gömücüyle
    üretilir ve modül başlığında yazılıdır.

    Bu yüklem, o sınırın **sessizce kaybolmamasını** tutar: bir gün testler gerçek
    gömücüyle koşarsa kırmızı verir ve o gün buradaki sahte-gömücü yüklemleri gerçek
    sayılarla **yeniden düşünülmelidir** 🅕.
    """
    from app import vqr

    assert vqr._embedder() is None, (
        "🔴 Test ortamında GERÇEK gömücü koşuyor — bu dosyanın sahte gömücüleri artık "
        "`e5`'in yerine geçemez; yüklemler gerçek sayılara göre gözden geçirilmeli.")
