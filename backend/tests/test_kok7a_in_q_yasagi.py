"""🔴 KÖK-7a — **`in q` YASAĞI**: sözlükler biçimbirim disipliniyle taranır.

## Ölçülen kusur — *"kural tanındı, iki yerde uygulandı, ZORUNLU KILINMADI"*

`_covers` (Faz 0.4) ve `_syn_hit` (Faz D3) düz alt-dize taramasından **ayrı ayrı**
kurtarıldı ve ikisinin de kod yorumu bunu *"anti-desen"* diye adlandırıyor. Ama modülde
**25 yerde** sözlükler hâlâ `w in q` ile taranıyordu. Raporun teşhisi aynen buydu:

> *"Desen tanınmış, tek tek düzeltilmiş, ama bir KAPIYA bağlanmamış. Bu yüzden her yeni
> özellik onu yeniden doğuruyor. Kök neden kusur değil, **kusurun tekrarına izin veren
> boşluk**."*

⊙ Ölçülen sahte eşleşmeler:

| soru | sözlük kelimesi | eski davranış |
|---|---|---|
| `trendyol satislari` | `trend` *(granülerlik)* | 🔴 soru **zaman serisine** çevriliyordu |
| `bu ayrica onemli` | `bu ay` *(dönem)* | 🔴 **bu ay** filtresi takılıyordu |
| `uygun fiyat` | `gun` | 🔴 günlük kova |
| `detay ver` · `ayrica bakalim` | `ay` | 🔴 aylık kova |

🔴 En zararlısı `trendyol`: bir **müşteri adı** cevabın şeklini değiştiriyordu ve kullanıcı
bunu göremiyordu.

⊘ **Ve biri KAPANMADI:** `kodlama hatası` → `kod` hâlâ eşleşiyor (`kod`+`la`+`m`+`a`
geçerli bir zincirdir). Bilerek: *"yalnız çekim ekleri"* diye ikinci bir liste yazmak
ADR-0008'in yasağıdır. Karar `test_TURETME_EKI_SINIRI_YAZILI_KALIR`'da **yazılı** durur.

## 🔴 VE YASAK, GİZLENMİŞ BİR BOŞLUĞU AÇIĞA ÇIKARDI

`in q` kaldırılınca `bugunku ciro` **dönem filtresini kaybetti**: `bugun` alt-dize olarak
geçiyordu ama `bugun`+`ku` biçimbirim tablosunda **geçerli bir çekim değildi** (`-ki`nin
yuvarlak-ünlü biçimi `-kü` eksikti). Yani düz alt-dize taraması, tablodaki bir deliği
**örtüyordu**. *Bir yanlışın ikinci bir yanlışı örtmesi, ikisini birden düzeltmeyi zorunlu
kılar.*

## ⚠ VE BİR SINIR: kuralı HER YERE uygulamak da yanlış

`dün` için `_syn_hit` denendi ve **`dünya geneli ciro`** soruya dün filtresi taktı —
`dun`+`ya` biçimbirim tablosunda geçerli bir zincirdir (`-ya` yönelme eki). Kapalı sınıf
bir zaman zarfı için genel çekim denetimi **fazla cömerttir**; `_DUN_RE` kendi sınırını
taşır. *Bir kuralı her yere uygulamak, onu hiç uygulamamak kadar yanlış olabilir.*
"""

from __future__ import annotations

import ast
import pathlib

import pytest

import app.cube_router as cr
from app.cube_router import _gecenler, _herhangi, _syn_hit, date_filters

KAYNAK = pathlib.Path(cr.__file__).read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · YASAK — kod yapısı kapısı
# ═══════════════════════════════════════════════════════════════════════════════

def test_HICBIR_SOZLUK_IN_Q_ILE_TARANMIYOR():
    """🔴 **ASIL KAPI** — *kusurun tekrarına izin veren boşluk* kapatılır.

    ⚠ AST ile taranır, metinle değil: bu depoda bir kapı metin tarayıp **kendi
    belgelendirmesini** yakaladı (`test_OLUMSUZLUK_TEK_SAHIPTEN`, `firesiz` docstring'de).
    Yorumlar ve docstring'ler AST'de yoktur — kapı yalnız **çalışan kodu** görür."""
    agac = ast.parse(KAYNAK)
    kotu = []
    for d in ast.walk(agac):
        if not (isinstance(d, ast.Compare) and len(d.ops) == 1
                and isinstance(d.ops[0], (ast.In, ast.NotIn))):
            continue
        sag = d.comparators[0]
        if isinstance(sag, ast.Name) and sag.id == "q":
            kotu.append(f"satır {d.lineno}: {ast.unparse(d)}")
    assert not kotu, ("🔴 sözlük yine düz alt-dize ile taranıyor — `_herhangi`/"
                      "`_gecenler`/`_syn_hit` kullan:\n  " + "\n  ".join(kotu))


def test_TEK_SAHIP_KORUNUYOR():
    """⚠ `_herhangi`/`_gecenler` **yeni bir kural taşımaz**: kararı `_syn_hit` verir, o da
    `_ek_gecerli`ye sorar. Kendi eşleşme mantığını yazan bir yardımcı, kapatılan kusuru
    üçüncü kez doğururdu."""
    agac = ast.parse(KAYNAK)
    for ad in ("_herhangi", "_gecenler"):
        fn = next(n for n in ast.walk(agac)
                  if isinstance(n, ast.FunctionDef) and n.name == ad)
        cagrilar = {n.func.id for n in ast.walk(fn)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
        assert "_syn_hit" in cagrilar, f"🔴 `{ad}` kendi eşleşmesini yazıyor"
        # ⚠ Alt-dize denetimi ÜSTTEKİ AST kapısının işi. Burada metinle tekrar aramak,
        # fonksiyonun KENDİ belgelendirmesini yakalar (`ast.unparse` docstring'i korur) —
        # bu depoda birebir aynı hata bir kez yapıldı. *Bir kuralın iki denetçisi,
        # ikincisinin yanlış yerden bakmasıyla biter.*


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · ÖLÇÜLEN SAHTE EŞLEŞMELER — dördü de kapanıyor
# ═══════════════════════════════════════════════════════════════════════════════

SAHTE = [
    ("trendyol satislari", "trend", "müşteri adı granülerlik sanılıyordu"),
    ("bu ayrica onemli", "bu ay", "dönem filtresi takılıyordu"),
    ("uygun fiyat", "gun", "günlük kova"),
    ("detay ver", "ay", "ay ⊂ detay"),
    ("ayrica bakalim", "ay", "ay ⊂ ayrıca"),
]


@pytest.mark.parametrize("q,kelime,neden", SAHTE)
def test_SAHTE_ESLESME_KAPANDI(q, kelime, neden):
    """🔴 Alt-dize **geçiyor**, biçimbirim **geçmiyor** — fark tam olarak kusurdur."""
    assert kelime in q, "⊘ vaka bayatlamış: alt-dize artık geçmiyor"
    assert not _syn_hit(q, kelime), f"🔴 hâlâ sahte eşleşiyor ({neden})"


GERCEK = [
    ("bu ayki fire", "bu ay"), ("bugunku ciro", "bugun"), ("gunluk rapor", "gunluk"),
    ("aylara gore ciro", "aylar"), ("ceyreklik uretim", "ceyrek"),
    ("en yuksek fire hangi makinede", "en yuksek"),
]


@pytest.mark.parametrize("q,kelime", GERCEK)
def test_GERCEK_ESLESME_KORUNDU(q, kelime):
    """🔴 Kapının **asıl sınavı**: çekimli gerçek kullanımlar kaybolmamalı.
    *Bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*"""
    assert _syn_hit(q, kelime), f"🔴 meşru çekim kayboldu: «{q}» ∌ {kelime}"


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · GİZLENMİŞ BOŞLUK — `-ki`nin yuvarlak biçimi
# ═══════════════════════════════════════════════════════════════════════════════

def test_BUGUNKU_DONEM_FILTRESI_ALIYOR():
    """🔴 `in q` kaldırılınca ortaya çıkan **gizli boşluk**: `bugun`+`ku` çekim
    sayılmıyordu. Alt-dize taraması onu örtüyordu."""
    assert date_filters("bugunku ciro"), "🔴 `bugünkü` dönemsiz kaldı"
    assert date_filters("dunku uretim"), "🔴 `dünkü` dönemsiz kaldı"


def test_KU_ATOMU_BILINEN_DELIKLERI_ACMADI():
    """⚠ `_SUFFIX_ATOMS`'un kendi DİKKAT notu: atom eklemek kapatılmış delikleri açabilir.
    Belgelenmiş üç delik burada kilitli tutulur."""
    assert not cr._covers("mal", "maliyeti")
    assert not cr._covers("kar", "kargo")
    assert not cr._covers("fire", "firesiz")
    assert cr._covers("bugun", "bugunku") and cr._covers("dun", "dunku")


def test_DUN_KAPALI_SINIF_SINIRI():
    """🔴 **Ölçülen yanlış-pozitif:** `dun`+`ya` geçerli bir zincirdir (`-ya` yönelme eki)
    → genel çekim denetimi `dünya geneli ciro`ya **dün filtresi** takıyordu.

    *Bir kuralı her yere uygulamak, onu hiç uygulamamak kadar yanlış olabilir.*"""
    assert not date_filters("dunya geneli ciro"), "🔴 `dünya` dün sanıldı"
    assert not date_filters("dundar musteri cirosu"), "🔴 `dundar` dün sanıldı"
    assert date_filters("dun ciro") and date_filters("dunku uretim")


# ═══════════════════════════════════════════════════════════════════════════════
# 4 · YARDIMCILARIN KENDİSİ
# ═══════════════════════════════════════════════════════════════════════════════

def test_TURETME_EKI_SINIRI_YAZILI_KALIR():
    """⊘ **ÖLÇÜLDÜ ve KAPATILMADI — bilerek.** `kodlama` biçimbirim olarak `kod`+`la`+`m`+`a`
    diye ayrışır ve `_ek_gecerli` bunu **geçerli** sayar. Yani `kodlama hatası` sorusunda
    `kod` hâlâ eşleşir.

    Sebep `_ek_gecerli`nin kendi belgesinde yazılı: tablo **türetme** eklerini de geçerli
    sayar (aynı not `geçen aylık fire` için de düşülmüş). *"Yalnız çekim ekleri"* diye
    ikinci bir liste yazmak ADR-0008'in yasakladığı şeydir — dili kelime listesiyle
    kovalamak. Etkisi ölçüldü ve **küçük**: yalnız ad/kod sütun dedup'ı, sayıyı değil
    sütun seçimini etkiler.

    🔴 Bu test o sınırın **yazılı kalmasıdır**: bir gün türetme/çekim ayrımı yapılırsa
    burası kırmızı verir ve karar yeniden alınır — sessizce değişmez."""
    assert _syn_hit("kodlama hatasi", "kod"), \
        "⟳ türetme eki sınırı değişmiş — KÖK-7a'nın kayıtlı kararını gözden geçir"


def test_HERHANGI_VE_GECENLER_TUTARLI():
    """⚠ İkisi aynı kararı vermeli — ayrışırlarsa aynı soru geldiği yola göre farklı
    davranırdı (bu deponun *"üç çağrı yeri"* dersi)."""
    sozluk = ("trend", "aylik", "ceyrek", "gunluk")
    for q in ("trendyol satislari", "aylik ciro", "ceyreklik uretim", "gunluk rapor", "x"):
        assert _herhangi(q, sozluk) == bool(_gecenler(q, sozluk)), q


def test_BOS_SOZLUK_SESSIZ():
    """⚠ Boş sözlük `False`/`set()` döner — bir sözlük boşalırsa kapı sessizce açılmasın
    diye değil, **patlamasın** diye: boş liste bir hata değil, bir olgudur."""
    assert _herhangi("herhangi bir soru", ()) is False
    assert _gecenler("herhangi bir soru", ()) == set()
