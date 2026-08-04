"""🔴 CANLI KULLANICI TURUNDA BULUNAN SESSİZ-YANLIŞ — pivot trendi.

## Ne oldu

Gerçek bir kullanıcı gibi davranan bir denetçi turu (2026-08-04), `makine × ay` kırılımlı
bir fire raporunda **aynı veri için üç ayrı yüzde** gördü:

    tur 3  : "%88,1 arttı — olumsuz"
    tur 5  : "%72,3 azaldı — İYİLEŞTİ"
    tur 6  : "%98,3 arttı"

Kullanıcının kendi cümlesi:
> *"Aynı veriye üç farklı yüzde. Sarı satırı okumayı bıraktım."*
> *"Veriyi çekmek için kullanırım, ama yorumunu müdürler toplantısında ekrana yansıtmam —
> çünkü yanlış yüzdeyi bir kez okursam, o toplantıda benim itibarım gider."*

## Kök neden

`_series_facts` **satır başına** bir nokta alıyordu. `makine × ay` pivotunda aynı ay
onlarca kez tekrarlanır; sıralamadan sonra *"ilk"* ve *"son"* **iki farklı makinenin**
değeridir. Yani rapor edilen trend, hiçbir zaman bir dönem trendi değildi.

Kod pivot olduğunu **zaten fark ediyordu** (`entity` değişkeni) ama yalnız bir "şekil"
notu ekleyip yanlış sayıyı **yine de yayımlıyordu**.

## İki katmanlı düzeltme

1. **Dönem trendi dönem toplamları üzerinden** hesaplanır (`_donem_bazinda_topla`).
2. Ölçü **toplanamıyorsa** (oran/ortalama) trend **hiç yazılmaz** — ve bu kural
   `contribution.ayristirilabilir_mi`'nin, yani ZATEN VAR OLAN tek sahibin, çağrılmasıyla
   gelir. `interpret` onu tanımıyordu: katkı yolu *"oran → katkı payı tanımsız"* diye
   dürüstçe reddederken yorum satırı aynı ölçü için hem pay hem trend basıyordu.
   **Aynı kuralın iki sahibi / kimlik asimetrisi** — bu deponun 1 numaralı kusur sınıfı.

MIMARI §5: *"kalibre edilmemiş bir sayı bir güven değil bir süstür."* Yanlış bir yüzde
süs bile değildir; **zarardır**.
"""

from __future__ import annotations

from app.interpret import interpret

#: `makine × ay` pivotu. DÖNEM TOPLAMLARI: 2026-01 → 300, 2026-06 → 600 ⇒ **+%100**.
#: Ham satırlarda ilk→son ise RAM-1(100) → RAM-3(100) ⇒ %0 gibi görünür; sıralama
#: değişirse başka bir sayı çıkar. Kusurun tam şekli budur.
PIVOT = {
    "columns": ["ay", "makine", "fire_kg"],
    "row_count": 6,
    "rows": [
        {"ay": "2026-01", "makine": "RAM-1", "fire_kg": 100},
        {"ay": "2026-01", "makine": "RAM-2", "fire_kg": 100},
        {"ay": "2026-01", "makine": "RAM-3", "fire_kg": 100},
        {"ay": "2026-06", "makine": "RAM-1", "fire_kg": 400},
        {"ay": "2026-06", "makine": "RAM-2", "fire_kg": 100},
        {"ay": "2026-06", "makine": "RAM-3", "fire_kg": 100},
    ],
}
CQ = {"cube": "fire", "measures": ["fire_kg"],
      "dimensions": ["makine"], "timeDimensions": [{"dimension": "ay"}]}
META_TOPLANABILIR = {"name": "fire", "measure_expressions": {"fire_kg": "SUM(fire_kg)"}}
META_ORAN = {"name": "fire", "non_additive": ["fire_orani_yuzde"],
             "measure_expressions": {"fire_orani_yuzde": "SUM(a)/SUM(b)*100"}}


def _trend(yorum):
    return next((f for f in (yorum or {}).get("facts", []) if f.get("type") == "trend"), None)


def _sekil(yorum):
    return next((f for f in (yorum or {}).get("facts", []) if f.get("type") == "shape"), None)


def test_PIVOT_TRENDI_DONEM_TOPLAMI_uzerinden():
    """🔴 KAPI. Dönem toplamları 300 → 600 ⇒ **+%100**. Ham satır ilk→son'u DEĞİL."""
    t = _trend(interpret(PIVOT, CQ, cube_meta=META_TOPLANABILIR))
    assert t is not None, "toplanabilir ölçüde dönem trendi yazılmalıydı"
    assert t["pct"] == 100.0, (
        f"pivot trendi dönem toplamlarından gelmiyor: %{t['pct']} — ham satırların "
        "ilk→son'u iki FARKLI MAKİNEYİ kıyaslar ve her sıralamada başka sayı verir")
    assert "300" in t["text"] and "600" in t["text"], \
        f"trend metni dönem TOPLAMLARINI göstermiyor: {t['text']}"


def test_PIVOT_ORAN_OLCUSUNDE_TREND_HIC_YAZILMAZ():
    """Toplanamayan ölçüde susmak, yanlış yüzdeden iyidir — ve NEDENİ yazılır."""
    p = {**PIVOT, "columns": ["ay", "makine", "fire_orani_yuzde"],
         "rows": [{**r, "fire_orani_yuzde": r["fire_kg"]} for r in PIVOT["rows"]]}
    cq = {**CQ, "measures": ["fire_orani_yuzde"]}
    y = interpret(p, cq, cube_meta=META_ORAN)
    assert _trend(y) is None, "oran ölçüsünde dönem trendi YAZILDI — sayı tanımsız"
    s = _sekil(y)
    assert s and "YAZILMADI" in s["text"], \
        f"trendin neden yazılmadığı SÖYLENMİYOR (sessiz kırpma): {s}"


def test_TEK_EKSENLI_ZAMAN_SERISI_DEGISMEDI():
    """KURAL A — kırılımsız zaman serisi bugünkü davranışını AYNEN korur."""
    duz = {"columns": ["ay", "fire_kg"], "row_count": 2,
           "rows": [{"ay": "2026-01", "fire_kg": 300}, {"ay": "2026-06", "fire_kg": 600}]}
    t = _trend(interpret(duz, {"cube": "fire", "measures": ["fire_kg"],
                               "timeDimensions": [{"dimension": "ay"}]},
                         cube_meta=META_TOPLANABILIR))
    assert t and t["pct"] == 100.0


def test_ORAN_OLCUSUNDE_TOPLAMIN_PAYI_YAZILMAZ():
    """*"toplamın %10,2'si"* bir YÜZDE ölçüsünde anlamsızdır — yüzdeler toplanmaz.
    (Canlı turda ölçüldü: `fire_orani_yuzde` için tam bu cümle basılıyordu.)"""
    kat = {"columns": ["makine", "fire_orani_yuzde"], "row_count": 2,
           "rows": [{"makine": "RAM-1", "fire_orani_yuzde": 21.9},
                    {"makine": "RAM-2", "fire_orani_yuzde": 17.4}]}
    y = interpret(kat, {"cube": "fire", "measures": ["fire_orani_yuzde"],
                        "dimensions": ["makine"]}, cube_meta=META_ORAN)
    ust = next(f for f in y["facts"] if f["type"] == "top")
    assert "toplamın" not in ust["text"], \
        f"oran ölçüsünde 'toplamın %X'i' basıldı — yüzdeler toplanmaz: {ust['text']}"

    kg = {"columns": ["makine", "fire_kg"], "row_count": 2,
          "rows": [{"makine": "RAM-1", "fire_kg": 300}, {"makine": "RAM-2", "fire_kg": 100}]}
    y2 = interpret(kg, {"cube": "fire", "measures": ["fire_kg"], "dimensions": ["makine"]},
                   cube_meta=META_TOPLANABILIR)
    ust2 = next(f for f in y2["facts"] if f["type"] == "top")
    assert "toplamın %75" in ust2["text"], \
        f"toplanabilir ölçüde pay KAYBOLDU (aşırı düzeltme): {ust2['text']}"


def test_KURAL_TEK_SAHIPTE_kalir():
    """`interpret` toplanabilirliği KENDİ bilmez — `contribution`'ın sahibine sorar.
    İkinci bir kopya, iki mekanizmanın aynı ölçü için farklı şey söylemesi demektir
    (bu deponun 1 numaralı kusuru; canlı turda tam olarak bu görüldü)."""
    import inspect

    from app import interpret as mod

    src = inspect.getsource(mod)
    assert "ayristirilabilir_mi" in src, "toplanabilirlik sahibine SORULMUYOR"
    for kopya in ("non_additive", "semi_additive", 'AVG('):
        assert kopya not in src, (
            f"toplanabilirlik kuralı `interpret.py`'ye KOPYALANMIŞ ({kopya!r}) — "
            "tek sahip `contribution.ayristirilabilir_mi`")
