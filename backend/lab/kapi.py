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
| `--tam` | **İKİ KORPUS** — kataloğun sözlüğü *ve* kullanıcının sözlüğü | **demet sonunda, bir kez** | **~3 dk** |
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
    python lab/kapi.py --tam        # demet sonu — iki korpus (katalog + gerçek-dünya)
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
    # 🔴 BÜYÜME TAVANLARI — **her koşumda**, ne değişirse değişsin (eklendi 2026-08-06).
    #
    # Ölçülen kusur: `test_frontend_buyume` **üç commit boyunca kırmızıydı** ve hızlı kapı
    # her seferinde YEŞİL dedi. Sebep bir kod kusuru değil bir **seçim** kusuruydu:
    # `--degisen` ELLE verilen bir listedir ve o demette `ReportCard.tsx` listeye
    # YAZILMAMIŞTI → `_frontend_degisti()` `False` döndü → frontend kapıları hiç seçilmedi.
    #
    # ⚠ Ve bu, `_frontend_degisti`nin kendi docstring'indeki dersin **ikinci hâlidir**:
    # orada kapsam *uzantı süzgecinden* dardı, burada *girdi listesinden*. İkisi de aynı
    # cümleye çıkıyor: **bir kapının kapsamı, onu tetikleyen sinyalden büyük olamaz.**
    #
    # 🔴 Çözüm neden ÇEKİRDEK: bir tavanı **her değişiklik** aşabilir; import bağımlılığına
    # bakan bir seçim onu asla güvenilir şekilde bulamaz (tavan bir *dosya boyutudur*, bir
    # *çağrı grafiği* değil). Ve maliyeti ölçüldü: ikisi birlikte **~5 sn** — çekirdeğin
    # geri kalanının yanında bedava.
    "test_modul_buyume.py",             # ask()/cube_router tavanları
    "test_frontend_buyume.py",          # ReportCard/types tavanları
)


#: Frontend kaynak uzantıları. ⚠ `.css` **dahil**: FAZ 7.2'nin tasarım sistemi kapısı
#: `globals.css`'i okuyor ve bir token silinmesi yalnız oradan görünür.
_FE_UZANTI = (".ts", ".tsx", ".css")

#: Frontend'i okuyan kapıların **tek ortak imzası**: hepsi `tests/kapi_ortak`'ın
#: yardımcılarını (`fe_dosyalari` · `fe_kaynak` · `frontend_dir`) ya da doğrudan frontend
#: dizin adını kullanır. *Bir kuralı bir listeye değil bir İMZAYA bağlamak, listeyi
#: bayatlamaktan kurtarır.*
_FE_OKUYAN = re.compile(r"fe_dosyalari|fe_kaynak|frontend_dir|dima-frontend-demo-master")


def _frontend_degisti(degisen: list[str]) -> bool:
    """🔴 **Ölçülmüş bir kör nokta** (2026-08-05).

    `_desenler` yalnız `.py` dosyalarına bakıyordu; bir `.tsx` değişikliği **hiçbir**
    kapı seçmiyordu. Sonuç: FAZ 7.8'de `ReportCard.tsx`'ten taşınan bir alan yüzünden
    `test_ai_act_uyumu` kırmızıya döndü ve **dört demet boyunca görünmedi** — hızlı
    kapı her seferinde yeşil dedi.

    *Bir kapının kapsamı, onu tetikleyen sinyalden büyük olamaz.*

    ⚠ Frontend'i okuyan kapılar **modül bağımlılığıyla** seçilemez: onlar bir Python
    modülünü import etmez, bir **dosya ağacını okur**. Bu yüzden ayrı ve adı olan bir
    kural — ve `--hizli`'nin sade-ad tuzağına düşmemek için desen `kapi_ortak`'ın
    yardımcı **adlarına** bağlı, `"frontend"` gibi bir kelimeye değil.
    """
    return any(pathlib.PurePosixPath(d).suffix in _FE_UZANTI for d in degisen)


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


def _yol_desenleri(degisen: list[str]) -> list[re.Pattern[str]]:
    """Değişen dosyanın **YOLUNU dize olarak** okuyan kapılar.

    🔴 **İkinci kör nokta, birincisiyle aynı sınıf** (2026-08-05). `_desenler()` yalnız
    **import** biçimli bağımlılığı sayıyor. Ama bazı kapılar modülü import etmez, dosyayı
    **okur**: `ast.parse((KOK / "app" / "routers" / "ask.py").read_text())`. O kapılar
    `ask.py` değişse bile **hiç seçilmiyordu**.

    Ölçülen bedel: `_queue_discovery_job` `discovery_kuyrugu.py`'ye taşındı ve
    `test_ai_act_uyumu::test_KOSUCU_IPTALI_GERCEKTEN_OKUYOR` kırmızıya döndü; o turun
    hızlı kapısı **517 yeşil** dedi ve kırmızı ancak bir sonraki turda görüldü.

    *Bir kapının kapsamı, onu tetikleyen sinyalden büyük olamaz* — ve bir kaynak dosyayı
    okumak da bir bağımlılıktır, import kadar gerçek.

    ⚠ **Ölçüt TIRNAK İÇİNDEKİ DOSYA ADIDIR**, tam yol değil — ve bu bir daraltma değil,
    bir **genelleme**: bu depoda yol üç ayrı biçimde kuruluyor
    (`"app/routers/ask.py"` · `KOK / "app" / "routers" / "ask.py"` · `APP / "ask.py"`).
    Üçünün **tek ortak noktası** tırnak içindeki dosya adıdır.

    ⚠ Yanlış-pozitif riski kabul edildi ve ölçüldü: bir docstring'de geçen `"ask.py"`
    de seçim üretir. *Fazladan koşan bir kapı zaman kaybettirir; koşmayan bir kapı
    kırmızıyı gizler* — ve ikincisi bu operasyonda **iki kez** oldu.
    """
    desenler: list[re.Pattern[str]] = []
    for d in degisen:
        yol = pathlib.PurePosixPath(d)
        if yol.suffix != ".py" or yol.name == "__init__.py":
            continue
        desenler.append(re.compile(f'"{re.escape(yol.name)}"'))
    return desenler


#: 🔴 UÇTAN-TÜKETİLEN BAĞIMLILIKLAR — import grafiğinin GÖREMEDİĞİ kenarlar.
#:
#: `_desenler` yalnız **import-biçimli** eşleşme sayar ve kendi belgesi bunu bilinçli bir
#: sınır olarak yazar: *"bir modülü import etmeden yalnız HTTP ucundan tüketen test
#: kaçabilir."* Sınır doğruydu (sade ad araması 67/137 dosya seçiyordu) ama bedeli bu
#: turda **üçüncü kez** ödendi:
#:
#:     `app/llm.py` değişti  →  `test_yol_siniri` SEÇİLMEDİ  →  kırmızı iki demet gizlendi
#:
#: O test `llm.py`'yi hiç import etmez; `ask(client, …)` ile **uçtan** tüketir. Ve tam da
#: `llm.py`'nin uydurma-SQL dalına dayanıyordu.
#:
#: ⚠ Çözüm import grafiğini genişletmek DEĞİL (ölçüldü, reddedildi) — **adı olan, sayılı
#: ve gerekçeli** bir kenar listesi. *Bir grafiğin göremediği kenarı elle çizmek, grafiği
#: bulanıklaştırmaktan iyidir.*
UCTAN_TUKETILEN: dict[str, tuple[str, ...]] = {
    # Sağlayıcı sınırı: cevaplama merdiveninin EN ALT basamağı. Onu import eden test
    # neredeyse yok; onu HTTP ucundan ölçen test çok.
    "app/llm.py": ("test_yol_siniri.py", "test_uydurma_sayi_yok.py",
                   "test_discovery_dogrulama.py"),
}


def _uctan(degisen: list[str]) -> set[str]:
    """Import grafiğinin göremediği kenarlardan gelen test dosyaları."""
    out: set[str] = set()
    for d in degisen:
        anahtar = str(pathlib.PurePosixPath(d)).removeprefix("backend/")
        out |= set(UCTAN_TUKETILEN.get(anahtar, ()))
    return {a for a in out if (TESTLER / a).exists()}


def _secim(degisen: list[str]) -> tuple[list[str], int]:
    hepsi = sorted(f.name for f in TESTLER.glob("test_*.py"))
    secili = {f for f in CEKIRDEK if (TESTLER / f).exists()}
    # Değişen test dosyaları HER ZAMAN koşar (yeni yazdığım kapı en olası kırılan yer).
    for d in degisen:
        ad = pathlib.PurePosixPath(d).name
        if ad.startswith("test_") and (TESTLER / ad).exists():
            secili.add(ad)
    secili |= _uctan(degisen)
    desenler = _desenler(degisen) + _yol_desenleri(degisen)
    fe = _frontend_degisti(degisen)
    if desenler or fe:
        for ad in hepsi:
            metin = (TESTLER / ad).read_text(encoding="utf-8", errors="ignore")
            if desenler and any(dsn.search(metin) for dsn in desenler):
                secili.add(ad)
            elif fe and _FE_OKUYAN.search(metin):
                secili.add(ad)
    return sorted(secili), len(hepsi)


def _kos(komut: list[str], baslik: str) -> int:
    print(f"\n{'=' * 78}\n▶ {baslik}\n{'=' * 78}", flush=True)
    return subprocess.call(komut, cwd=KOK)


#: Özete girecek satırın seçiciler — her aracın "sonuç" satırı farklı biçimde.
#: ⟳ `§A2`/`§A3` (rapor `§14`) — **`cevapsız` ve `semantik vaka` de manşete girer.**
#: Öncesinde özet yalnız *«doğru-cube %»*i taşıyordu ve o oran **SQL üretebilmiş**
#: turların içindedir; cevapsız kalanlar paydanın **dışındadır**. Yani kapı, ürünün en
#: görünür kusurunu **tanım gereği** göremiyordu (ölçüldü: korpus %19,9 · canlı %21,8).
#: ⚠ `_son_anlamli` **son** işaretli satırı seçtiği için sıra önemlidir: `nl_corpus`
#: bu üç satırı doğru-cube → cevapsız → semantik vaka sırasıyla basar ve özete
#: sonuncusu değil **hepsi** girsin diye `_ozet_satirlari` çoğul döner.
_OZET_ISARET = ("passed", "failed", "error", "baseline'a göre", "TOPLAM doğru-cube",
                "ÖLÇÜLEMEDİ", "sınıf ", "cevapsız:", "semantik vaka:")


def _son_anlamli(cikti: str) -> str:
    """Bir aracın çıktısından ÖZETE girecek satır(lar). Bulunamazsa son dolu satır —
    sessizce boş bırakmaktan iyidir (boş özet 'ölçüm yok'u 'sorun yok' gibi gösterir)."""
    satirlar = [s.strip() for s in cikti.splitlines() if s.strip()]
    isaretli = [s for s in satirlar if any(i in s for i in _OZET_ISARET)]
    if not isaretli:
        return (satirlar[-1] if satirlar else "(çıktı yok)")[:120]
    # ⟳ `§A2` — **korpus manşeti artık ÜÇ satır.** Son işaretli satırı almak, cevapsız
    # ve semantik payda satırlarını düşürürdü; ölçüm eklendiği hâlde görünmezdi.
    # ⚠ Öteki adımlar (süit, eval) tek satır basar → davranışları değişmez.
    _korpus = [s for s in isaretli
               if any(i in s for i in ("TOPLAM doğru-cube", "cevapsız:", "semantik vaka:"))]
    if len(_korpus) > 1:
        return "\n" + "\n".join(f"      {s[:118]}" for s in _korpus)
    return isaretli[-1][:120]


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
    # ⚠ Bildirim **burada da** çağrılır: `--hizli` kendi çıkışını kullanıyor ve ilk
    # yazımda yalnız `--tam` özetine bağlıydı. Ölçüldü: hızlı koşumda **34 test
    # atlanıyordu** ve özet yine yeşildi. *İki çıkışı olan bir koşucuda, tek çıkışa
    # konan bir bildirim yarım bir bildirimdir.*
    _belgeler_bildirimi()
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
ADIM_ANAHTARLARI = ("korpus", "gercek", "suit", "eval", "senaryo", "garson_korpusu",
                    "garson", "eval_llm")

#: 🔴 **`garson` (CANLI KOŞUCU) HİÇBİR TOPLU KOŞUMDA YOK — ne yerelde ne `--hepsi`'de.**
#:
#: ⟳ **BAŞLIK DÜZELTİLDİ (2026-08-12) — ve düzeltmenin sebebi bir MİRAS kusuruydu.**
#: Bu blok *«garson»* diyordu ve okuyan bunu **garson basamağının tamamı** sanıyordu.
#: Oysa ölçüldü: `lab/garson_korpusu.py` **kasetli** koşuyor (`--network none`,
#: `36 isabet · 0 ıska`) ve aşağıdaki gerekçenin **hiçbir maddesi** ona uymuyor —
#: kota istemiyor, ağ istemiyor, belirlenimsiz değil. O adım artık `--hepsi`'de.
#: *Bir sınıfın ilk üyesi için yazılmış gerekçe, ikinci üyeye sessizce miras kalır.*
#:
#: Sebebi bir tercih değil, bir **tabiat farkı** (yol haritası §12.2b): öteki beş adım
#: **belirlenimlidir** ve LLM'siz koşar; `garson` ise `--live` ister, kotaya bağlıdır ve
#: **belirlenimsizdir**. Onu `--hepsi`'ye koymak iki şeyi birden bozardı: gecelik CI
#: kotaya çarpar, ve *"kapı yeşil"* cümlesi belirlenimsiz bir ölçüme dayanır.
#:
#: ⚠ Ve **KURAL G-1**: bu adım tek koşumla karar vermez — en az iki koşum, ayrışırsa `⊘`.
#: Bu yüzden bir *kapı adımı* değil, bir **faz-sonu ölçümüdür**:
#:
#:     python lab/kapi.py --tam --sadece garson     # açıkça istenirse
#:     python lab/garson.py --live --muhur k1       # asıl kullanım
GARSON_TOPLUDA_YOK = "garson"

#: 🔴 **TOPLU KOŞUMA GİRMEYEN ADIMLAR — bir KÜME, tek bir ad değil** (2026-08-09).
#:
#: ## Ölçülen kusur: adımın belgesi *"girmez"* diyordu, kod onu KOŞUYORDU
#:
#: Süzgeç tek elemanlı bir **dizeye** (`GARSON_TOPLUDA_YOK`) bağlıydı ve `--hepsi` yalnız
#: onu eliyordu. Ama `eval_llm`'in kendi docstring'i (aşağıda, `adimlar` içinde) şunu
#: yazıyor:
#:
#: > *"Toplu koşuma girmez ve sebebi `garson` ile aynı: gerçek sağlayıcı + anahtar ister,
#: > `--hepsi` ise `--network none` ile koşar. Yeri **faz sonu**dur."*
#:
#: Canlı kütükte (`dima-kapi-z`, 2026-08-09 03:29:38) **`▶ eval LLM dilimi` koşuyordu** —
#: ağ + kota isteyen, **belirlenimsiz** bir adım `--hepsi`'nin içindeydi ve *"tam kapı
#: yeşil"* cümlesi belirlenimsiz bir ölçüme dayanıyordu.
#:
#: 🔴 Bu, bu dosyanın **kendi dersinin üçüncü tekrarıdır**: `konusma_senaryolari`
#: bayraksız koşumda hiç kırmızı veremiyordu (*"dörtte biri sessizce dekordu"*),
#: `gercek_dunya` aynı tuzağa düşmesin diye `--kapi` zorunlu kılındı — ve `eval_llm`
#: belgesinin tersini yapıyordu. *Bir kuralı tek elemanlı bir dizeye yazmak, ikinci
#: üyeyi eklemeyi unutturur; kümeye yazmak unutturmaz.*
#:
#: ⚠ İkisi de **SİLİNMEDİ**, yalnız toplu koşumdan çıkarıldı (MIMARI §10):
#:
#:     python lab/kapi.py --tam --sadece garson     # açıkça istenirse
#:     python lab/kapi.py --tam --sadece eval_llm   # faz sonu, gerçek sağlayıcıyla
TOPLUDA_YOK = ("garson", "eval_llm")

#: ⟳ **② ÖLÇÜLDÜ (2026-08-12) — «konuşma senaryoları adımı ⊘ ölçülemez» YANLIŞTI.**
#:
#: Adım koşuldu: **9 sınıf, hepsi yeşil, ratchet'li** (`--kapi`, çıkış kodu 0). ⊘ olan
#: adımın kendisi değil, içindeki **tek vaka**: `vqr_kalicilik` (0/1, taban 0).
#:
#: Ve o ⊘ **doğru** bir işarettir, bir eksiklik değil: VQR yalnız `intent_source ==
#: "cube+llm"` yolunda öğrenir (`ask.py`; Faz 2b-2'nin ölçülmüş kararı — deterministik
#: bir cevabı dondurmak kazanç getirmez). LLM'siz CI modunda replay **yapısal olarak**
#: doğamaz. Eski sürüm bunu *«parafraz replay YOK ✅»* diye raporluyordu — ölçmediğini
#: ölçmüş gibi; FAZ 9.6 onu üçüncü bir duruma (`None` = ÖLÇÜLEMEDİ) çevirdi.
#:
#: ⊙ Ölçülebilir hâle gelmesinin tek yolu `--live` + gerçek sağlayıcıdır ve o **`A1`**
#: kalemidir — kullanıcının bağlayıcı kuralıyla **PARK** (*«ölçüm/altyapı tesisatı ürün
#: değildir»*). Yani ② bir borç değil, park edilmiş bir kalemin **gölgesidir**.
#:
#: *Bir ⊘ işaretini bir borç sanmak, dürüstlüğü bir eksiklik saymaktır.*

#: 🔴 **YEREL DEMET KAPISI = KORPUS + GERÇEK-DÜNYA** (2026-08-05'te ikinciyle genişledi).
#:
#: ## Neden ikinci bir korpus adımı — ve neden yereldeki tek ekleme bu
#:
#: `nl_corpus` soruları **katalogdan** üretir; yani sistemin **kendi kelimeleriyle**
#: sorar ve bu yüzden hep yüksek çıkar (%93,1). `gercek_dunya` ise **kullanıcının
#: kelimeleriyle** sorar — katalog sızıntısı yasağıyla (kural 1) katalog kelimeleri
#: **elenir**.
#:
#: > ⚠ İkisi aynı sistemi ölçüp **farklı sayı** verir, ve fark ölçümün kendisidir:
#: > *bir ürünün kendi sözlüğündeki başarısı, kullanıcının sözlüğündeki başarısı
#: > değildir.* Yalnız birincisini kapıya koymak, ikincisini görmemeyi kural hâline
#: > getirirdi.
#:
#: Maliyet: `route()` çağrıları koşut dağıtılıyor (`lab/kosut.py`), korpus paydasına
#: dokunmuyor. **Ölçüldü: ~1 dk 10 sn** — `nl_corpus`'un yanına eklenebilir bir bütçe.
#:
#: 🔴 **`--kapi` bayrağı ZORUNLU** — `konusma_senaryolari` tuzağı: o adım bayraksız
#: koşumda `main()` her yolda `0` döndüğü için **hiçbir koşulda kırmızı veremiyordu**
#: ve *"dört bileşenli bir kapının dörtte biri sessizce dekordu"*. Aynı hata burada
#: tekrarlanmasın diye bayrak açıkça verilir ve `gercek_dunya.kapi()` gerilemede
#: **mutlaka** sıfırdan farklı döner.
#:
#: ⚠ Metamorfik ölçüm ve konuşma korpusu **yerel kapıda YOK**: ikisi de teşhis
#: aletidir, kapı değil. Yerleri `--hepsi` ve gecelik CI.
YEREL_KAPI = ("korpus", "gercek")


def tam(sadece: tuple[str, ...] = (), *, hepsi: bool = False) -> int:
    """Demet kapısı. **Varsayılan: iki korpus.** `hepsi=True` → beş adım (CI).

    `sadece` verilirse **yalnız o adımlar** koşar.

    🔴 **KIRMIZI DOĞRULAMASI TÜM KAPIYI TEKRAR KOŞMAZ.** Kullanıcı kararı (2026-08-04):
    *"demette kapı kırmızı verince neden sadece kırmızı veren kısım tekrar çalışmıyor?"*
    — haklı: dört adımın biri kırmızıysa diğer üçü **zaten yeşil ölçüldü** ve kod o
    aşamalardan sonra değişmediyse tekrar koşmaları **saf israftır** (~13 dk).

    Doğru döngü:
    ```
    python lab/kapi.py --tam                  # demet kapısı (iki korpus)
    #  ✗ korpus kapısı  →  düzelt  →
    python lab/kapi.py --tam --sadece korpus  # YALNIZ kırmızı olan
    ```
    ⚠ **Sınır:** düzeltme **başka bir adımı besleyen** bir dosyaya dokunduysa
    (`OPERASYON.md §3` risk listesi) kısmi koşum yetmez — tüm kapı tekrar koşar.
    Bu ayrımı araç bilemez, **koşan kişi beyan eder**.
    """
    adimlar = (
        ([sys.executable, "lab/nl_corpus.py", "--kapi"], "korpus kapısı"),
        # 🔴 GERÇEK-DÜNYA KORPUSU — kullanıcının kelimeleriyle, katalogun değil.
        # `--kapi` bayrağı ZORUNLU (yukarıdaki dekor tuzağı). Gerileme kapısıdır,
        # eşik değil: *dün ne kadardıysa bugün ondan az olmasın.*
        ([sys.executable, "lab/gercek_dunya.py", "--kapi"], "gerçek-dünya korpusu"),
        # ⚡ `-n 8`: süit 8 dk 30 sn → 2 dk 15 sn (ölçüldü, 2499 test, SIFIR yeni kırmızı).
        # İzolasyon `tests/conftest.py`'de: her worker kendi derlenmiş proje ağacına yazar.
        ([sys.executable, "-m", "pytest", "-q", "-p", "no:warnings", "-n", "8"], "tam süit"),
        ([sys.executable, "-m", "eval.run"], "eval.run"),
        # 🔴 `--kapi` ZORUNLU: bayraksız koşumda `main()` her yolda 0 döner ve bu adım
        # **hiçbir koşulda kırmızı veremez** (ölçüldü: `returncode == 0`, senaryo tümden
        # çökse bile). Dört bileşenli bir kapının dörtte biri sessizce **dekordu**.
        ([sys.executable, "lab/konusma_senaryolari.py", "--kapi"], "konuşma senaryoları"),
        # 🔴🔴 **KASETLİ GARSON KORPUSU — GARSON BASAMAĞININ TEK TOPLU ÖLÇÜMÜ.**
        #
        # ⟳ Yazılmıştı ama **hiçbir koşuma bağlı değildi** (ölçüldü 2026-08-12:
        # `grep garson_korpusu lab/kapi.py tests/` → sıfır). Ve sebebi bir **miras**tı:
        # yukarıdaki `GARSON_TOPLUDA_YOK` gerekçesi (*«`--live` ister, kotaya bağlı,
        # BELİRLENİMSİZ»*) **canlı koşucu** `lab/garson.py` için yazılmıştı; kasetli
        # korpus ise kendi başlığında *«her demet sonunda, SIFIR API»* diyor ve
        # `--network none` altında **36 isabet · 0 ıska** ile koştuğu ölçüldü.
        #
        # *Bir sınıfın ilk üyesi için yazılmış gerekçe, ikinci üyeye sessizce miras kalır.*
        ([sys.executable, "lab/garson_korpusu.py", "--kapi"], "kasetli garson korpusu"),
        # 🔴 GARSON KAPISI — yalnız `--sadece garson` ile. `--live` ve ağ ister; ötekiler
        # `--network none` ile koşar. Toplu koşuma girmemesi bilinçlidir (yukarı bak).
        ([sys.executable, "lab/garson.py", "--live"], "garson kapısı"),
        # 🔴 **LLM DİLİMİ — VARSAYILAN YOLUN TEK OTOMATİK KANCASI** (denetim bulgusu).
        #
        # `eval/run.py` `--slice {det,llm}` destekliyor ve `eval/cases.yaml`'de `slice: llm`
        # vakaları duruyor. Ama yukarıdaki `eval.run` adımı **bayraksız** çağırıyor →
        # varsayılan `det`. Yani planın *"`route()` varsayılan değil, ispatlı istisnadır"*
        # dediği mimaride, **varsayılan yol hiç ölçülmüyordu**.
        #
        # ⚠ Toplu koşuma girmez ve sebebi `garson` ile aynı: gerçek sağlayıcı + anahtar
        # ister, `--hepsi` ise `--network none` ile koşar. Yeri **faz sonu**dur.
        # *Koşulmayan bir dilim, olmayan bir dilimden yalnızca daha pahalıdır: bakım
        # ister, güven verir, hiçbir şey ölçmez.*
        ([sys.executable, "-m", "eval.run", "--slice", "llm"], "eval LLM dilimi"),
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
    elif hepsi:
        # 🔴 `--hepsi` **belirlenimsiz adımların HEPSİNİ** atlar — ve bunu YAZAR.
        # Sessizce atlanan bir adım, atlanmamış gibi okunur (bu dosyanın kendi dersi).
        print(f"▶ `--hepsi`: {' · '.join(TOPLUDA_YOK)} ATLANDI — gerçek sağlayıcı + "
              "kota ister, BELİRLENİMSİZDİR. Yeri faz sonudur: `--sadece <adım>`.\n")
        adimlar = tuple(k for k, ad in zip(adimlar, ADIM_ANAHTARLARI, strict=True)
                        if ad not in TOPLUDA_YOK)
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

    # 🔴 ORTAM ENGELLİ ADIM — **açıkça istenmediyse** düşürülür, ve düşüşü özet
    # içinde `_belgeler_bildirimi()` **adıyla** yazar.
    #
    # ⚠ İki yanlış seçenek vardı ve ikisi de reddedildi: (a) yine de koşturmak → gecelik
    # CI, ortam eksiğini bir **ürün kusuru** gibi kırmızıya çevirirdi (`§F8` hijyeni);
    # (b) sessizce atlamak → yeşil özet, koşmamış bir kapıyı koşmuş gibi okuturdu
    # (`ADR-0020`). Üçüncü yol: **düşür ve söyle**.
    #
    # ⊙ `--sadece garson_korpusu` bu düşürmeyi **bilerek** atlar: açıkça istenen bir
    # adımın ortam reçetesini görmek, onun sessizce yok sayılmasından iyidir.
    if not sadece:
        _engelli = {ad for ad, (kosul, *_) in ORTAMA_BAGLI_ADIMLAR.items() if not kosul()}
        adimlar = tuple(a for a in adimlar if a[1] not in _engelli)

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
    # Dalga 1: İKİ KORPUS, sırayla (ikisi de tüm çekirdekleri ister)
    # Dalga 2: süit ‖ eval ‖ senaryo (süit 8 worker; ötekiler tek çekirdek, 2 dk 20 sn)
    # Toplam ~5 dk 20 sn — sıralı 15+ dk yerine. Yerel kapı yalnız dalga 1'dir.
    #
    # 🔴 GERÇEK-DÜNYA KORPUSU DA DALGA 1'DE — ve bunun sebebi ölçülmüş bir tuzak:
    # `lab/kosut.py` `route()` çağrılarını **16 sürece** dağıtıyor. Süitle aynı anda
    # koşarsa iki taraf da çekirdek için yarışır ve **ikisi de yavaşlar** — üstelik
    # `--hepsi`'nin kendi belgesinde kayıtlı bir yarış var: *"korpus + süit eş zamanlı
    # compose yapınca derleme kilidi 60 sn'de zaman aşımına uğradı, süit 934 hata verdi"*.
    #
    # ⚠ İki korpus **birbiriyle de paralel koşmaz**: ikisi de tüm çekirdekleri ister,
    # yan yana koymak toplam süreyi kısaltmaz — yalnız ikisini birden yavaşlatır.
    # *Paralellik, kaynak boştayken kazanç; doluyken kuyruk üretir.*
    _AGIR_ADIMLAR = ("korpus kapısı", "gerçek-dünya korpusu")
    dalga1 = [a for a in adimlar if a[1] in _AGIR_ADIMLAR]
    dalga2 = [a for a in adimlar if a[1] not in _AGIR_ADIMLAR]
    sonuclar_map: dict[str, tuple[int, str]] = {}
    for _sira, dalga in enumerate((dalga1, dalga2)):
        if not dalga:
            continue
        # ⚠ Dalga 1 **SIRAYLA** koşar (her adım tüm çekirdekleri ister); dalga 2
        # paralel. Bu ayrım olmadan iki korpus birbirinin çekirdeğini yer.
        if len(dalga) == 1 or _sira == 0:
            for komut, baslik in dalga:
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
    _belgeler_bildirimi()
    print("\n".join(ozet))
    if sadece:
        print("\n" + ("✓ KISMİ KOŞUM YEŞİL — ama bu bir DEMET KAPISI DEĞİL"
                      if kotu == 0 else "✗ KISMİ KOŞUM KIRMIZI"))
    elif hepsi:
        # ⚠ Adım sayısı **SAYILIR, yazılmaz**: burada `"dört adım"` yazıyordu ama
        # `--hepsi` beş adım koşuyor (`gercek` 2026-08-05'te eklendi ve bu cümle
        # güncellenmedi). *Bir özetin içindeki elle yazılmış sayı, ilk değişiklikte yalan
        # olur* — bu dosyanın `_AGIR` sabitiyle aynı sınıf kusur.
        print("\n" + (f"{'✓' if kotu == 0 else '✗'} TAM KAPI ({len(adimlar)} adım) "
                      f"{'YEŞİL' if kotu == 0 else 'KIRMIZI'}"))
    else:
        print("\n" + ("✓ DEMET KAPISI (korpus) YEŞİL" if kotu == 0
                      else "✗ DEMET KAPISI (korpus) KIRMIZI"))
    return kotu


#: 🔴🔴 `A7` — **ROUTE KORPUSU DEĞİŞİKLİK-TETİKLİDİR.**
#:
#: Raporun `§4i` kararı: kapının merkezi **kasetli garson korpusu**dur (her demet, sıfır
#: API); route korpusu (~10.800 soru, **13-20 dk CPU**) *"her demet sonunda"* değil
#: **kritik değişiklikte + günde 1** koşar.
#:
#: ⊙ Gerekçe ölçülmüş: route korpusu iki şeyi görür ve ikisi de **kapsam** eksenindedir —
#: *"kaç soru cevaplanabiliyor"* (payda) ve `sessiz_yanlis`. Bu iki sayı ancak
#: **route'un kendisi ya da katalog** değiştiğinde kıpırdar. Bir anlatı düzeltmesinden
#: sonra 13 dakika beklemek, ölçmediğini ölçmek için ödenen bir bedeldir.
#:
#: ⚠ Liste elle değil **desenle** tutulur: yeni bir pack ya da yeni bir router modülü
#: eklendiğinde tetikleyici kendiliğinden kapsar. *Elle tutulan bir tetik listesi, bir
#: gün eklenen dosyayı görmez ve kapı sessizce kör olur.*
ROUTE_TETIKLEYICILERI: tuple[str, ...] = (
    "app/cube_router",      # eşleştiricinin kendisi
    "app/wren_service",     # şema derlemesi + sinonim katmanları
    "app/compose",          # katman birleştirme
    "app/katalog_metni",    # garsonun menüsü
    "demo/packs/",          # katalog verisi (küp · ölçü · sinonim · sahiplik)
)


def route_korpusu_gerekli(degisen: list[str]) -> tuple[bool, str]:
    """Değişen dosyalar route korpusunu **tetikliyor mu**? Döner: `(gerekli, gerekçe)`.

    🔴 Boş `degisen` → **gerekli** (bilinmeyen bir değişiklik, en kötüsü varsayılır).
    *Ölçmediğini güvenli saymak, bu deponun üç kez ödediği hatadır.*
    """
    if not degisen:
        return True, "değişen dosya listesi verilmedi — bilinmeyen değişiklik en kötüsü sayılır"
    vuran = sorted({t for t in ROUTE_TETIKLEYICILERI
                    for d in degisen if t in d.replace("\\", "/")})
    if vuran:
        return True, "tetikleyici dokunuldu: " + ", ".join(vuran)
    return False, ("route/katalog dosyalarına dokunulmadı — korpusun ölçtüğü iki eksen "
                   "(payda · sessiz_yanlış) kıpırdayamaz")


#: 🔴🔴 `belgeler/` BAĞLANMAZSA SESSİZCE KAYBOLAN KAPILAR.
#:
#: ## Ölçülen kusur (2026-08-12, denetim ajanı buldu)
#:
#:     belgeler BAĞLI DEĞİL  → 11 skipped in 0.12s
#:     belgeler BAĞLI        → 11 passed in 4.85s
#:
#: Ve hiçbir **belgeli reçete** o mount'u içermiyordu (`grep "belgeler:/belgeler"` →
#: `MIMARI.md`/`CLAUDE.md`/`OPERASYON.md`'de sıfır). Yani *«yayınlanmış bir sayı
#: çürümesin»* diye kurulan iki kapı (`§F8` doğruluk yayını · `§0.6` karne manşeti)
#: **hiç koşmuyordu** — ve `pytest` bunu `skipped` diye, yani **iyi haber gibi**
#: raporluyordu.
#:
#: 🔴 Bu, `§F8` hijyeninin **aynadaki hâli**: orada *«kapı, ortam eksiğini ürün kusuru
#: gibi göstermemeli»* dedik ve skip'i doğru bulduk. Doğruydu — ama yarısıydı:
#: **koşucu da o eksiği sessizce yutmamalı.**
#:
#: > *Bir kapıyı ortam eksiğinde susturmak dürüstlüktür; o susmayı DUYURMAMAK ise
#: > kapsamı sessizce kırpmaktır.*
#:
#: ⚠ Koşum **düşürülmez** (yerel geliştirici `belgeler` olmadan da koşabilmeli); yalnız
#: kaybedilen kapsam **adıyla** yazılır — `--hizli`nın *«KAPSANMADI»* satırıyla aynı
#: disiplin (`ADR-0020`: sessiz yutma yok).
def _belgeler_var_mi() -> bool:
    """`belgeler/` konteynerden görülüyor mu — iki yerleşim de denenir."""
    import pathlib as _p

    return any((_p.Path(a) / "arastirma").is_dir()
               for a in ("/belgeler", _p.Path(__file__).resolve().parents[2] / "belgeler"))


def _repo_koku_var_mi() -> bool:
    """Repo kökü (backend'in ÜSTÜ) görülüyor mu — `test_belge_duzeni` bunu ister."""
    import pathlib as _p

    kok = _p.Path(__file__).resolve().parents[2]
    return (kok / "belgeler").is_dir() and (kok / "backend").is_dir()


#: 🔴 `dosya → (koşul, ne kaybedilir, reçete ipucu)`.
#:
#: ⟳ **LİSTE İKİ DOSYADAN ÜÇE ÇIKTI (2026-08-12) — ve sebebi bir derstir.** İlk yazımda
#: yalnız `belgeler/` bağımlılığını saydım; sonra ölçüldü ki `test_belge_duzeni.py`'nin
#: **yedi** testi de atlanıyor — **başka** bir ortam eksiğinden (repo kökü). Yani liste
#: bir sınıfı değil, o sınıfın **ilk gördüğüm üyesini** sayıyordu.
#:
#: *Bir kapsam kaybını bildirirken tek bir sebebi saymak, ikinci sebebi sessiz bırakır.*
ORTAMA_BAGLI_KAPILAR: dict[str, tuple] = {
    "test_f8_dogruluk_yayini.py": (
        _belgeler_var_mi, "yayınlanmış doğruluk sayısı (§F8)",
        '-v "$PWD/belgeler:/belgeler:ro"'),
    "test_karne_kendini_sayar.py": (
        _belgeler_var_mi, "§0.6 karne manşeti satırlarla tutsun",
        '-v "$PWD/belgeler:/belgeler:ro"'),
    "test_belge_duzeni.py": (
        _repo_koku_var_mi, "belge düzeni denetimi (7 test)",
        "repo KÖKÜNÜ bağlayın (yalnız `backend/` yetmez)"),
}

#: Geriye dönük ad — `test_ortam_butunlugu` ve dış okuyucular için.
BELGELERE_BAGLI_KAPILAR = tuple(ORTAMA_BAGLI_KAPILAR)


def _garson_korpusu_kosulabilir() -> bool:
    """🔴 `A1` — kasetli korpusun **üç** ön koşulu; üçü de ORTAM, hiçbiri ürün.

    Ölçüldü (2026-08-12), üçü de tek tek: kaset kurulmazsa araç **canlı** koşmaya
    çalışır (`--network none` altında çökme), kimlik kaynağı yanlış dosyaysa `/ask`
    401 döner (ve o **kimlik kusuru gibi** okunur), rapor dosyası root sahipliyse
    korpus sonuna kadar koşup **son satırda** düşer.

    ⚠ Bu bir onarım değil bir **koşuldur**: onarımı aracın kendisi (`--kapi` çıktısı)
    komutlarıyla yazar. Buradaki tek karar, adımı **sessizce yeşil saymamak**.
    """
    import os
    import pathlib as _p

    lab = _p.Path(__file__).resolve().parent
    if not (lab / "kasetler" / "garson-korpus.json").is_file():
        return False
    if not (os.environ.get("DIMA_LLM_PROVIDER") and os.environ.get("DIMA_DATABASE_URL")):
        return False
    rapor = lab / "reports" / "garson_korpusu.md"
    return not (rapor.exists() and not os.access(rapor, os.W_OK))


#: 🔴 `adım → (koşul, ne kaybedilir, reçete)` — `ORTAMA_BAGLI_KAPILAR`ın **adım**
#: karşılığı.
#:
#: ⚠ Neden ayrı bir sözlük: o sözlüğün her anahtarı `tests/` altında **var olan bir
#: dosya** olmak zorunda (`test_ortam_butunlugu` bunu ölçüyor, ve haklı — bayat bir
#: bildirim gürültüdür). Bir lab adımı o yüklemi karşılayamaz. *İki farklı şeyi tek
#: listeye sıkıştırmak, listenin yüklemini ikisine de yanlış uygular.*
ORTAMA_BAGLI_ADIMLAR: dict[str, tuple] = {
    "kasetli garson korpusu": (
        _garson_korpusu_kosulabilir,
        "garson basamağı — trafiğin %37'si (21 senaryo · çok turlu · kasetli)",
        'docker cp dima-backend-core:/app/logs/dima.db /tmp/canli.db  →  '
        '--env-file .env -v /tmp:/cp -e DIMA_DATABASE_URL=sqlite:////cp/canli.db'),
}


def _belgeler_bildirimi() -> None:
    dusen = [(ad, ne, ipucu) for ad, (kosul, ne, ipucu)
             in (*ORTAMA_BAGLI_KAPILAR.items(), *ORTAMA_BAGLI_ADIMLAR.items())
             if not kosul()]
    if not dusen:
        return
    print("\n🔴 KAPSAM KAYBI: ortam eksik → şu kapılar HİÇ KOŞMADI:")
    for ad, ne, ipucu in dusen:
        print(f"      ↳ {ad}  ({ne})\n           çare: {ipucu}")
    print("   Yeşil bir özet, bu kapıların koştuğu anlamına GELMEZ.")


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
    ap.add_argument("--tetik", action="store_true",
                    help="`A7` — `--degisen` route/katalog'a dokunduysa `--tam` koş, "
                         "yoksa ATLA ve sebebini yaz (13-20 dk tasarruf)")
    a = ap.parse_args()
    if a.tetik:
        gerekli, gerekce = route_korpusu_gerekli(a.degisen)
        print(f"`A7` route korpusu: {'KOŞULACAK' if gerekli else 'ATLANDI'} — {gerekce}")
        if not gerekli:
            return 0
        return tam(tuple(a.sadece), hepsi=a.hepsi)
    if a.tam or a.hepsi:
        return tam(tuple(a.sadece), hepsi=a.hepsi)
    if a.hizli:
        return hizli(a.degisen)
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
