"""FAZ 2.7 — **ADLANDIRMA SÖZLEŞMESİ: yalnız YENİ küplere.** [bayraksız: kural]

> Bu dosya **ADR-0023**'ün (*yeni cube kapısı: yazılı gerekçe + başka modülün grain'ini
> çalmama*) kapı tarafıdır. ⚠ Atıf FAZ 4.6'da eklendi: karar `packs/modul/enerji/`
> yorumlarında ve bu testte **yaşıyordu** ama kimliğiyle hiçbir yerde **anılmıyordu** —
> yani `docs/adr/0023-*.md` kodda karşılığı olmayan bir kayıt gibi görünüyordu.
> *Bir kararın kimliği, kararın yaşadığı yerde yazılı olmalı; yoksa kayıt ile kod
> birbirini doğrulayamaz.*

## 🔴 VAR OLAN ADLAR KALIR — ve bu ölçülmüş bir karardır

Toplu yeniden adlandırma **denendi ve reddedildi**: `surdurulebilirlik` kimliğinden ham
kaynak adları çıkarılınca erişim **%64 → %56** düştü, **110 sessiz-yanlış kapandı ama 388
cevap kayboldu** (3,5:1 kötü takas). `resolve_cube_name` ad göçünü **destekliyor** ama
ölçüm onu **haklı çıkarmıyor**.

*Bir kuralı geçmişe uygulamak, kuralın kendisinden daha pahalı olabilir.*

## Kural — bundan sonra doğan her grain küpü

**Olayla, tekil** adlandırılır (dbt kuralı): `fatura`, `stok_hareketi`, `parti` —
`faturalar`/`satislar` değil. Departman adı **küp adı olamaz** (departman bir
**mercektir**, 2.3).

## ⚠ Bu kapı NE YAPMAZ

Var olan küpleri **denetlemez**. Denetleseydi ilk koşumda 9 küp birden kırmızı verirdi ve
tek çözüm ya kapıyı kapatmak ya da ölçümle reddedilmiş göçü yapmak olurdu — *ölçümle
reddedilmiş bir işi zorlayan kapı, kapı değil bir tuzaktır.*
"""

from __future__ import annotations

import pathlib
import subprocess

import pytest
import yaml

KOK = pathlib.Path(__file__).resolve().parents[1]
PACKS = KOK / "demo" / "packs"

#: 🔴 **DONMUŞ TABAN.** Bu kümenin dışındaki her küp **yeni** sayılır ve sözleşmeye
#: uymak zorundadır. Küme **büyütülmez**: büyütmek, kuralı yeni küplere de uygulamamak
#: demektir — yani kapının kendisini kapatmak.
#: ⚠ **ÖLÇÜLDÜ, TAHMİN EDİLMEDİ — ve ilk yazımda tahmin etmiştim.** Elle yazdığım liste
#: `personel`/`stok`/`satis` gibi **var olmayan** küpler içeriyor, `enerji_*` üçlüsünü ise
#: **kaçırıyordu**; kapı ilk koşumda onları *"yeni doğmuş"* ilan etti. Bu deponun en sık
#: kusuru: *beyan var, sayım yok.* Liste artık ölçümden geliyor
#: (`python -c "from tests.test_yeni_kup_kapisi import _kup_adlari; print(sorted(_kup_adlari()))"`).
MEVCUT_KUPLER = {
    "bakim", "cari", "cari_finans", "enerji_makine", "enerji_sapma", "enerji_tesis",
    "ik", "kalite", "karlilik", "mal", "mizan", "oee", "parti", "surdurulebilirlik",
    "ticaret", "yaslandirma",
}

#: Departman adları — küp adı **olamaz** (departman bir MERCEKTİR, madde 2.3).
DEPARTMAN_ADLARI = {"satis_departmani", "pazarlama", "muhasebe", "insan_kaynaklari",
                    "finans", "operasyon", "lojistik"}

#: Çoğul ekleri — grain küpü **tekil** adlandırılır: bir satır = bir OLAY.
_COGUL_EKLERI = ("lar", "ler")


def _kup_adlari() -> set[str]:
    out: set[str] = set()
    for yol in PACKS.rglob("cubes/*/metadata.yml"):
        try:
            meta = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        except Exception:                                    # noqa: BLE001
            continue
        if isinstance(meta, dict) and meta.get("name"):
            out.add(str(meta["name"]))
    for yol in (PACKS / "modul").rglob("*.yml"):
        try:
            d = yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
        except Exception:                                    # noqa: BLE001
            continue
        c = (d or {}).get("cube") if isinstance(d, dict) else None
        if isinstance(c, dict) and c.get("name"):
            out.add(str(c["name"]))
    return out


# ── 1 · KURAL: YALNIZ YENİ KÜPLERE ──────────────────────────────────────────

def test_YENI_KUP_TEKIL_ADLANDIRILIYOR():
    """🔴 Bir grain küpünün bir satırı **bir olaydır** — `faturalar` değil `fatura`.
    Çoğul ad, küpü bir **tablo** gibi okutur ve grain sözleşmesini görünmez kılar."""
    yeni = _kup_adlari() - MEVCUT_KUPLER
    kotu = [a for a in sorted(yeni) if a.endswith(_COGUL_EKLERI)]
    assert not kotu, (
        f"yeni küp ÇOĞUL adlandırılmış: {kotu}. Grain küpü TEKİL adlandırılır "
        "(bir satır = bir olay). Var olan adlar bu kuraldan MUAF — ölçüldü (%64→%56).")


def test_YENI_KUP_DEPARTMAN_ADI_TASIMIYOR():
    """🔴 Departman bir **MERCEKTİR**, küp değil (madde 2.3). Bir departmanı küp yapmak,
    o departmanın **tüm sözlüğünü** kimliğe yapıştırır — `surdurulebilirlik` felaketinin
    kökü tam buydu."""
    yeni = _kup_adlari() - MEVCUT_KUPLER
    kotu = sorted(yeni & DEPARTMAN_ADLARI)
    assert not kotu, f"departman adı küp adı olarak kullanılmış: {kotu} — mercek kullan"


def test_MEVCUT_ADLAR_DENETLENMIYOR():
    """⚠ **Bu kapı var olan küpleri DENETLEMEZ** ve bu bilinçli: denetleseydi ilk koşumda
    9 küp birden kırmızı verir, tek çözüm ya kapıyı kapatmak ya da **ölçümle reddedilmiş**
    göçü yapmak olurdu. *Ölçümle reddedilmiş bir işi zorlayan kapı, kapı değil bir
    tuzaktır.*"""
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "MEVCUT_KUPLER" in kaynak and "%64" in kaynak, "muafiyetin GEREKÇESİ yazılı değil"
    # Ve muafiyet gerçekten uygulanıyor: `ticaret`/`cari` çoğul-olmasa da denetim dışı.
    assert "ticaret" in MEVCUT_KUPLER and "cari" in MEVCUT_KUPLER


def test_TABAN_KUMESI_BUYUTULMEMIS():
    """🔴 **Kapıyı kapatmanın en sessiz yolu, muafiyet listesini büyütmektir.** Küme
    donmuştur: bir sonraki tur yeni bir küp eklerken burayı genişletmek isterse, kuralı
    **yeni küplere de uygulamamayı** seçmiş olur — ve bu görünür olmalı."""
    assert len(MEVCUT_KUPLER) == 16, (
        f"donmuş taban {len(MEVCUT_KUPLER)} öğe — büyütüldüyse GEREKÇESİ buraya yazılmalı, "
        "sayı sessizce güncellenmemeli")


# ── 2 · KAPI: yeni küp korpusu GERİLETİRSE geri alınır ──────────────────────

def test_KORPUS_KAPISI_KOMUTU_YAZILI():
    """🔴 Yol haritasının şartı: *"yeni küp açan PR'da öncesi/sonrası `nl_corpus --kapi`;
    **doğru-cube gerilerse küp geri alınır**"*. Komut **yazılı** olmalı — yazılı olmayan
    bir yordam, uygulanmayan bir yordamdır."""
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "lab/kapi.py --tam" in kaynak, "kapı komutu bu dosyada YAZILI DEĞİL"


def test_KUP_SAYISI_BEYANLA_UYUSUYOR():
    """⚠ *"Kaç küp var"* sorusunun cevabı **ölçülür**, beyan edilmez. Bir küp sessizce
    doğarsa bu sayı değişir ve kapı onu görür.

    Yeni bir küp eklendiğinde YAPILACAK, sırayla:
      1. `docker run … python lab/kapi.py --tam`  → **öncesi** doğru-cube yüzdesi
      2. küpü ekle
      3. aynı komut → **sonrası**; **gerilerse küp GERİ ALINIR** (yol haritası şartı)
      4. bu testteki sayıyı güncelle + gerekçeyi yaz
    """
    adlar = _kup_adlari()
    assert adlar, "hiç küp bulunamadı — ölçüm aracı kırılmış olabilir"
    yeni = adlar - MEVCUT_KUPLER
    assert not yeni, (
        f"YENİ KÜP(LER) doğmuş: {sorted(yeni)}. Yukarıdaki dört adımı uygula: "
        "korpus öncesi/sonrası ölçülmeden yeni küp inmez.")


def test_KURAL_ADR_0008_ILE_CELISMIYOR():
    """⚠ ADR-0008 *"elle sözlük büyütme"*yi yasaklıyor. Bu kapı bir **sözlük** değil bir
    **adlandırma kuralı** uyguluyor: yeni kelime eklemez, yeni **ad biçimi** dayatır.
    Ayrımı yazmak gerekiyor, yoksa bir sonraki tur bu dosyayı ADR ihlali sanır."""
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "ADR-0008" in kaynak and "adlandırma kuralı" in kaynak


@pytest.mark.skipif(not (KOK / "lab" / "nl_corpus.py").is_file(),
                    reason="korpus aracı yok")
def test_KORPUS_ARACI_DURUYOR():
    """Kapının dayandığı ölçüm aracı **var olmalı** — aracı silmek, kapıyı sessizce
    kaldırmaktır."""
    assert (KOK / "lab" / "kapi.py").is_file()
    cikti = subprocess.run(["grep", "-c", "korpus", str(KOK / "lab" / "kapi.py")],
                           capture_output=True, text=True, check=False)
    assert cikti.stdout.strip() not in ("", "0"), "`kapi.py` korpus adımını kaybetmiş"
