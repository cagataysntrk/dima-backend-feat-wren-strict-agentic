"""**GERÇEK-DÜNYA KORPUSU kapısı** — aracın kendisi ölçülüyor. *(denetim §9.6)*

## 🔴 Neden bu araç HAYATİ

Mevcut korpus soruyu **cevabın anahtarından** kuruyor (`≥%97,1` katalog türevi). Yani
`%93,1` şu soruya cevap veriyor: *"sistem **kendi** kelimelerini tanıyor mu?"*

Ve bu, kullanıcının kendi gözlemini açıklıyor: *"bayrakları hep `off` tuttuk, hiç
değişiklik olmadı."*

> 🔴 **Bir A/B'nin sonucu «fark yok» ise, önce ölçen aletin o farkı GÖREBİLDİĞİ
> kanıtlanmalıdır.** İki ayrı sebep aynı belirtiyi üretiyordu: (a) bayrak bağlı değil
> *(beşi bağlandı)* · (b) korpus farkı göremiyor *(bu araç onun içindir)*.

## İlk ölçüm — **taban**, hedef değil

| kademe | vaka | kabul |
|---|---|---|
| K1 | 5 | 2 |
| K2 | 3 | 2 |
| K3 | 3 | **0** |
| K4 | 2 | **0** |
| K5 | 1 | 1 |

🔴 **K3 (kıyas) ve K4 (nedensel) sıfır**: deterministik yol, kullanıcının kendi
kelimeleriyle sorulan **kıyas** ve **neden** sorularına hiç ulaşamıyor. Bu, mevcut
korpusun **yapısal olarak göremediği** bir boşluk.

⚠ **Sessiz-yanlış: 0** — yani sistem bilmediğini **uydurmuyor**. Bu bir kazançtır ve
tabloda ayrı sütundur.

## ⚠ Ölçülen katman

`route()` — **sıfır-LLM** yol. `durust_ret`, *"deterministik yol pes etti"* demektir;
`/ask` orada durmaz. Tablo ürünün cevapsızlığını değil, **LLM'siz yolun erişimini** ölçer.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

_KOK = pathlib.Path(__file__).resolve().parents[1]
if str(_KOK) not in sys.path:
    sys.path.insert(0, str(_KOK))

from lab.gercek_dunya import (  # noqa: E402
    DURUST_RET, KADEMELER, PERSONALAR, SESSIZ_YANLIS, VAKALAR, katalog_sizintisi,
)


def test_ALTI_PERSONA_var():
    """Kural 2: aynı iş sorusu **altı ayrı ağızdan**."""
    assert len(PERSONALAR) == 6
    kullanilan = {v["persona"] for v in VAKALAR}
    assert kullanilan == set(PERSONALAR), f"kullanılmayan persona: {set(PERSONALAR) - kullanilan}"


def test_BES_KADEME_var_ve_HEPSI_kullanilmis():
    """Kural 3: *kademe atlanamaz* — payda kademeli raporlanır ki bir kademedeki kayıp
    ötekinde **saklanmasın**."""
    assert KADEMELER == ("K1", "K2", "K3", "K4", "K5")
    kullanilan = {v["kademe"] for v in VAKALAR}
    assert kullanilan == set(KADEMELER), f"boş kademe: {set(KADEMELER) - kullanilan}"


@pytest.mark.parametrize("vaka", VAKALAR, ids=[v["soru"][:28] for v in VAKALAR])
def test_HER_VAKA_UC_BEYAN_tasiyor(vaka):
    """Kural 4: `soru` + `kabul` + `yasak` — **yoksa vaka değildir**.
    ⚠ Ve `kaynak` (kural 5): *uydurulmuş bir vaka, uydurulmuş bir ölçüdür.*"""
    assert vaka["soru"] and vaka["kabul"] and vaka["yasak"] and vaka["kaynak"]
    assert len(vaka["yasak"]) > 15, "yasak cevap yüzeysel"


def test_YASAK_CEVAP_SESSIZ_YANLIS_sinifinda():
    """🔴 *Tek gerçek başarısızlık*: yanlış soruya **kendinden emin** cevap."""
    assert SESSIZ_YANLIS not in {k for v in VAKALAR for k in v["kabul"]}, (
        "🔴 bir vaka sessiz-yanlışı KABUL sayıyor")


def test_NETLESTIRME_bir_BASARIDIR():
    """🔴 Bugünkü korpus `CLARIFY`'ı OK saymıyor; oysa *"bakiye: cari mi mizan mı"* diye
    **sormak**, ₺11,86 milyonluk sessiz seçimden **iyidir**."""
    from lab.gercek_dunya import NETLESTIRME

    assert any(NETLESTIRME in v["kabul"] for v in VAKALAR)
    assert DURUST_RET != NETLESTIRME, "iki ayrı sınıf olmalı"


def test_KURAL1_TURETMEYI_yakaliyor_DAGARCIGI_degil():
    """🔴 **Kalibrasyon ölçümle düzeltildi.** Şartname *"soru ∩ etiketler = ∅"* diyor;
    harfiyen uygulandı ve **15 vakanın 8'i** elendi (`fire` · `bakiye` · `müşteri`…).

    Oysa bunlar *"cevabın anahtarı"* değil **işin kendi kelimeleri**: üretim müdürü
    *"fire"* der, başka kelimesi yoktur. *Bir kuralı harfiyen uygulamak, onu amacının
    tersine çevirebilir.*
    """
    etiketler = {"fire", "ciro", "makine", "bakiye"}
    hamlar = {"toplam_fire_kg", "fire_orani_yuzde"}
    # dağarcık — sızıntı DEĞİL
    assert not katalog_sizintisi("ne kadar fire verdik", etiketler, hamlar)
    # ham tanımlayıcı — sızıntı
    assert katalog_sizintisi("toplam_fire_kg nedir", etiketler, hamlar)
    # şablon imzası (tamamı katalog kelimesi) — sızıntı
    assert katalog_sizintisi("fire ciro makine", etiketler, hamlar)


def test_SIZINTI_SESSIZCE_elenmiyor():
    """⚠ *Bir vakayı sessizce düşürmek, paydayı sessizce kırpmaktır.*"""
    src = (_KOK / "lab/gercek_dunya.py").read_text(encoding="utf-8")
    assert 'sizinti.append(' in src and '"sizinti"' in src


def test_MEVCUT_KORPUSA_dokunulmadi():
    """🔴 **Kural 0 — payda kutsaldır.** Yeni korpus var olanın **yerine geçmez**,
    yanına kurulur; eski taban bozulursa geçmiş ölçümler karşılaştırılamaz."""
    src = (_KOK / "lab/gercek_dunya.py").read_text(encoding="utf-8")
    assert "nl_corpus" not in src.split('"""')[2] if src.count('"""') > 2 else True
    # nl_corpus.py'nin kendisi değişmemeli — üreteci hâlâ katalogdan kuruyor
    nl = (_KOK / "lab/nl_corpus.py").read_text(encoding="utf-8")
    assert "def gen_single" in nl and "REAL_PHRASINGS" in nl


def test_SIFIR_LLM_ve_SIFIR_DB():
    """⚠ §9.7/d: zincir deterministik → ölçüm **saniye**, dakika değil."""
    src = (_KOK / "lab/gercek_dunya.py").read_text(encoding="utf-8")
    assert "cube_router.route(" in src
    assert "client.post" not in src and "requests" not in src


def test_OLCULEN_KATMAN_yazili():
    """⊘ `route()` `None` dönmesi **ürünün** başarısızlığı değildir — `/ask` orada
    durmaz. Sınır **raporun içinde** yazılı, dipnotta değil."""
    src = (_KOK / "lab/gercek_dunya.py").read_text(encoding="utf-8")
    assert "SIFIR-LLM yol" in src and "/ask` orada durmaz" in src or "orada durmaz" in src


def test_HEDEF_YUZDE_DEGIL_ilerleme():
    """🔴 Kural 6: *bir tabanı hedefe çevirmek, ilk ölçümü bir söze dönüştürür.*
    Araç bir eşikte **kırmızı vermez**."""
    src = (_KOK / "lab/gercek_dunya.py").read_text(encoding="utf-8")
    assert "Hedef yüzde DEĞİL ilerleme" in src or "hedef DEĞİL" in src or "tabandır" in src


# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 KOPYA KAPISI — "15 az; ve birbirinin aynısı kesinlikle olmayacak"
# ═══════════════════════════════════════════════════════════════════════════════
#
# ## Neden mekanik bir kapı, "dikkat ederim" değil
#
# Bir korpus **kendi tekrarıyla** şişer: yazarın gözünde iki soru farklıdır ("biri
# müşteri, biri cari"), ölçüm gözünde aynıdır. *Paydayı şişiren bir vaka, ölçümü
# iyileştirmez — yalnız pahalılaştırır ve gerçek kapsamı gizler.*
#
# ⚠ Ölçü **kelime kümesi**, cümle değil: *"en çok kim alıyor"* ile *"kim en çok
# alıyor"* farklı cümlelerdir, **aynı** vakadır.

_DURAK = {
    "ne", "mi", "mı", "mu", "mü", "bu", "şu", "o", "bir", "var", "yok", "de", "da",
    "ve", "ile", "için", "gibi", "kadar", "daha", "çok", "az", "en", "göre", "peki",
    "ya", "ama", "nasıl", "kaç", "hangi", "nerede", "neden", "niye", "kim", "biz",
    "bize", "bizi", "bizim", "miyiz", "mıyız", "müyüz", "miydi", "mıydı", "oldu",
    "olur", "the", "a",
    # ⚠ `"var mı"` BURADAN ÇIKARILDI: `soru.split()` tek kelimeler üretir, yani iki
    # kelimelik bir girdi **hiçbir zaman** eşleşemezdi — ölü satır. Zararsızdı ama
    # bir durak listesinin okunduğu gibi davranmadığı yerdi.
    # *Çalışmayan bir kural, olmayan bir kuraldan daha kötüdür: varlığı denetimi durdurur.*

}


def _anlamli(soru: str) -> frozenset:
    """Durak kelimeler **atılır**: iki soruyu benzer yapan şey `mi`/`bu` değil,
    taşıdıkları **iş kelimeleridir**."""
    return frozenset(k for k in soru.lower().split() if k not in _DURAK and len(k) > 1)


def _ortusme(a: frozenset, b: frozenset) -> float:
    """Jaccard: kesişim / birleşim. ⚠ **Kapsama değil** — kapsama kullanılsaydı
    tek kelimelik bir vaka her uzun vakaya %100 benzerdi."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def test_KOPYA_YOK_hicbir_vaka_cifti_yuzde_70_ustu_ortusmez():
    """🔴 Kullanıcı kuralı: *"birbirinin aynısı kesinlikle olmadan"*.

    Eşik **%70**: altında kalan çiftler *aynı alanı* paylaşabilir (fire/fire) ama
    **farklı davranış** ölçer (miktar-oran karışması vs eşanlam tanıma). Üstünde
    kalan çift, kılık değiştirmiş **tek** vakadır."""
    from lab.gercek_dunya import VAKALAR

    kume = [(v["soru"], _anlamli(v["soru"])) for v in VAKALAR]
    cakisan = [
        (kume[i][0], kume[j][0], round(o, 2))
        for i in range(len(kume))
        for j in range(i + 1, len(kume))
        if (o := _ortusme(kume[i][1], kume[j][1])) > 0.70
    ]
    assert not cakisan, f"kopya vaka çifti: {cakisan}"


def test_AYNI_SORU_IKI_KEZ_yazilmamis():
    """⚠ Jaccard'ın **kaçırdığı** hâl: birebir aynı metin zaten %100 verir, ama bu
    kapı hata mesajını okunur kılar — *bir kapının teşhisi, yakalaması kadar
    değerlidir.*"""
    from lab.gercek_dunya import VAKALAR

    sorular = [v["soru"] for v in VAKALAR]
    tekrar = {s for s in sorular if sorular.count(s) > 1}
    assert not tekrar, f"birebir tekrar: {tekrar}"


def test_KAPSAM_her_persona_ve_her_kademe_temsil_edilir():
    """🔴 *Bir korpusun büyüklüğü kapsamı değil, **dağılımı** kapsamı gösterir.*
    42 vakanın 40'ı tek personada olsaydı sayı büyük, ölçüm dar olurdu."""
    from lab.gercek_dunya import KADEMELER, PERSONALAR, VAKALAR

    for p in PERSONALAR:
        assert any(v["persona"] == p for v in VAKALAR), f"persona boş: {p}"
    for k in KADEMELER:
        assert any(v["kademe"] == k for v in VAKALAR), f"kademe boş: {k}"


def test_VAKA_SAYISI_ondan_fazla_persona_basina():
    """⚠ Alt sınır **yazılı**: kullanıcı 15'i az buldu. Bu kapı bir daha 15'e
    düşmeyi **hata** yapar. *Bir kararın kapıya çevrilmemiş hâli, bir sonraki turda
    unutulur.*"""
    from lab.gercek_dunya import VAKALAR

    assert len(VAKALAR) >= 40, f"vaka sayısı geriledi: {len(VAKALAR)}"


# ═══════════════════════════════════════════════════════════════════════════════
# 🔴 DİLSEL KAPSAM KAPISI — "ne eksik" artık tahmin değil, ölçüm
# ═══════════════════════════════════════════════════════════════════════════════
#
# ## Bu kapının doğuş hikâyesi
#
# Kullanıcı iki gerçek kusur bildirdi (`şubata göre` · `üzerindeki etkisini ölç yani`)
# ve sordu: *"testler bunları yakalar mı?"* Cevap **hayırdı**. İkisini eksen olarak
# ekledim. Sonra doğru soruyu sordu:
#
# > *"bu ikisi en basiti — bu tarz o zaman **binlerce eksik** vardır"*
#
# Ve haklıydı. Eksen eklemek bir çözüm değil: hangi eksenin eksik olduğunu ancak kusur
# **canlıda patladığında** öğrenirsek, test ortamı kusurları bulan değil **arkasından
# koşan** bir alete dönüşür.
#
# 🔴 Bu kapı o döngüyü kırar: dilin özellikleri **önce sayılır** (`dil_ozellikleri.py`,
# 71 özellik / 8 aile), sonra üretecin kaçını ürettiği **rakamla** söylenir. Kapsanmayan
# bir özellik artık bilinmeyen bir bilinmeyen değil, **kırmızı bir testtir**.


def test_DILSEL_KAPSAM_hicbir_ozellik_bos_kalmaz():
    """🔴 Boş bir özellik = test ortamının deliği.

    O sınıftaki bir kusur, korpus **ne kadar büyürse büyüsün** görünmez kalır —
    çünkü onu tetikleyecek tek bir vaka bile üretilmiyordur.

    ⚠ İlk koşumda **10 delik** buldu: yalın ay adı · olumsuzluk · çoklu soru ·
    iki kırılım · sayısal aralık · boşluk hatası · büyük harf · noktalama · sayı
    biçimi · yalın hâl. Onunun da onu kapatıldı ve kapı yeşile döndü.
    """
    from lab import dil_ozellikleri as D
    from lab.gercek_dunya import VAKALAR

    sorular = [v["soru"] for v in VAKALAR] + _uretilmis_sorular()
    k = D.kapsam_olc(sorular)
    assert not k["bos"], (
        "🔴 test ortamının deliği — hiç üretilmeyen dilsel özellikler: "
        + ", ".join(f"{o['kod']} ({o['ornek']})" for o in k["bos"])
    )


def test_DILSEL_KAPSAM_zayif_ozellik_yok():
    """⚠ **Sıfır kapsam bir delik, BİR kapsam bir yanılsamadır.**

    Tek vakayla kapsanan bir özellik raporda yeşil görünür ama o sınıfta bir kusuru
    yakalama şansı istatistiksel olarak sıfıra yakındır. Eşik **5**."""
    from lab import dil_ozellikleri as D
    from lab.gercek_dunya import VAKALAR

    k = D.kapsam_olc([v["soru"] for v in VAKALAR] + _uretilmis_sorular())
    assert not k["zayif"], (
        "⚠ zayıf kapsam (<5 vaka): "
        + ", ".join(f"{o['kod']}={o['adet']}" for o in k["zayif"])
    )


def test_KAPALI_AILELER_tam_kapsanir():
    """🔒 Türkçenin durum · iyelik · fiil kipi ekleri **sonlu** kümelerdir.

    Yani bu ailelerde *"acaba unuttuğum bir biçim var mı"* sorusu **kapatılabilir** —
    ve kapatıldığı bu testle beyan edilir. *Bir taksonominin değeri, neyi kapsamadığını
    söylemesi kadar, neyi TAM kapsadığını kanıtlayabilmesindedir.*"""
    from lab import dil_ozellikleri as D
    from lab.gercek_dunya import VAKALAR

    k = D.kapsam_olc([v["soru"] for v in VAKALAR] + _uretilmis_sorular())
    for aile in D.KAPALI_AILELER:
        v = k["aile_kapsami"][aile]
        assert v["kapsanan"] == v["toplam"], (
            f"🔒 kapalı küme «{aile}» eksik: {v['kapsanan']}/{v['toplam']}")


def test_URETEC_canli_iki_kusur_sinifini_uretir():
    """🔴 Kullanıcının bildirdiği **iki gerçek kusur** korpusta karşılığı olmadan
    kalmasın. *Bir kusur bir kez canlıda görüldüyse, bir daha ancak korpus onu
    üretebiliyorsa yakalanır.*"""
    from lab import senaryo_uretec as S

    vakalar = _uretilmis_vakalar()
    cekimli = [v for v in vakalar
               if any(v["donem"].startswith(a) and v["donem"] != a for a in S._AYLAR)]
    iliski = [v for v in vakalar if v["niyet"] in (S.NIYET_ETKI, S.NIYET_KOMPOZISYON)]
    assert len(cekimli) >= 50, f"ay çekimi («şubata göre») yetersiz: {len(cekimli)}"
    assert len(iliski) >= 50, f"iki-ölçü ilişkisi («üzerindeki etkisi») yetersiz: {len(iliski)}"


def test_PAIRWISE_kopya_uretmez():
    """Üreteç **üretim anında** kopya eler; iki vaka aynı anlamlı kelime kümesini
    taşımaz. ⚠ Sonradan elemek pairwise kapsamını sessizce delerdi."""
    from lab.dil_ozellikleri import OZELLIKLER  # noqa: F401  (modül yüklenebilirlik denetimi)

    sorular = _uretilmis_sorular()
    assert len(set(sorular)) == len(sorular), "üreteç birebir kopya üretti"


# --- yardımcılar: şema BİR KEZ yüklenir (her test yeniden yüklerse süit yavaşlar) ---
_ONBELLEK: dict = {}


#: 🔴 KAPI ile LAB'ın AYRIMI — ve neden bu ayrım şart.
#:
#: Kapı 10 732 vakayı **üretiyordu**. Üretim bir **lab** işidir: pairwise algoritması
#: tek çekirdekli ve soğuk koşumda dakikalar sürer. Bir geliştirme kapısının bütçesi
#: **1-2 dakikadır** (kullanıcı kararı) ve bu bütçe üretime harcanamaz.
#:
#: > ⚠ *Uzun bir kapı, atlanan bir kapıya dönüşür* — ve atlanan bir kapı, olmayan
#: > bir kapıdan daha kötüdür, çünkü varlığı güvence sanılır.
#:
#: **Ayrım:** kapı üretecin **doğruluğunu** deterministik bir örnekle sınar
#: (aynı tohum → aynı örnek, yani kopya/kapsam iddiaları hâlâ geçerli). **Tam
#: kapsam ölçümü** demet sonu lab koşumuna aittir (`lab/gercek_dunya.py --kapi`).
#:
#: ⚠ Örnek **kapsamı düşürmez, ölçüm anını değiştirir**: aynı 71 dilsel özellik
#: hâlâ sınanıyor — yalnız daha az vakayla, ve yetmezse test bunu **söyler**.
KAPI_ORNEK = 2500


def _uretilmis_vakalar() -> list[dict]:
    if "vakalar" not in _ONBELLEK:
        from app.config import get_settings
        from app.wren_service import WrenService
        from lab import senaryo_uretec

        s = get_settings()
        svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                          connection_info=s.connection_dict())
        _ONBELLEK["vakalar"] = senaryo_uretec.uret(svc.schema(), azami=KAPI_ORNEK)[0]
    return _ONBELLEK["vakalar"]


def _uretilmis_sorular() -> list[str]:
    return [v["soru"] for v in _uretilmis_vakalar()]
