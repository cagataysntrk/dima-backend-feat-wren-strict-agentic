"""FAZ 4.6 kapısı — **kodda anılan her ADR kimliğinin bir DOSYASI var.**

## Ölçülen boşluk

**20 ADR kimliği · 252 atıf · 0 dosya** (doğrulandı, MIMARI §8.2). Ve bunun bir maliyeti
vardı: **`ADR-0007-K3`, v1'in §C/3 çıkış ölçütünü taşıyor** — yani ürünün kırmızı çizgisi
**var olmayan bir belgeye** dayanıyordu.

## Bu kapının işi

*"Yeni bir kimlik, dosyası olmadan merge edilemez."* Bir ADR kimliği yazmak ucuzdur;
onu **yazılı bir kararla karşılamak** pahalıdır. Kapı olmadan ucuz olan kazanır ve
kimlikler yeniden birikir.

## ⚠ Bu kapının YAKALAYAMADIĞI şey

Dosyanın **içeriğinin doğru** olduğunu ölçemez — dosyalar birer **rekonstrüksiyondur** ve
her biri bunu kendi başında ilan eder. Kapı *"belge var mı"* der, *"belge doğru mu"*
demez. Sınırın yazılması, olmayan bir garantiyi rozetlememek içindir.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

_KOK = Path(__file__).resolve().parents[1]
_ADR = _KOK / "docs/adr"

#: Kimlik deseni — `ADR-0007` ve `ADR-0007-K3` biçimlerinin **ikisini de** yakalar.
_DESEN = re.compile(r"ADR-(\d{4})")

#: Taranan ağaçlar. ⚠ `docs/adr`'nin **kendisi hariç**: ADR dosyaları birbirine atıf
#: yapar ve kendi atıflarını kanıt saymak, kapıyı **kendi kendini doğrulayan** bir şeye
#: çevirirdi (*"ölçüm aracının kendisi de bir bağımlılıktır"*).
_AGACLAR = ("app", "control_plane", "admin_app", "lab", "tests", "eval")


def _atiflar() -> dict[str, int]:
    sayim: dict[str, int] = {}
    for agac in _AGACLAR:
        d = _KOK / agac
        if not d.exists():
            continue
        for p in d.rglob("*.py"):
            for m in _DESEN.finditer(p.read_text(encoding="utf-8", errors="ignore")):
                sayim[m.group(1)] = sayim.get(m.group(1), 0) + 1
    for belge in ("MIMARI.md", "CLAUDE.md"):
        p = _KOK / belge
        if p.exists():
            for m in _DESEN.finditer(p.read_text(encoding="utf-8", errors="ignore")):
                sayim[m.group(1)] = sayim.get(m.group(1), 0) + 1
    return sayim


def _dosyalar() -> dict[str, Path]:
    return {p.name[:4]: p for p in _ADR.glob("[0-9][0-9][0-9][0-9]-*.md")}


def test_dizin_VAR():
    assert _ADR.is_dir(), (
        "🔴 `backend/docs/adr/` YOK. MIMARI §8.2'nin ölçtüğü boşluk buydu ve FAZ 4.6 onu "
        "kapattı; dizin silinirse `ADR-0007-K3`'e dayanan §C/3 çıkış ölçütü yine "
        "**var olmayan bir belgeye** dayanır.")


def test_KODDA_ANILAN_her_kimligin_DOSYASI_var():
    """🔴 Asıl kapı. *Yeni bir kimlik, dosyası olmadan merge edilemez.*"""
    eksik = sorted(k for k in _atiflar() if k not in _dosyalar())
    assert not eksik, (
        f"🔴 DOSYASIZ ADR KİMLİĞİ: {eksik}\n"
        f"Kodda anılan her kimliğin `docs/adr/NNNN-*.md` dosyası olmalı. Bir kimlik "
        f"yazmak ucuz, onu yazılı bir kararla karşılamak pahalıdır — kapı olmadan ucuz "
        f"olan kazanır.\nİki seçenek: (1) dosyayı yaz, (2) atfı kaldır. "
        f"'Sonra yazarım' bir seçenek DEĞİL.")


def test_HIC_KULLANILMAYAN_kimlige_dosya_YAZILMAZ():
    """⚠ Ters yön: `0001/0002/0006/0013` **hiç kullanılmadı** (MIMARI §8.2).

    Kullanılmayan bir kimliğe dosya yazmak, olmayan bir kararı **varmış gibi** kaydetmek
    olurdu — kapının kendisi bir kayıt uydurma aracına dönüşürdü.
    """
    fazla = sorted(k for k in _dosyalar() if k not in _atiflar())
    assert not fazla, (
        f"🔴 Kodda HİÇ anılmayan ADR dosyası: {fazla}. Bir karar kaydı, karşılığı olmayan "
        f"bir kimliği meşrulaştırmak için kullanılamaz.")


#: 🔴 **KÖKEN BEYANI — iki hâlden BİRİ, ikisi birden DEĞİL.**
#:
#: `0003…0024` **rekonstrüksiyondur** (karar alındığı gün yazılmamıştı, atıf
#: bağlamlarından türetildi). `0025+` ise kararla **aynı turda** yazıldı.
#:
#: ⚠ İkisini aynı damgayla işaretlemek **yanlış beyandır** ve iki yönü de vardır:
#: yeni bir kaydı *"rekonstrüksiyon"* demek onu **olduğundan zayıf**, eski bir kaydı
#: *"günü yazıldı"* demek **olduğundan güçlü** gösterirdi. *Bir kaydın değeri, ne
#: zaman yazıldığını doğru söylemesine bağlıdır.*
_KOKENLER = ("REKONSTRÜKSİYON", "GÜNÜ YAZILDI")


@pytest.mark.parametrize("num", sorted(_dosyalar()))
def test_her_dosya_KOKENINI_ILAN_eder(num):
    """🔴 *Var olmayan bir belgeye atıf yapmak bir eksiklikti; onu uydurulmuş bir tarihle
    doldurmak bir SAHTEKÂRLIK olurdu.*

    Her dosya (a) **kökenini** (rekonstrüksiyon ↔ günü yazıldı), (b) çelişkide **kodun
    kazandığını**, (c) **kanıt** işaretçisini taşımak zorunda.
    """
    metin = _dosyalar()[num].read_text(encoding="utf-8")
    ust = metin.upper()
    bulunan = [k for k in _KOKENLER if k in ust]
    assert bulunan, (
        f"ADR-{num}: dosya KÖKENİNİ ilan etmiyor ({' ya da '.join(_KOKENLER)}) — ne "
        f"zaman yazıldığı bilinmeyen bir karar kaydı, doğrulanamaz bir kayıttır.")
    assert len(bulunan) == 1, (
        f"ADR-{num}: dosya İKİ köken birden iddia ediyor ({bulunan}). Bir kayıt ya "
        f"sonradan türetilmiştir ya kararla birlikte yazılmıştır; ikisi birden olamaz.")
    assert "kod kazanır" in metin, (
        f"ADR-{num}: çelişkide kodun kazandığı yazılı değil — belge bir otorite gibi "
        f"okunabilir hâle gelmiş.")
    assert "## Kanıt" in metin, f"ADR-{num}: kanıt bölümü yok — doğrulanamaz bir kayıt."


def test_ESKI_kayitlar_REKONSTRUKSIYON_yeniler_DEGIL():
    """⚠ Köken **numaraya göre** doğrulanır: `0024` ve öncesi rekonstrüksiyon, `0025+`
    kararla aynı turda yazıldı. Bir gün biri eski bir dosyaya *"günü yazıldı"* yazarsa
    bu kapı kırmızı olur."""
    for num, yol in sorted(_dosyalar().items()):
        ust = yol.read_text(encoding="utf-8").upper()
        beklenen = "REKONSTRÜKSİYON" if int(num) <= 24 else "GÜNÜ YAZILDI"
        assert beklenen in ust, (
            f"ADR-{num}: köken beklenen ile uyuşmuyor (beklenen: {beklenen!r}). "
            f"0024 ve öncesi rekonstrüksiyondur; 0025+ kararla aynı turda yazıldı.")


def test_ADR_0007_K3_DOSYASI_C3_olcutunu_tasiyor():
    """🔴 v1'in **üçüncü çıkış ölçütü** bu dosyaya dayanıyor — boş olamaz."""
    p = _dosyalar().get("0007")
    assert p is not None, "🔴 ADR-0007 dosyası yok — §C/3 ölçütü dayanaksız kalır."
    metin = p.read_text(encoding="utf-8")
    assert "K3" in metin, "ADR-0007 dosyası K3 şartını taşımıyor"
    assert "CLARIFY" in metin or "netleştirme" in metin.lower(), (
        "ADR-0007-K3'ün içeriği (dönem eksikse SOR) dosyada yok")


def test_ADR_0008_disiplini_YAZILI():
    """En çok atıf alan karar (70): *refleksle yeni regex ekleme* disiplini yazılı olmalı."""
    metin = _dosyalar()["0008"].read_text(encoding="utf-8")
    assert "kök nedeni düzelt" in metin.lower(), (
        "ADR-0008'in disiplin cümlesi (*kök nedeni düzelt, örneği değil*) dosyada yok — "
        "oysa bu deponun en sık ihlal edilen kuralı odur.")
