"""BELGE DÜZENİ KAPISI — *düzen bir kez kurulur, bir kural onu ayakta tutar.*

## Neden bu kapı var

Kök dizinde **16 markdown** birikmişti; üçü git'te bile değildi. Kimse yanlış bir şey
yapmamıştı — her biri yazıldığı gün doğru yere konmuştu, çünkü **yer diye bir şey
yoktu**.

> ⚠ *Bir düzen, onu koruyan kural olmadan yalnız bir temizlik günüdür.* Altı ay sonra
> aynı yığın, bu kez farklı adlarla geri gelir.

## Yerleşim kuralı — **bayatlama süresine göre**

| dizin | ne zaman bayatlar |
|---|---|
| kök (`OPERASYON*`) | ⟳ hiç — sürekli güncellenir, operasyonun giriş noktası |
| `belgeler/kilavuz/` · `mimari/` · `urun/` | ⟳ ürün/karar değişince — **canlı** |
| `belgeler/denetim/` · `devir/` | 🔒 **anında** — yazıldığı anın fotoğrafı, DEĞİŞTİRİLMEZ |
| `belgeler/arsiv/` | 🔒 zaten bayat |

*Bir denetim raporunu güncellemek, ölçümün ne zaman alındığını silmek demektir — ve
tarihi olmayan bir ölçüm, kıyaslanamaz bir sayıdır.*
"""

from __future__ import annotations

import pathlib
import re
import shutil
import subprocess

import pytest

_KOK = pathlib.Path(__file__).resolve().parents[2]
_BELGELER = _KOK / "belgeler"

# ═══════════════════════════════════════════════════════════════════════════════
# ⊘ ÖLÇÜLEMEDİĞİNDE **ATLA**, KALMA — ölçülmüş bir kusurun düzeltmesi
# ═══════════════════════════════════════════════════════════════════════════════
#
# 🔴 Bu dosya `backend/tests/` altında yaşıyor ama **repo kökünü** denetliyor.
# Standart test konteynerine yalnız `backend/` bağlanıyor (`-v "$PWD:/app"`) ve
# imajda `git` **yok**. Sonuç: dört test `FileNotFoundError` ve *"belgeler yok"*
# diye **KALIYORDU** — oysa belgeler yerinde, konteyner onları **göremiyor**.
#
# > ⚠ *Göremediği bir şeyi "yok" diye raporlayan bir test, ölçüm değil gürültü
# > üretir.* Ve gürültü üreten bir kapı, ilk kırmızısında güvenilirliğini kaybeder:
# > insan onu *"zaten hep kırmızı"* diye okumaya başlar.
#
# Doğrusu bu deponun kendi üçüncü hâli: **⊘ ÖLÇÜLEMEDİ** — geçmek de kalmak da
# değil. `pytest.skip` sebebiyle birlikte atlar; kapı sessizce yeşil görünmez,
# **atlandığını söyler**.
_KOK_GORUNUR = (_KOK / "belgeler").is_dir() and (_KOK / "OPERASYON.md").exists()
_GIT_VAR = shutil.which("git") is not None

_kok_gerekli = pytest.mark.skipif(
    not _KOK_GORUNUR,
    reason="⊘ ÖLÇÜLEMEDİ — repo kökü bu ortamda görünmüyor (konteynere yalnız "
           "`backend/` bağlı). Bu denetim repo kökünden koşulmalı: "
           "`cd backend && python -m pytest tests/test_belge_duzeni.py`")
_git_gerekli = pytest.mark.skipif(
    not (_KOK_GORUNUR and _GIT_VAR),
    reason="⊘ ÖLÇÜLEMEDİ — `git` bu ortamda yok (test imajında kurulu değil)")

#: 🔴 Kökte durabilecek **tek** belge kümesi — operasyonun giriş noktası.
#: `backend/CLAUDE.md` doğrudan bunlara işaret ediyor: bağlam sıfırlansa bile
#: operasyon buradan devam eder. Taşımak, girişi görünmez yapardı.
#:
#: ⟳ **`README.md` EKLENDİ (2026-08-13) — ve bu sessiz bir istisna değil, bir gerekçedir.**
#: Bu testin kendi şerhi *«yeni bir belge kökte durmak istiyorsa önce bu testin gerekçesi
#: değiştirilmeli»* diyordu; işte değiştiriliyor. Sebep ölçüldü: depoda **kök `README`
#: yoktu** ve depoya ilk bakan biri (insan ya da yeni oturum) `backend/` · `belgeler/` ·
#: `WrenAI-main/` · `lab/` yığınıyla karşılaşıp **nereden başlayacağını** bilmiyordu.
#: `OPERASYON*` üçlüsü bir **operasyonun** giriş noktasıdır — *«bu depo nedir, nasıl
#: koşar»* sorusunun cevabı değildir; üstelik o üçlü artık **önceki** operasyonu anlatıyor
#: (güncel durum `belgeler/plan/ONGORU-DURUM.md`) ⑳.
#: ⚠ `README.md` bir **yön tabelasıdır**: kendisi bilgi taşımaz, hepsini işaret eder —
#: yani bayatlaması *«bağ kırıldı mı»* sorusuna indirgenir ve onu bu dosyadaki
#: `test_INDEKS_kirik_bag_tasimaz` kardeşi kadar mekanik bir kapı tutabilir.
KOK_IZINLI = {"OPERASYON.md", "OPERASYON-DURUM.md", "OPERASYON-DENETIM.md", "README.md"}

#: Tarih damgalı ad kalıbı — tarih **başta** ki dizin kendiliğinden kronolojik sıralansın.
_TARIHLI = re.compile(r"^\d{4}-\d{2}-\d{2}_[\wÇĞİÖŞÜçğıöşü.\-]+\.md$")

#: ⟳ `§80` — **KURALIN ÖNGÖRMEDİĞİ ÜÇÜNCÜ SINIF: CANLI KAYIT DEFTERİ.**
#:
#: `denetim/` tanımı gereği 🔒 *«yazıldığı anın fotoğrafı, DEĞİŞTİRİLMEZ»*. Ama bu iki
#: dosya bir fotoğraf değil, **sürekli eklenen tek kayıt**: başlıkları da bunu söylüyor
#: (*«ajan bulgularının TEK KAYDI»* · *«bulgu → ölçüm → karar → kapı»*) ve ikisi de
#: bugün hâlâ güncelleniyor.
#:
#: Üç seçenek vardı ve ikisi yanlıştı: **(a)** tarih damgası vermek — *«değiştirilmez»*
#: sözünü yalan yapardı, çünkü ertesi gün yine yazılacak; **(b)** `belgeler/` köküne
#: taşımak — orası *«dışarıya verilen, **kapıyla** canlı tutulan»* sınıfıdır ve bu ikisini
#: canlı tutan bir kapı **yok** 🆆. Kalan doğru seçenek **(c)**: sınıfı **adıyla ilan et**
#: ㉖ ve listeyi **kısa** tut — bir muafiyet ne kadar uzarsa kural o kadar azalır.
#:
#: ⚠ Buraya yeni bir ad eklemek, *«bu dosya neden ne fotoğraf ne yayın»* sorusunu
#: **yazılı** cevaplamayı gerektirir. Cevap yoksa dosya ya tarihlenir ya taşınır.
DENETIM_CANLI_DEFTER = {"DENETIM-FAZ-A-F.md", "DENETIM-A-G.md"}


def _kok_md() -> list[str]:
    return sorted(p.name for p in _KOK.glob("*.md"))


@_kok_gerekli
def test_KOKTE_yalniz_operasyon_uclusu():
    """🔴 Kök üç dosyalıktır.

    *Bir istisna, bir sonraki istisnanın gerekçesi olur; ve üç istisna sonra kural
    kalmaz.* Yeni bir belge kökte durmak istiyorsa önce bu testin gerekçesi
    değiştirilmeli — sessizce eklenemez."""
    fazla = set(_kok_md()) - KOK_IZINLI
    assert not fazla, (
        f"🔴 kökte yeri olmayan belge: {sorted(fazla)}\n"
        "   → ölçüm mü? `belgeler/denetim/YYYY-AA-GG_KONU.md`\n"
        "   → talimat mı? `belgeler/kilavuz/`\n"
        "   → karar mı?   `belgeler/mimari/`  (önce backend/MIMARI.md'ye mi ait bak)\n"
        "   Kural: belgeler/00-INDEKS.md"
    )


@_kok_gerekli
def test_KOK_UCLUSU_yerinde():
    """Üçü de **var olmalı**: biri taşınırsa `backend/CLAUDE.md`'nin işaret ettiği
    giriş noktası kırılır ve bağlam sıfırlandığında operasyon **nereden devam
    edeceğini bilemez**."""
    eksik = KOK_IZINLI - set(_kok_md())
    assert not eksik, f"🔴 operasyon giriş dosyası kayıp: {sorted(eksik)}"


@_kok_gerekli
def test_DENETIM_raporlari_tarih_damgali():
    """`denetim/` **kronolojik bir arşivdir**: ad `YYYY-AA-GG_` ile başlar.

    ⚠ Tarih **başta**, sonda değil — sonda olsaydı dizin listesi konuya göre
    sıralanır ve *"en son ne ölçtük"* sorusu gözle taranarak cevaplanırdı."""
    if not (_BELGELER / "denetim").is_dir():
        return
    hatali = [p.name for p in (_BELGELER / "denetim").glob("*.md")
              if not _TARIHLI.match(p.name) and p.name not in DENETIM_CANLI_DEFTER]
    assert not hatali, (
        f"🔴 tarih damgası olmayan denetim raporu: {hatali} — "
        "ad `YYYY-AA-GG_KONU.md` olmalı.\n"
        "   Sürekli eklenen bir **kayıt defteri** ise `DENETIM_CANLI_DEFTER`'e "
        "**gerekçesiyle** yaz; gerekçesiz bir ad, sessiz bir kural aşınmasıdır.")


@_git_gerekli
def test_HER_BELGE_git_tarafindan_izleniyor():
    """⚠ İzlenmeyen bir belge **yalnız bu makinede vardır**.

    Kökteki 16 markdown'ın **üçü** git'te değildi — yani başka bir makinede o
    raporlar **yoktu** ve onlara atıf yapan her cümle kırıktı.
    *Paylaşılmayan bir belge, yazılmamış bir belgedir.*"""
    izlenen = set(subprocess.run(
        ["git", "ls-files", "*.md", "belgeler"], cwd=_KOK,
        capture_output=True, text=True, check=False).stdout.split())
    diskte = {str(p.relative_to(_KOK)) for p in _BELGELER.rglob("*.md")}
    diskte |= {p.name for p in _KOK.glob("*.md")}
    kayip = sorted(diskte - izlenen)
    assert not kayip, f"🔴 git'in görmediği belge: {kayip} — `git add` et"


@_kok_gerekli
def test_INDEKS_var_ve_her_dizini_anlatiyor():
    """İndeks olmadan bir dizin ağacı yalnız bir yığındır: hangi dosyanın **neden**
    orada olduğunu söyleyen tek şey odur."""
    indeks = _BELGELER / "00-INDEKS.md"
    assert indeks.exists(), "🔴 belgeler/00-INDEKS.md yok"
    m = indeks.read_text(encoding="utf-8")
    for d in sorted(p.name for p in _BELGELER.iterdir() if p.is_dir()):
        assert f"{d}/" in m, f"🔴 «{d}/» dizini indekste anlatılmıyor"


@_kok_gerekli
def test_INDEKS_kirik_bag_tasimaz():
    """⚠ İndeksteki kırık bir bağ, indeksi **olduğundan güvenilir** gösterir:
    okuyucu dosyanın var olduğunu sanır."""
    indeks = _BELGELER / "00-INDEKS.md"
    m = indeks.read_text(encoding="utf-8")
    kirik = []
    for hedef in re.findall(r"\]\((?!https?:)([^)]+)\)", m):
        yol = (indeks.parent / hedef).resolve()
        if not yol.exists():
            kirik.append(hedef)
    assert not kirik, f"🔴 indekste kırık bağ: {kirik}"


@_kok_gerekli
def test_TASINAN_BELGELERE_atif_kirilmadi():
    """🔴 **Taşımanın asıl bedeli**: bir belgeyi taşımak, ona atıf yapan her dosyayı
    kırar. Bu test eski (kök) yolların kodda/belgede **kalmadığını** sınar.

    ⚠ `belgeler/` içindeki dosyaların KENDİ adları hariç: `SERVER_COMMANDS.md`
    dizinin içinde geçebilir, orada zaten doğru yerdedir."""
    eski_yollar = ("SERVER_COMMANDS.md", "V1-SON-KONTROL.md", "UI-UX-DENETIM.md",
                   "V1-MIMARI-HARITASI.md", "CANLI_TEST_REHBERI.md",
                   "KULLANIM-KILAVUZU-v1.md", "TEST-ORTAMI-KILAVUZU.md")
    ihlal = []
    for f in list(_KOK.glob("*.md")) + list((_KOK / "backend").glob("*.md")):
        m = f.read_text(encoding="utf-8")
        for eski in eski_yollar:
            # Yalnız **öneksiz** atıf kırıktır; `belgeler/…/X.md` doğrudur.
            for eslesme in re.finditer(re.escape(eski), m):
                onceki = m[max(0, eslesme.start() - 20):eslesme.start()]
                if "belgeler/" not in onceki:
                    ihlal.append(f"{f.name} → {eski}")
                    break
    assert not ihlal, f"🔴 taşınmış belgeye ESKİ yolla atıf: {sorted(set(ihlal))}"
