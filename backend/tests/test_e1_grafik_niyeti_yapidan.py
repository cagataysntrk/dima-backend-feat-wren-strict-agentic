r"""🔴🔴 `§E.1` — **GRAFİK KARARI NİYETİ ZATEN BİLİYOR — ÇÜNKÜ YAPIDAN OKUYOR.**

## Raporun açık bıraktığı tek delta — ve ölçüm onu KAPATTI

`§14.11 D7` (`2026-08-11_REKABET-VE-MIMARI-ANALIZI.md:4393`) `@antv/ava` ithalatını
reddederken **tek gerçek delta** diye şunu bıraktı:

> 🟢 *«`viz.recommend` imzası niyeti **hiç almıyor** — parametreleri `(result, units,
> lower_set, cube_query, non_additive, hedefler, paket)`, yani grafik kararı **yalnız veri
> şeklinden** doğuyor. Kanca **yalnız daraltıcı** yönde açılır (`TUR_KIYAS` → `partition`
> teklifi kapanır; `TUR_TREND` → tabloya daraltma yasak).»*

**İmza ölçümü doğru.** Ama önerilen iki daraltmanın **ikisi de zaten yürürlükte** —
ve bir **etiketten** değil, **yapıdan** türetilerek:

| raporun istediği daraltma | bugünkü hâli | nereden |
|---|---|---|
| `TUR_KIYAS` → `partition` **kapansın** | ✅ **kapalı** | `viz.py:497` — pay grafiği `len(measures)==1` ister; kıyas ailesi (`_gecen`·`_degisim_yuzde`) **her zaman** çok ölçülüdür |
| `TUR_TREND` → **tabloya daraltma yasak** | ✅ **yasak** | `viz.py:220` — `time_col and measures ≥1` → **`line`**; `table`'a düşmek için ya **ölçü 0** ya **boyut >2** olmalı |

⊘ **KARAR: kanca AÇILMAZ, gerekçesiyle.** Bir `niyet=` parametresi eklemek, bugün
**yapının söylediği** şeye **ikinci bir sahip** vermek olurdu (`KAT-1`) — ve iki sahip
bir gün ayrışır: kullanıcı *«trend»* der ama sonuçta zaman sütunu **yoktur**; o an
etiket `line` derken yapı `table` der. `ADR-0024`'ün *«grafik kararı deterministiktir»*
kuralı, kararı **veriye** bağladığı için çalışıyor — niyete bağlanan bir daraltma,
LLM'in seçtiği bir etiketi grafik kararına sokardı.

> ㊲ *Aynı işin iki satırı bir yedeklilik değil, bir ayrışma randevusudur.*

## Bu kapının işi — daraltmaları **DEĞİŞMEZ** yapmak

Rapor bir **niyet** beyan etti; kod onu **karşılıyor**. Aradaki tek eksik, karşıladığının
**kapıda** olmamasıydı: yukarıdaki iki satır bugün bir **yan etki**, yarın bir
**gerileme** olabilir. 🆇 *Bir raporun sayısını kapıya bağlamazsan, o sayı bir sonraki
turda bir hatıra olur.*
"""

from __future__ import annotations

import inspect

_TARIH, _KAT = "tarih", "musteri"
_OLCU = "toplam_ciro"


def _sonuc(kolonlar, satirlar):
    """⚠ ⑤ **ŞEKLİ ÖLÇ:** `rows` bir liste-listesi **değil**, `dict` listesidir —
    `result_shape.py:192` satırlara `r.get(kolon)` ile bakıyor. İlk yazımım liste
    veriyordu ve kapı `AttributeError` ile düştü: *kendi probumun beklentisi yanlıştı.*"""
    return {"columns": list(kolonlar),
            "rows": [dict(zip(kolonlar, s, strict=True)) for s in satirlar]}


def test_OLCUM_TABANI_RECOMMEND_CAGRILABILIYOR():
    """⊘ **Boş yeşil avı.** `recommend` düşerse aşağıdaki üç yüklem hiçbir şey ölçmez."""
    from app import viz

    spec = viz.recommend(_sonuc([_KAT, _OLCU],
                                [["A", 10.0], ["B", 20.0], ["C", 7.0], ["D", 3.0]]),
                         cube_query={"cube": "satis", "measures": [_OLCU],
                                     "dimensions": [_KAT]})
    # ⚠ ③ **PROBUN BEKLENTİSİ DE YANLIŞ OLABİLİR:** iki satırla çağırınca karar `bar`
    # değil **`cumle`** çıktı — az satırda grafik değil **cümle** basılıyor. Bu bir kusur
    # değil bir tasarım; kapı onu öğrenip dört satıra geçti.
    assert spec and spec.get("kind") == "bar", f"⊘ ölçüm tabanı çöktü: {spec}"


def test_KIYASTA_PAY_GRAFIGI_ONERILMIYOR():
    """🔴🔴 **ASIL KAPI — raporun birinci daraltması.** Dönemsel kıyasta pay grafiği
    **anlamsızdır** (*«bu ayın payı»* ile *«geçen ayın payı»* aynı pastada olamaz) ve
    bugün **yapı** bunu kapatıyor: kıyas ailesi her zaman **çok ölçülüdür**.

    ⚠ Bir gün pay grafiği çok ölçüye açılırsa bu yüklem kırmızı olur — ve **olmalıdır**.
    """
    from app import viz

    spec = viz.recommend(
        _sonuc([_KAT, _OLCU, f"{_OLCU}_gecen", f"{_OLCU}_degisim_yuzde"],
               [["A", 10.0, 8.0, 25.0], ["B", 20.0, 25.0, -20.0]]),
        cube_query={"cube": "satis", "compare": "yoy", "dimensions": [_KAT],
                    "measures": [_OLCU, f"{_OLCU}_gecen", f"{_OLCU}_degisim_yuzde"]})
    assert spec, "⊘ ölçüm tabanı: kıyas sonucu için spec üretilmedi"
    assert spec.get("partition") is not True, (
        "🔴 KIYASTA PAY GRAFİĞİ ÖNERİLİYOR — `§14.11 D7`'nin birinci daraltması düştü. "
        f"alternatives={spec.get('alternatives')!r}")


def test_ZAMAN_EKSENI_VARSA_TABLOYA_DARALTILMIYOR():
    """🔴🔴 **ASIL KAPI — raporun ikinci daraltması.** Zaman sütunu + en az bir ölçü
    varsa karar **`line`**'dır; tabloya düşmek bir trendi **görünmez** yapardı."""
    from app import viz

    spec = viz.recommend(
        _sonuc([_TARIH, _OLCU], [["2026-01", 10.0], ["2026-02", 14.0],
                                 ["2026-03", 9.0]]),
        cube_query={"cube": "satis", "measures": [_OLCU], "dimensions": [_TARIH]})
    assert spec, "⊘ ölçüm tabanı: zaman serisi için spec üretilmedi"
    assert spec.get("kind") == "line", (
        f"🔴 ZAMAN SERİSİ TABLOYA DARALDI: kind={spec.get('kind')!r} — "
        "`§14.11 D7`'nin ikinci daraltması düştü.")


def test_GRAFIK_KARARININ_TEK_SAHIBI_YAPIDIR():
    """🔴 `KAT-1` + `ADR-0024`. `recommend()` bir **niyet etiketi** almaz; kararı
    `result` + `cube_query`'den, yani **veriden** türetir.

    ⚠ Bu yüklem bir *«eklemeyin»* yasağı değil, bir **bilinçli karar kaydıdır**: kanca
    eklenecekse `ADR-0024` ve bu docstring **birlikte** güncellenmelidir. *Bir kararı
    kapıya yazmak, onu bir sonraki turda yeniden tartışmaktan ucuzdur.*
    """
    from app import viz

    parametreler = set(inspect.signature(viz.recommend).parameters)
    assert "niyet" not in parametreler and "tur" not in parametreler, (
        f"🔴 `recommend()` artık bir NİYET ETİKETİ alıyor: {sorted(parametreler)}. "
        "Grafik kararının ikinci bir sahibi oldu — `ADR-0024`'ün determinizmi ve bu "
        "kapının gerekçesi birlikte gözden geçirilmeli.")
    assert {"result", "cube_query"} <= parametreler, (
        f"🔴 kararın YAPISAL girdileri kayboldu: {sorted(parametreler)}")


def test_NIYET_TURLERI_GERCEKTEN_URETILIYOR(schema):
    """⊙ Raporun *«6 kapalı tür **zaten var ve bağlı**»* iddiasının **payda kontrolü**.

    🆌 *Bir motoru doğru kurmak onu çalıştırmaz* — türler bir sabit listesi olarak
    dursaydı `bicim.oneri_kotasi` onları **hiç görmezdi**. Üretici zincir:
    `niyet.coz(soru, schema).turler` → `bicim.oneri_kotasi` (`answer.py:872`).
    """
    from app.bicim import oneri_kotasi
    from app.niyet import coz

    n = coz("bu yıl müşteriye göre ciro", schema)
    turler = getattr(n, "turler", None)
    assert turler, f"🔴 `Niyet.turler` boş ya da yok — tür ÜRETİLMİYOR: {turler!r}"
    assert oneri_kotasi(turler) is not None, (
        f"🔴 üretilen türleri `bicim` TÜKETEMİYOR: {turler!r}")
