"""FAZ 7.9/7.10 kapısı — **mock yok, NUL yok, bayrak yüzeyle aynı commit'te.**
[bayraksız: kapı + V-6]

## Ölçüm teşhisi TERK EDİLEN DALA ait çıkardı — 7.1'le aynı sınıf

| iddia | ölçüm (bu dal) |
|---|---|
| *"`src/lib/mock/` Plan 3'ün henüz olmayan uçlarını taklit ediyor"* | **dizin YOK** |
| *"`PivotTable.tsx` binary — gömülü NUL (`\\x00`)"* | 🔴 **DOĞRU ÇIKTI — iki NUL, `:26` ve `:52`** |

> 🔴 **İki iddiadan biri yanlış, biri DOĞRU — ve bu, ikisini de ölçmenin sebebidir.**
> Mock için yapılacak iş **kilitlemek** (*bir dalda çözülmüş bir sorun, kilitlenmediyse
> çözülmemiştir* — 7.1'in cümlesi, aynı sınıf ikinci kez). NUL için yapılacak iş
> **düzeltmek**: `PivotTable.tsx` bu dalda da iki NUL taşıyordu.

### 🔴 NUL neden hiçbir aracın gözüne çarpmadı

Dosya **UTF-8 olarak tamamen geçerliydi**. Linter, derleyici, `tsc`, kod incelemesi —
hiçbiri görmedi; yalnız **bayt düzeyinde** bakan bu kapı yakaladı.

⚠ Ve düzeltme ayracı değiştirmekle bitmedi: asıl kusur bileşik anahtarın **iki ayrı yerde
elle kurulmasıydı** (`set` ve `get`) — biri bir gün başka bir ayraç kullanır ve `get`
`set`'i **bulamaz**, tablo sessizce boşalır. Anahtar artık `anahtar()`'ın içinde, tek yerde.
⚠ Yeni ayraç (`␟`, U+241F) veride **geçemeyecek** bir karakter olmalıydı: `-` ya da `|`
seçilseydi `"A-B"+"C"` ile `"A"+"B-C"` **aynı anahtarı** üretir ve iki hücre birbirini ezerdi.

## Neden mock, yetim uçtan **daha kötüdür**

Yetim uç: **yetenek var**, tüketicisi yok → kimse görmez, kimse zarar görmez.
Mock: **yetenek yok**, ama ekranda **varmış gibi** görünür → kullanıcı ona **güvenerek
karar verir**. *Var olmayan bir yeteneği var göstermek, eksik bir yetenekten pahalıdır.*

## Dört hatanın bu daldaki karşılığı

| # | Hata | Bu dal |
|---|---|---|
| 1 | bayrak yüzeyle **aynı commit'te** değil (dalda **%43,8** retrofit) | kapı: her `useFeature` adı `FLAG_REGISTRY` **ve** `features.yml`'de (7.1'de kilitlendi) |
| 2 | `ui_*` bayrakları backend'e | ✅ tüm `ui_*` `FLAG_REGISTRY`'de |
| 3 | gömülü **NUL** | kapı: hiçbir kaynak dosyada `\\x00` |
| 4 | `src/lib/mock/` geçici | kapı: dizin **doğmasın** |
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.kapi_ortak import fe_kaynak, frontend_dir

_KOK = Path(__file__).resolve().parents[1]


def test_MOCK_dizini_YOK():
    """🔴 *Var olmayan bir yeteneği var göstermek, eksik bir yetenekten pahalıdır.*

    Bir mock **bir gün** gerekirse, gerçek uç indiğinde silinmesi bu kapıya bağlıdır —
    ve kapı **şimdi** yazılır, mock doğduğunda değil. *Bir temizlik borcunu borcun
    doğduğu anda yazmak, onu bir söz olmaktan çıkarır.*
    """
    mock = frontend_dir() / "lib" / "mock"
    assert not mock.exists(), (
        f"🔴 `{mock}` var. Her mock, gerçek uç geldiğinde SİLİNİR ve silinmesi bu teste "
        f"bağlıdır. Mock kalırsa kullanıcı **olmayan bir yeteneğe güvenerek karar verir**.")


def test_MOCK_ithali_YOK():
    """⚠ Dizin silinip **import** kalırsa derleme kırılır ve kusur bir *"build hatası"*
    gibi görünür — oysa asıl kusur, bir yüzeyin sahte veriye bağlanmış olmasıdır."""
    kaynak = fe_kaynak()
    kotu = re.findall(r'from\s+"[^"]*\bmock\b[^"]*"', kaynak)
    assert not kotu, f"🔴 mock ithali: {kotu}"


def test_SAHTE_VERI_isaretleri_YOK():
    """⚠ Bir mock **dizin adı olmadan** da yaşar: `const SAHTE = [...]` bir bileşenin
    içinde durur ve hiçbir kapı görmez. Bu tarama en yaygın adları yakalar.

    🔴 Yalnız **atama** aranır, kelime değil: bir yorumda geçen *"mock"* kelimesi bir
    mock değildir — ve bu operasyonda metin taramaları kendi belgesini **altı kez**
    yakaladı.
    """
    kaynak = fe_kaynak()  # yorumsuz
    kotu = re.findall(r"const\s+(MOCK_\w+|SAHTE_\w+|FAKE_\w+|DUMMY_\w+)\s*[:=]", kaynak)
    assert not kotu, (
        f"🔴 Sahte veri sabiti: {kotu}. Bir yüzey sahte veriyle dolduruluyorsa, o yüzey "
        f"**yok** demektir — ve bunu kullanıcı değil bu kapı söylemeli.")


def test_GOMULU_NUL_yok():
    """🔴 Hata (3): teşhis **BOM değil, gömülü NUL**'du (`\\x00`, bileşik-anahtar ayracı
    olarak). Dosya UTF-8 olarak **geçerliydi** — bu yüzden hiçbir linter görmedi.

    ⚠ *Görünmez bir ayraç, kendisini bir kodlama sorunu gibi gösterir ve kimse veri
    modeline bakmaz.* Ayraç görünür bir karakter olmalı.
    """
    kotu = []
    for p in sorted(frontend_dir().rglob("*")):
        if p.is_file() and p.suffix in (".ts", ".tsx", ".css", ".json"):
            if b"\x00" in p.read_bytes():
                kotu.append(p.relative_to(frontend_dir()).as_posix())
    assert not kotu, (
        f"🔴 Gömülü NUL (`\\x00`) taşıyan dosya(lar): {kotu}. Bir ayraç GÖRÜNÜR bir "
        f"karakter olmalı — görünmez olan, bir kodlama hatası sanılır ve veri modeline "
        f"kimse bakmaz.")


def test_UI_BAYRAKLARI_backendde():
    """Hata (2): `ui_*` bayrakları **backend'in** kayıt defterinde yaşar; frontend'de
    ikinci bir kaynak açmak kill-switch'i **yarım** bırakır (MIMARI §6.13z/9.11)."""
    from app.features import FLAG_REGISTRY

    ui_adlari = set(re.findall(r'useFeature\(\s*"(ui_[a-z0-9_]+)"', fe_kaynak()))
    eksik = sorted(ui_adlari - set(FLAG_REGISTRY))
    assert not eksik, f"🔴 Frontend'de okunan ama kayıtta olmayan `ui_*` bayrak(lar): {eksik}"


def test_V6_BAYRAK_TEMIZLIK_BORCU_gorunur():
    """🔴 Hata (1): dalda **32 commit'in 14'ü (%43,8)** bayrağı yüzeyden **sonra** ekledi.

    *Sonradan eklenen bir bayrak, aradaki commit'lerde kapatılamayan bir yüzey demektir.*
    Kapı geçmişi düzeltemez ama **bugünü** kilitler: her `useFeature` adının kayıtta **ve**
    fabrika varsayılanında olması (`test_ui_bayrak_tekligi`) bu borcun **ödenmiş hâlidir**.
    Burada o kapının **varlığı** kilitleniyor — bir kuralın kapısını silmek, kuralı silmektir.
    """
    kapi = _KOK / "tests/test_ui_bayrak_tekligi.py"
    assert kapi.exists()
    src = kapi.read_text(encoding="utf-8")
    assert "FLAG_REGISTRY" in src and "features.yml" in src


def test_AYRAC_TEK_YERDE_kuruluyor():
    """🔴 NUL'u değiştirmek **yarım bir düzeltmedir**. Asıl kusur, bileşik anahtarın
    `set` ve `get`'te **iki ayrı yerde elle** kurulmasıydı: biri bir gün başka bir ayraç
    kullanır, `get` `set`'i **bulamaz** ve tablo **sessizce boşalır**.

    ⚠ Ayrıca ayraç veride **geçemeyecek** bir karakter olmalı: `-` seçilseydi
    `"A-B"+"C"` ile `"A"+"B-C"` aynı anahtarı üretir, iki hücre birbirini ezerdi.
    """
    from tests.kapi_ortak import fe_dosyalari

    src = fe_dosyalari()["components/PivotTable.tsx"]
    assert "function anahtar(" in src, "🔴 anahtar iki yerde elle kuruluyor"
    assert src.count("${AYRAC}") == 1, "🔴 ayraç birden çok yerde yazılmış"
    assert "`${e}" not in src, "🔴 elle kurulan bileşik anahtar kalmış"


def test_BU_DALDA_OLCULEN_hal_BELGEDE_yazili():
    """⊘ *Bir teşhisi ölçmeden devralmak, çözülmüş bir sorunu ikinci kez çözmektir* —
    ya da daha kötüsü, hiç var olmamış bir sorunu.

    🔴 **Bu kapı bir kez kendini ölçüyordu**: doğrulama dizgisi (`"DOĞRU ÇIKTI"`) hem
    belgede hem de `assert` satırının kendisinde geçiyordu, yani belge silinse bile
    **yeşil kalırdı**. Artık yalnız **modül belgesi** (`__doc__`) okunuyor — *ölçüm
    aracının kendisi de bir bağımlılıktır.*
    """
    doc = __doc__ or ""
    assert "dizin YOK" in doc, "🔴 mock ölçümü belgede yazılı değil"
    assert "iki NUL" in doc, "🔴 NUL ölçümünün SONUCU belgede yazılı değil"
