"""KAPI — doğrulama maliyetini işin boyutuna göre ölçekler.

## Neden bu araç var

Tam süit + `eval` + korpus + senaryo ≈ **15 dakika**. Bu bir faz kapısı olarak doğru,
ama her düzenlemeden sonra koşturulunca geliştirmenin kendisini yavaşlatıyor (ölçüldü:
bir fazda üç kez koşturuldu → 45 dakika, ve üçünün ikisi hiçbir şey bulmadı).

Çözüm **daha az doğrulama** değil, **doğru zamanda doğru doğrulama**:

| Seviye | Ne koşar | Ne zaman |
|---|---|---|
| `--hizli` | değişen modüle **bağımlı** test dosyaları + çekirdek duman | geliştirme sırasında |
| `--tam` | süit + `eval` + korpus + senaryo | **faz sonunda, bir kez** |

## `--hizli` bir KAPI DEĞİLDİR — bir SİNYALDİR

Seçim `import` bağımlılığına bakar; bir modülü **adıyla anmayan** ama davranışına
dayanan bir test kaçabilir. Bu yüzden araç her koşumda **kapsanmayan dosya sayısını
yazar** — bu deponun *"sessiz kırpma yok"* disiplini ölçüm aracının kendisine de
uygulanır (MIMARI §6.4: *"ölçüm aracının kendisi de bir bağımlılıktır"*).

Yalnız `--tam` bir kapıdır. Commit öncesi o koşar.

## Kullanım

    # host'ta değişen dosyaları git verir, konteyner yalnız koşar
    python lab/kapi.py --hizli --degisen app/eylem.py tests/test_eylem_onayi.py
    python lab/kapi.py --tam
"""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

KOK = pathlib.Path(__file__).resolve().parents[1]
TESTLER = KOK / "tests"

#: ÇEKİRDEK DUMAN — değişiklik neye dokunursa dokunsun koşan, ucuz ve geniş kapsamlı
#: dosyalar. Merdivenin her basamağından en az bir tanık: deterministik route, takip
#: yolu, mühür/gizlilik, cevap alanlarının yetim olmaması.
CEKIRDEK = (
    "test_cube_router.py",              # deterministik basamak
    "test_ask_golden.py",               # uçtan uca altın yol
    "test_takip_ucuncu_sinif.py",       # takip/konuşma yolu
    "test_cevap_alani_yetim_degil.py",  # cevap alanlarının tüketicisi var mı
)


def _desenler(degisen: list[str]) -> list[re.Pattern[str]]:
    """Değişen kaynak dosya → o modüle BAĞIMLILIĞI gösteren desenler.

    ## Neden sade ad ARANMAZ (ölçüldü, 3 Ağustos 2026)

    İlk sürüm `\bask\b` gibi sade modül adlarını da arıyordu. Sonuç: `app/routers/ask.py`
    değişince **67/137 dosya** seçildi (3,4 dk) — çünkü `ask` aynı zamanda
    `tests/conftest.py`'nin **yardımcı fonksiyonudur** ve neredeyse her testte geçer.
    Yani sinyal bağımlılık değil, **ad çakışmasıydı**.

    Artık yalnız **import-biçimli** eşleşme sayılır (`app.routers.ask`,
    `from app.routers import ask`, `from app import ask`). Bir modülü import etmeden
    yalnız HTTP ucundan tüketen test kaçabilir — bu bilinçli: `--hizli` bir kapı değil
    sinyaldir ve kapsanmayanı sayısıyla yazar.
    """
    desenler: list[re.Pattern[str]] = []
    for d in degisen:
        yol = pathlib.PurePosixPath(d)
        if yol.suffix != ".py" or yol.name == "__init__.py":
            continue
        parcalar = [x for x in yol.parts if x not in ("backend", ".")]
        if not parcalar or parcalar[0] not in ("app", "control_plane", "lab"):
            continue
        paket, stem = ".".join(parcalar[:-1]), yol.stem
        nokta = re.escape(f"{paket}.{stem}")
        desenler.append(re.compile(
            rf"{nokta}\b"                                        # app.routers.ask...
            rf"|from\s+{re.escape(paket)}\s+import\s+[^\n]*\b{re.escape(stem)}\b"
            rf"|import\s+{nokta}\b"))
    return desenler


def _secim(degisen: list[str]) -> tuple[list[str], int]:
    hepsi = sorted(f.name for f in TESTLER.glob("test_*.py"))
    secili = {f for f in CEKIRDEK if (TESTLER / f).exists()}
    # Değişen test dosyaları HER ZAMAN koşar (yeni yazdığım kapı en olası kırılan yer).
    for d in degisen:
        ad = pathlib.PurePosixPath(d).name
        if ad.startswith("test_") and (TESTLER / ad).exists():
            secili.add(ad)
    desenler = _desenler(degisen)
    if desenler:
        for ad in hepsi:
            metin = (TESTLER / ad).read_text(encoding="utf-8", errors="ignore")
            if any(dsn.search(metin) for dsn in desenler):
                secili.add(ad)
    return sorted(secili), len(hepsi)


def _kos(komut: list[str], baslik: str) -> int:
    print(f"\n{'=' * 78}\n▶ {baslik}\n{'=' * 78}", flush=True)
    return subprocess.call(komut, cwd=KOK)


#: Özete girecek satırın seçiciler — her aracın "sonuç" satırı farklı biçimde.
_OZET_ISARET = ("passed", "failed", "error", "baseline'a göre", "TOPLAM doğru-cube",
                "ÖLÇÜLEMEDİ", "sınıf ")


def _son_anlamli(cikti: str) -> str:
    """Bir aracın çıktısından ÖZETE girecek satır(lar). Bulunamazsa son dolu satır —
    sessizce boş bırakmaktan iyidir (boş özet 'ölçüm yok'u 'sorun yok' gibi gösterir)."""
    satirlar = [s.strip() for s in cikti.splitlines() if s.strip()]
    isaretli = [s for s in satirlar if any(i in s for i in _OZET_ISARET)]
    return (isaretli[-1] if isaretli else (satirlar[-1] if satirlar else "(çıktı yok)"))[:120]


def _dusenler(cikti: str) -> list[str]:
    """DÜŞEN test adları. Özette olmazsa *"kırmızı"* bilgisi tek başına işe yaramaz:
    kapı çıktısı `tail` ile okunur, ayrıntı kırpılır ve hangi testin düştüğünü bulmak
    için süiti YENİDEN koşmak gerekir (bu turda iki kez oldu — 8'er dakika)."""
    return [s.strip()[:110] for s in cikti.splitlines() if s.strip().startswith("FAILED")]


def _kos_yakala(komut: list[str], baslik: str) -> tuple[int, str]:
    """`_kos` gibi ama çıktıyı da döndürür — hem canlı basar hem özet için saklar."""
    print(f"\n{'=' * 78}\n▶ {baslik}\n{'=' * 78}", flush=True)
    p = subprocess.Popen(komut, cwd=KOK, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True, bufsize=1)
    parcalar: list[str] = []
    assert p.stdout is not None
    for satir in p.stdout:
        print(satir, end="", flush=True)
        parcalar.append(satir)
    return p.wait(), "".join(parcalar)


def hizli(degisen: list[str]) -> int:
    secili, toplam = _secim(degisen)
    atlanan = toplam - len(secili)
    print(f"HIZLI KAPI · değişen={len(degisen)} → seçilen test dosyası "
          f"{len(secili)}/{toplam}")
    for s in secili:
        print(f"  · {s}")
    print(f"\n⚠ KAPSANMADI: {atlanan} test dosyası. Bu bir KAPI DEĞİL, bir SİNYALDİR — "
          f"seçim import bağımlılığına bakar, davranışa değil.\n"
          f"  Kapı: python lab/kapi.py --tam   (faz sonunda, commit'ten önce)")
    if not secili:
        return 0
    return _kos([sys.executable, "-m", "pytest", "-q", "-p", "no:warnings",
                 *[f"tests/{s}" for s in secili]], "pytest (seçili)")


#: `--tam`'ın adımları — anahtar, `--sadece` ile seçmek için.
ADIM_ANAHTARLARI = ("suit", "eval", "korpus", "senaryo")


def tam(sadece: tuple[str, ...] = ()) -> int:
    """Dört kapı adımı. `sadece` verilirse **yalnız o adımlar** koşar.

    🔴 **KIRMIZI DOĞRULAMASI TÜM KAPIYI TEKRAR KOŞMAZ.** Kullanıcı kararı (2026-08-04):
    *"demette kapı kırmızı verince neden sadece kırmızı veren kısım tekrar çalışmıyor?"*
    — haklı: dört adımın biri kırmızıysa diğer üçü **zaten yeşil ölçüldü** ve kod o
    aşamalardan sonra değişmediyse tekrar koşmaları **saf israftır** (~13 dk).

    Doğru döngü:
    ```
    python lab/kapi.py --tam                  # demet kapısı (dört adım)
    #  ✗ korpus kapısı  →  düzelt  →
    python lab/kapi.py --tam --sadece korpus  # YALNIZ kırmızı olan
    ```
    ⚠ **Sınır:** düzeltme **başka bir adımı besleyen** bir dosyaya dokunduysa
    (`OPERASYON.md §3` risk listesi) kısmi koşum yetmez — tüm kapı tekrar koşar.
    Bu ayrımı araç bilemez, **koşan kişi beyan eder**.
    """
    adimlar = (
        ([sys.executable, "-m", "pytest", "-q", "-p", "no:warnings"], "tam süit"),
        ([sys.executable, "-m", "eval.run"], "eval.run"),
        ([sys.executable, "lab/nl_corpus.py", "--kapi"], "korpus kapısı"),
        # 🔴 `--kapi` ZORUNLU: bayraksız koşumda `main()` her yolda 0 döner ve bu adım
        # **hiçbir koşulda kırmızı veremez** (ölçüldü: `returncode == 0`, senaryo tümden
        # çökse bile). Dört bileşenli bir kapının dörtte biri sessizce **dekordu**.
        ([sys.executable, "lab/konusma_senaryolari.py", "--kapi"], "konuşma senaryoları"),
    )
    if sadece:
        gecersiz = [a for a in sadece if a not in ADIM_ANAHTARLARI]
        if gecersiz:
            print(f"🔴 bilinmeyen adım: {gecersiz} — geçerli: {list(ADIM_ANAHTARLARI)}")
            return 2
        secili = [(k, b) for (k, b), anahtar in zip(adimlar, ADIM_ANAHTARLARI, strict=True)
                  if anahtar in sadece]
        atlanan = [a for a in ADIM_ANAHTARLARI if a not in sadece]
        print(f"⚠ KISMİ KOŞUM — yalnız: {list(sadece)} · ATLANAN: {atlanan}\n"
              "  Bu bir DEMET KAPISI DEĞİL, bir kırmızı doğrulamasıdır. Atlanan adımlar\n"
              "  son tam koşumdaki sonuçlarını korur; düzeltme onları besleyen bir dosyaya\n"
              "  dokunduysa TÜM kapı tekrar koşmalıdır (sessiz kırpma yok).\n")
        adimlar = tuple(secili)

    kotu = 0
    ozet: list[str] = []
    for komut, baslik in adimlar:
        rc, cikti = _kos_yakala(komut, baslik)
        ozet.append(f"  {'✓' if rc == 0 else '✗'} {baslik:22} {_son_anlamli(cikti)}")
        ozet.extend(f"      ↳ {ad}" for ad in _dusenler(cikti)[:12])
        if rc != 0:
            kotu = rc
    # ÖZET EN SONDA ve TEK BLOK: kapı çıktısı çoğu zaman `tail` ile okunur; sayılar
    # ortada kalırsa kırpılır ve *"yeşil mi?"* sorusu cevaplanır ama *"kaç test, kaç
    # yüzde?"* cevapsız kalır (bu turda tam olarak bu oldu — ölçüm kaydı kayboldu).
    print("\n" + "=" * 78)
    print("FAZ KAPISI ÖZETİ")
    print("=" * 78)
    print("\n".join(ozet))
    if sadece:
        print("\n" + ("✓ KISMİ KOŞUM YEŞİL — ama bu bir DEMET KAPISI DEĞİL"
                      if kotu == 0 else "✗ KISMİ KOŞUM KIRMIZI"))
    else:
        print("\n" + ("✓ FAZ KAPISI YEŞİL" if kotu == 0 else "✗ FAZ KAPISI KIRMIZI"))
    return kotu


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hizli", action="store_true")
    ap.add_argument("--tam", action="store_true")
    ap.add_argument("--sadece", nargs="+", default=[], metavar="ADIM",
                    help="kırmızı doğrulaması: YALNIZ bu adımlar koşar "
                         f"({' | '.join(ADIM_ANAHTARLARI)}). Demet kapısı DEĞİLDİR.")
    ap.add_argument("--degisen", nargs="*", default=[],
                    help="değişen dosya yolları (host'ta `git status` verir)")
    a = ap.parse_args()
    if a.tam:
        return tam(tuple(a.sadece))
    if a.hizli:
        return hizli(a.degisen)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
