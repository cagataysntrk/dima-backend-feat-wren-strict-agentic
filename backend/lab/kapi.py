"""KAPI — doğrulama maliyetini işin boyutuna göre ölçekler.

## 🔴 KULLANICI KARARI (2026-08-04): **YEREL KAPI = YALNIZ KORPUS**

*"Kapı testlerini iptal edelim, sadece korpus koşsun — o da sadece en gerekli
zamanlarda, sıklığı düşük, demet sonu gibi. Çok daha hızlı geliştirmeliyiz."*

Karar **ölçümle uyumlu** ve gerekçesi burada duruyor ki bir sonraki tur onu
*"unutulmuş"* sanmasın:

| Adım | Bu operasyonda kaç kez kırmızı verdi | Süre |
|---|---|---|
| `eval.run` | **0** — her koşumda `+0,0 / +0,0 / +0,0` | ~1,5 dk |
| konuşma senaryoları | **0** — dokuz sınıf tabanda sabit | ~1,5 dk |
| tam süit | birkaç kez — ama aynı kusurları **`--hizli` de yakaladı** | ~8,5 dk |
| **korpus** | 🔴 **1 kez — ve kimsenin göremeyeceği bir kusuru yakaladı** | **1 dk 57 sn** |

Korpusun o tek yakalaması, neden **onun kaldığının** tamamıdır: `gitas` bir compose
yarışıyla korpustan **tamamen düştü**, payda **445 → 342**'ye indi ve doğruluk
**%93,2 → %94,3'e ÇIKTI**. Yani sistem bozulurken **sayı iyileşti**. Süit yeşildi,
`eval` yeşildi, senaryolar yeşildi — çünkü hiçbiri *"kaç soru cevaplanabiliyor"*
sorusunu sormuyor. *Bir metriğin iyileşmesi, ölçülemeyenlerin denklemden çıkmasıyla
da olur.*

## Seviyeler

| Seviye | Ne koşar | Ne zaman | Süre |
|---|---|---|---|
| `--hizli` | değişen modüle **bağımlı** testler + çekirdek duman | geliştirme sırasında | **~30 sn – 2 dk** |
| `--tam` | **YALNIZ korpus** — *"kaç soru cevaplanabiliyor"* | **demet sonunda, bir kez** | **1 dk 50 sn** |
| `--hepsi` | korpus + süit + `eval` + senaryo | **gecelik CI** (geliştirme saatine mal olmaz) | **4 dk 06 sn** |

⚠ **Üç adım SİLİNMEDİ, yerel kapıdan ÇIKARILDI** (MIMARI §10: *"kapananlar işaretlenir,
silinmez"*). `--hepsi` ile hâlâ koşarlar ve **gecelik CI** onları koşmaya devam eder —
yani ağ hâlâ var, yalnız artık **geliştirmenin saatinden** ödenmiyor. Geri alma tek
bayrak: `--hepsi`.

## ⚡ PARALELLİK — kapsam kırpılmadan 7× (2026-08-04, ölçüldü)

Süreler yukarıda **düştü ama tek bir soru/test bile silinmedi**. Sebep basit ve utanç
vericiydi: kapı 20 çekirdekli makinede **tek çekirdeği %91'de** tutup 19'unu boş
bırakıyordu (167 MB / 38 GB kullanım). Darboğaz soru sayısı değil, **paralellik
yokluğuydu**.

| | önce | sonra | nasıl |
|---|---|---|---|
| korpus | 13 dk 18 sn | **1 dk 50 sn** | şirket × dilim → 16 süreç (`spawn`) |
| süit | ~8 dk 30 sn | **2 dk 15 sn** | `pytest -n 8` + worker başına izole proje ağacı |
| tam kapı | ~15 dk | **4 dk 06 sn** | iki dalga (aşağıda) |

🔴 **PAYDA BÖLÜNDÜ, KIRPILMADI.** Doğrulandı — paralel koşumun sayıları seri koşumla
**birebir aynı**: boyahane 5306 · atiksan 1462 · gulteks 1618 · gitas 2479 tur,
semantik vaka paydası **445**, toplam doğru-cube **%93,1**. KURAL A geçerli, donmuş
tabanlar kıyaslanabilir kaldı.

🔴 **SEYRELTME YASAK.** *"Korpus uzun sürüyorsa soruları azaltalım"* önerisi ölçülüp
**reddedildi**: paydayı kırpmak korpusun tek gerçek yakalamasını (`gitas` düştü, payda
445→342 indi, doğruluk **%93,2→%94,3 YÜKSELDİ**) görünmez kılardı — o sinyal tamamen
payda **sabitliğine** dayanır. Hız, kapsamdan değil **çekirdekten** satın alınır.

⚠ **"Dördünü aynı anda koş" YANLIŞTIR — denendi, KIRMIZI üretti.** Eş zamanlı koşumda
korpus (10 süreç) ile süit (8 worker) aynı anda compose yaptı, 20 çekirdek yetmedi,
derleme kilidi **60 sn zaman aşımına** uğradı → süit **934 hata**. Bu yüzden `--hepsi`
**iki dalga** koşar: önce korpus tek başına (tüm çekirdekler onun), sonra
süit ‖ eval ‖ senaryo. Aynı ölçüm iki dalgada: **0 hata, 2528 test geçti.**

Geri alma tek env: `DIMA_KORPUS_PARALEL=1` → eski seri davranış.

## ⚡ `--hizli` PARALEL KOŞAR (2026-08-05) — kapsamdan tek test gitmeden

Ölçüldü, `app/wren_service.py` değişimi (635 test seçiliyor):

| | süre |
|---|---|
| seri (eski) | **2 dk 51 sn** |
| `-n 8` | 1 dk 16 sn |
| **`-n 12`** | **1 dk 09 sn** |

Seçim büyüklüğüne göre bugünkü tablo:

| değişen dosya | seçilen | test | süre |
|---|---|---|---|
| `app/coldstart.py` | 5/192 | 245 | **33 sn** |
| `app/wren_service.py` | ~30/192 | 635 | **1 dk 09 sn** |
| `cube_router.py` + `routers/ask.py` | 51/192 | 991 | **2 dk 05 sn** |

🔴 **Aynı dosya kümesi, aynı testler — yalnız aynı anda.** Seri ve paralel koşum **635
test** ile birebir aynı sonucu verdi; hız boşta duran çekirdeklerden alındı.

⚠ **İşçi sayısı seçim büyüklüğüne bağlı** (`len(secili) // 2`, tavan 12): xdist işçi
başına oturum-kapsamlı fikstürleri (compose + Wren + login) **yeniden kurar**. Üç
dosyalık bir seçimde on iki işçi açmak, kurulum maliyetini testin kendisinden pahalı
yapardı — *paralelliğin bedeli, işin kendisinden büyükse paralellik bir yavaşlatmadır.*

⚠ **Kalan darboğaz yazılı:** en ağır seçimde (51 dosya) süre 2 dk 05 sn ve bunun büyük
kısmı **işçi başına compose**'dur (12 × ~5 sn). Onu kırmak, işçilerin derlenmiş ağacı
**paylaşması** demektir ve test izolasyonuna dokunur (`lab/izolasyon.py`'nin çözdüğü
compose yarışı geri gelebilir) — **ayrı bir iş**, ölçülmeden yapılmaz.

## `--hizli` bir KAPI DEĞİLDİR — bir SİNYALDİR

Seçim `import` bağımlılığına bakar; bir modülü **adıyla anmayan** ama davranışına
dayanan bir test kaçabilir. Bu yüzden araç her koşumda **kapsanmayan dosya sayısını
yazar** — bu deponun *"sessiz kırpma yok"* disiplini ölçüm aracının kendisine de
uygulanır (MIMARI §6.4: *"ölçüm aracının kendisi de bir bağımlılıktır"*).

## Kullanım

    # host'ta değişen dosyaları git verir, konteyner yalnız koşar
    python lab/kapi.py --hizli --degisen app/eylem.py tests/test_eylem_onayi.py
    python lab/kapi.py --tam        # demet sonu — korpus
    python lab/kapi.py --hepsi      # gecelik CI — dört adım
"""

from __future__ import annotations

import argparse
import os
import pathlib
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

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
    # ⚡ PARALEL (2026-08-04) — ölçüldü: `app/wren_service.py` değişiminde 635 test
    # **2 dk 51 sn** sürüyordu ve bu, demet kapısının kendisinden (korpus, 1 dk 47 sn)
    # PAHALIYDI. Süit adımı `-n 8`'i zaten kullanıyordu; hızlı sinyal SERİ kalmıştı.
    #
    # 🔴 KAPSAMDAN TEK TEST GİTMEDİ: aynı dosya kümesi, aynı testler — yalnız aynı anda.
    # Hız, boşta duran çekirdeklerden alındı (`lab/izolasyon.py` her worker'a kendi
    # derlenmiş ağacını verdiği için compose yarışı yapısal olarak yok).
    #
    # ⚠ İŞÇİ SAYISI DOSYA SAYISINA GÖRE: xdist işçi başına oturum-kapsamlı fikstürleri
    # (compose + Wren + login) YENİDEN kurar. Üç dosyalık bir seçimde sekiz işçi açmak,
    # kurulum maliyetini testin kendisinden pahalı yapardı — *paralelliğin bedeli, işin
    # kendisinden büyükse paralellik bir yavaşlatmadır.*
    isci = min(12, max(1, len(secili) // 2))
    paralel = ["-n", str(isci), "--dist", "loadfile"] if isci > 1 else []
    return _kos([sys.executable, "-m", "pytest", "-q", "-p", "no:warnings", *paralel,
                 *[f"tests/{s}" for s in secili]], "pytest (seçili)")


#: Tüm adımlar — anahtar, `--sadece` ile seçmek için. **Sıra anlamlıdır:** korpus
#: BAŞTA, çünkü yerel kapının tek adımı odur ve `--hepsi`'de de önce o konuşmalıdır.
ADIM_ANAHTARLARI = ("korpus", "suit", "eval", "senaryo")

#: 🔴 **YEREL DEMET KAPISI = YALNIZ KORPUS** (kullanıcı kararı, 2026-08-04).
#: Öteki üç adım **silinmedi**, yerel kapıdan **çıkarıldı**: `--hepsi` ve gecelik CI
#: onları koşmaya devam eder. Gerekçe ve ölçüm modül belgesinde.
YEREL_KAPI = ("korpus",)


def tam(sadece: tuple[str, ...] = (), *, hepsi: bool = False) -> int:
    """Demet kapısı. **Varsayılan: yalnız korpus.** `hepsi=True` → dört adım (CI).

    `sadece` verilirse **yalnız o adımlar** koşar.

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
        ([sys.executable, "lab/nl_corpus.py", "--kapi"], "korpus kapısı"),
        # ⚡ `-n 8`: süit 8 dk 30 sn → 2 dk 15 sn (ölçüldü, 2499 test, SIFIR yeni kırmızı).
        # İzolasyon `tests/conftest.py`'de: her worker kendi derlenmiş proje ağacına yazar.
        ([sys.executable, "-m", "pytest", "-q", "-p", "no:warnings", "-n", "8"], "tam süit"),
        ([sys.executable, "-m", "eval.run"], "eval.run"),
        # 🔴 `--kapi` ZORUNLU: bayraksız koşumda `main()` her yolda 0 döner ve bu adım
        # **hiçbir koşulda kırmızı veremez** (ölçüldü: `returncode == 0`, senaryo tümden
        # çökse bile). Dört bileşenli bir kapının dörtte biri sessizce **dekordu**.
        ([sys.executable, "lab/konusma_senaryolari.py", "--kapi"], "konuşma senaryoları"),
    )
    # 🔴 Yerel kapı **daraltılmış**: `--sadece` verilmediyse ve `--hepsi` denmediyse
    # YALNIZ korpus koşar. Bu bir kırpma DEĞİL, ilan edilmiş bir kapsam — ve aşağıda
    # **yazılır**: sessizce atlanan bir adım, atlanmamış gibi okunur.
    if not sadece and not hepsi:
        sadece = YEREL_KAPI
        print("▶ YEREL DEMET KAPISI — yalnız KORPUS (kullanıcı kararı 2026-08-04).\n"
              "  Süit · eval · senaryo SİLİNMEDİ: `--hepsi` ve gecelik CI onları koşar.\n"
              "  Geliştirme sırasındaki kontrol: `--hizli --degisen <dosyalar>`.\n")
        adimlar = tuple(k for k, ad in zip(adimlar, ADIM_ANAHTARLARI, strict=True)
                        if ad in YEREL_KAPI)
        sadece = ()
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
    # ⚡ Adımlar BİRBİRİNDEN bağımsız (ayrı süreç, ayrı proje ağacı) → aynı anda koşarlar.
    # Sıralı koşumda toplam = adımların TOPLAMI; paralelde = EN UZUNU. Dört adım için
    # 7 dk 05 sn yerine ~2 dk 20 sn. Tek adım varsa havuz kurmaya değmez.
    # ⚡ İKİ DALGA — hepsi birden DEĞİL.
    #
    # Dört adımı aynı anda koşmak denendi ve ÖLÇÜLDÜ: korpus (10 süreç) ile süit
    # (8 worker) eş zamanlı compose yapınca 20 çekirdek yetmedi, derleme kilidi
    # 60 sn zaman aşımına uğradı ve süit **934 hata** verdi. Yani "hepsini paralel
    # koş" saf hızlanma değil, aşırı abone olunca KIRMIZI ÜRETİR.
    #
    # Dalga 1: korpus TEK BAŞINA (tüm çekirdekler onun; 1 dk 50 sn)
    # Dalga 2: süit ‖ eval ‖ senaryo (süit 8 worker; ötekiler tek çekirdek, 2 dk 20 sn)
    # Toplam ~4 dk 10 sn — sıralı 15 dk yerine. Yerel kapı zaten yalnız dalga 1'dir.
    _AGIR_ADIM = "korpus kapısı"
    dalga1 = [a for a in adimlar if a[1] == _AGIR_ADIM]
    dalga2 = [a for a in adimlar if a[1] != _AGIR_ADIM]
    sonuclar_map: dict[str, tuple[int, str]] = {}
    for dalga in (dalga1, dalga2):
        if not dalga:
            continue
        if len(dalga) == 1:
            komut, baslik = dalga[0]
            sonuclar_map[baslik] = _kos_yakala(komut, baslik)
        else:
            with ThreadPoolExecutor(max_workers=len(dalga)) as havuz:
                for (_k, baslik), sonuc in zip(
                        dalga, havuz.map(lambda a: _kos_yakala(a[0], a[1]), dalga),
                        strict=True):
                    sonuclar_map[baslik] = sonuc
    sonuclar = [sonuclar_map[baslik] for _komut, baslik in adimlar]
    for (rc, cikti), (_komut, baslik) in zip(sonuclar, adimlar, strict=True):
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
    elif hepsi:
        print("\n" + ("✓ TAM KAPI (dört adım) YEŞİL" if kotu == 0
                      else "✗ TAM KAPI (dört adım) KIRMIZI"))
    else:
        print("\n" + ("✓ DEMET KAPISI (korpus) YEŞİL" if kotu == 0
                      else "✗ DEMET KAPISI (korpus) KIRMIZI"))
    return kotu


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hizli", action="store_true")
    ap.add_argument("--tam", action="store_true",
                    help="DEMET KAPISI — yalnız korpus (ölçüldü: 1 dk 57 sn, paralel)")
    ap.add_argument("--hepsi", action="store_true",
                    help="korpus + süit + eval + senaryo (~15 dk) — GECELİK CI içindir, "
                         "yerel geliştirmede koşulmaz")
    ap.add_argument("--sadece", nargs="+", default=[], metavar="ADIM",
                    help="kırmızı doğrulaması: YALNIZ bu adımlar koşar "
                         f"({' | '.join(ADIM_ANAHTARLARI)}). Demet kapısı DEĞİLDİR.")
    ap.add_argument("--degisen", nargs="*", default=[],
                    help="değişen dosya yolları (host'ta `git status` verir)")
    a = ap.parse_args()
    if a.tam or a.hepsi:
        return tam(tuple(a.sadece), hepsi=a.hepsi)
    if a.hizli:
        return hizli(a.degisen)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
