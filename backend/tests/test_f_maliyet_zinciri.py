r"""🔴🔴 `§F` — **MALİYET ZİNCİRİ: ölçülüyor, ama HİÇBİR YERDE TOPLANMIYOR.**

## Ölçüm (2026-08-12) — `F`'nin üç kalemi

| # | kalem | bulgu |
|---|---|---|
| **①** | istem boyutu | ✅ **kırpma var**: `katalog_metni.py:353` `_dar = "sema_daraltma" in _bayraklar`; bayrak `features.yml:224` **`beta`**. Katalog metni soruya göre **daraltılıyor**, kapalıyken soru **yok sayılır** (`KURAL B`). |
| **②** | gölge sayacı | ⚠ `compose.py:808-810` `shadow` kademesi **loglar** (*«%d cube birleşecekti, YAZILMADI»*) ama **sayaç yok** — kaç kez koştu, kaç kez ayrıştı **toplanmıyor**. |
| **③** | token telemetrisi | ✅ **var ve KALICI**: `llm.record_llm_usage(model, input_tokens, output_tokens, latency_ms)` (`llm.py:109`, **5** çağrı) → istek-kapsamlı `ContextVar` → `answer.py:258` `InteractionLog.llm_input_tokens`/`llm_output_tokens`/`llm_model`/`llm_latency_ms`. |

## `F`'nin ASIL bulgusu — ikisi aynı kusur

`②` ve `③` **aynı şeklin** iki hâli: **sayı üretiliyor, hiçbir yerden okunamıyor.**
Ölçüldü: `app/routers/` altında `input_tokens` arayan **hiçbir uç yok** (0 eşleşme).
Yani maliyet **kaydediliyor** ama **raporlanmıyor**.

> 🆓 *Bir boşluğu saymak için önce ona ad ver.* Adı: **toplama katmanı yok.**

⊘ **KARAR: uç AÇILMAZ, boşluk RAPORLANIR** — ve gerekçe `§G`'nin kendi kuralı:
bir `/stats/maliyet` ucu bugün yazılsa **ön uç tüketicisi olmayan bir uç** olurdu, yani
`§G`'nin tam da kapatmak üzere olduğu **yetim uç** sınıfını **elimizle üretirdik**.
Kullanıcının talimatı da bu yönde: *«riskliyse sadece raporlansın»*.

## Bu kapının işi — **var olanı** kilitlemek

Maliyet görünürlüğünün bugünkü tek dayanağı `③`'ün zinciri. O zincirin bir halkası
sessizce koparsa (ör. `InteractionLog` yazımından `llm_input_tokens` düşerse) hiçbir şey
kırmızı olmaz: cevaplar üretilmeye devam eder, yalnız **ne harcadığımız** kaybolur.

🅩 *Harcadığını göremeyen ajan tutumlu olmayı seçemez* — ve bu, sistemin kendisi için de
geçerlidir.
"""

from __future__ import annotations

import ast
import inspect
import pathlib

_KOK = pathlib.Path(__file__).resolve().parents[1]

#: 🔴 Zincirin **dört** halkası. Biri koparsa maliyet sessizce görünmez olur.
_HALKALAR = ("llm_model", "llm_input_tokens", "llm_output_tokens", "llm_latency_ms")


def test_OLCUM_TABANI_USTA_UC_FONKSIYON_VAR():
    """⊘ **Boş yeşil avı.** Üç fonksiyon da yoksa aşağıdaki yüklemler hiçbir şey ölçmez."""
    from app import llm

    for ad in ("reset_llm_usage", "record_llm_usage", "get_llm_usage"):
        assert callable(getattr(llm, ad, None)), f"⊘ ölçüm tabanı çöktü: `llm.{ad}` yok"


def test_KAYDEDICI_GIRDI_TOKENINI_ISTIYOR():
    """🔴 `record_llm_usage` **girdi** token'ını parametre olarak almalı — yalnız süre
    ölçen bir telemetri, **maliyeti** ölçmez. ㉗ *Birimsiz bir sayı bir ölçüm değildir.*"""
    from app.llm import record_llm_usage

    p = set(inspect.signature(record_llm_usage).parameters)
    assert {"input_tokens", "output_tokens"} <= p, (
        f"🔴 MALİYET AYAĞI DÜŞTÜ: `record_llm_usage` artık token almıyor: {sorted(p)}")


def test_ZINCIR_KOPMAMIS_DORT_HALKA_KALICI_YAZILIYOR():
    """🔴🔴 **ASIL KAPI.** Ölçülen token'ın **kalıcı** hâle geldiği tek yer
    `answer.py`'nin `InteractionLog` yazımı. Dört alandan biri düşerse maliyet
    görünürlüğü **sessizce** kaybolur — hiçbir cevap bozulmaz, yalnız kör kalırız.

    ⚠ ② `ast` ile aranıyor: kelime araması **bu dosyanın kendi satırlarını** sayardı.
    """
    agac = ast.parse((_KOK / "app" / "answer.py").read_text(encoding="utf-8"))
    yazilan = {n.arg for n in ast.walk(agac) if isinstance(n, ast.keyword) and n.arg}
    eksik = [h for h in _HALKALAR if h not in yazilan]
    assert not eksik, (
        f"🔴 MALİYET ZİNCİRİ KOPTU: `answer.py` artık {eksik} alanlarını YAZMIYOR. "
        "Token ölçülüyor olabilir ama hiçbir yerde kalmıyor — harcadığını göremeyen bir "
        "sistem tutumlu olmayı seçemez. 🅩")


def test_OLCUM_ISTEK_KAPSAMLI_SIFIRLANIYOR():
    """⚠ **Yarış kapanı.** Sayaç istek başına sıfırlanmazsa bir sonraki isteğin makbuzu
    **öncekinin** token'ını taşır — *doğru bir sayı, yanlış cümlede hâlâ yanlıştır* 🅫.
    """
    agac = ast.parse((_KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8"))
    cagrilar = {n.func.id for n in ast.walk(agac)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "reset_llm_usage" in cagrilar, (
        "🔴 `ask.py` artık `reset_llm_usage()` ÇAĞIRMIYOR — token sayacı istekler arasında "
        "taşar ve makbuz başka bir sorunun maliyetini gösterir.")


def test_TOPLAMA_KATMANI_YOKLUGU_BEYANLI():
    """⊙ **Borcun kendisi bir yüklem.** `②`+`③`'ün ortak boşluğu — *«sayı üretiliyor,
    okunamıyor»* — bugün **bilinçli** olarak açık: bir `/stats/maliyet` ucu, tüketicisi
    olmadığı için `§G`'nin **yetim uç** sınıfını elimizle üretirdi.

    Bu yüklem o kararı **kapıya** bağlar: bir gün maliyet ucu açılırsa **bu docstring**
    (ve `§G`'nin yetim-uç kapısı) birlikte gözden geçirilmelidir. 🆖 *Kova eklemek
    paydaya dokunmamalı* — ve bir borç, ödenmeden önce **adlandırılmış** olmalı 🆓.
    """
    yollar = list((_KOK / "app" / "routers").rglob("*.py"))
    assert yollar, "⊘ ölçüm tabanı: router dizini boş"
    ucu_olan = [p.name for p in yollar
                if "llm_input_tokens" in p.read_text(encoding="utf-8")]
    assert not ucu_olan, (
        f"🔴 MALİYET UCU AÇILMIŞ ({ucu_olan}) ama bu kapının gerekçesi hâlâ *«uç "
        "açılmaz»* diyor. İkisinden biri bayat: ya ucun bir FE tüketicisi var ve bu "
        "docstring güncellenmeli, ya da uç `§G`'nin yasakladığı yetim uçtur.")
