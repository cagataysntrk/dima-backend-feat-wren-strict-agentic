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


# --- CANLI KULLANICI TURUNUN İKİNCİ DALGASI (denetçi C, `e22b2b9` sonrası) --------
#
# Pivot sessiz-yanlışı KAPANDI ve kullanıcı bunu **elle doğruladı**: aynı `makine × ay`
# tablosunu iki kez sordu, ikisinde de `%116,7` geldi ve Ocak sütununu kendisi toplayıp
# `43.869` ile birebir eşleşti. Ama aynı tur ÜÇ yeni kusur çıkardı — üçü de bu turda
# yazılan METİNDE.

META_YARI = {"name": "cari", "semi_additive": ["bakiye"],
             "measure_expressions": {"bakiye": "SUM(bakiye)"}}


def test_OZET_METNINDE_MARKDOWN_YOK():
    """🔴 `OutputInsight` `summary`'yi **düz metin** basar. Kullanıcı ekranda
    `**dönem toplamları**` yıldızlarını **harfi harfine** gördü. Bir yorum satırının
    içinde biçimlendirme kaçağı, sayının kendisine olan güveni de aşındırır."""
    y = interpret(PIVOT, CQ, cube_meta=META_TOPLANABILIR)
    for f in y["facts"]:
        assert "**" not in f["text"] and "`" not in f["text"], \
            f"olgu metninde markdown kaçağı: {f['text']!r}"
    assert "**" not in y["summary"] and "`" not in y["summary"], \
        f"özet metninde markdown kaçağı: {y['summary']!r}"


def test_TREND_YAZILMAMA_GEREKCESI_GORUNUMUN_SINIRINI_anlatir():
    """🔴 **Kullanıcı iki ekranı yan yana gördü ve haklı olarak isyan etti.**

    Kırılımsız ekran: *"fire_orani_yuzde %3,1 azaldı — iyileşti"*.
    Kırılımlı ekran (aynı ölçü): *"trend YAZILMADI: … matematiksel olarak TANIMSIZ"*.
    > *"İkisi aynı anda doğru olamaz — hangisine inanacağım?"*

    Mantık doğruydu (kırılımsız seride toplama YOK, oran trendi meşru) ama **cümle
    yanlıştı**: tanımsız olan trend değil, **kırılım boyunca toplama**. Gerekçe artık
    bunu söyler ve kullanıcıyı **çalışan görünüme** yönlendirir."""
    p = {**PIVOT, "columns": ["ay", "makine", "fire_orani_yuzde"],
         "rows": [{**r, "fire_orani_yuzde": r["fire_kg"]} for r in PIVOT["rows"]]}
    y = interpret(p, {**CQ, "measures": ["fire_orani_yuzde"]}, cube_meta=META_ORAN)
    s = _sekil(y)
    assert s, "şekil notu yok"
    assert "TOPLANAMAZ" in s["text"], f"gerekçe TOPLAMA sınırını anlatmıyor: {s['text']}"
    assert "kırılımsız" in s["text"].lower(), \
        f"kullanıcı ÇALIŞAN görünüme yönlendirilmiyor: {s['text']}"
    assert "tanımsız" not in s["text"].lower(), (
        "gerekçe hâlâ trendi 'tanımsız' ilan ediyor — kırılımsız ekranda AYNI ölçü için "
        f"trend yazılıyor, bu bir çelişkidir: {s['text']}")


def test_YARI_TOPLANABILIR_OLCUNUN_TRENDI_YAZILIR():
    """🔴 Bütünlük denetiminin bulgusu: bir **stok/bakiye** ölçüsü müşteriler arasında
    **pekâlâ toplanır**; toplanamadığı eksen **zamandır**. Katalogda yedi tane var
    (`bakiye` · `acik_bakiye` · `acik_borc` · `net_bakiye` · `net_miktar` · `stok_deger` ·
    `vadesi_gecen`) ve ilk düzeltme hepsinin trendini **haksız yere** susturmuştu."""
    p = {"columns": ["ay", "cari", "bakiye"], "row_count": 4,
         "rows": [{"ay": "2026-01", "cari": "A", "bakiye": 100},
                  {"ay": "2026-01", "cari": "B", "bakiye": 200},
                  {"ay": "2026-06", "cari": "A", "bakiye": 400},
                  {"ay": "2026-06", "cari": "B", "bakiye": 200}]}
    cq = {"cube": "cari", "measures": ["bakiye"], "dimensions": ["cari"],
          "timeDimensions": [{"dimension": "ay"}]}
    t = _trend(interpret(p, cq, cube_meta=META_YARI))
    assert t is not None, "yarı-toplanabilir ölçünün dönem trendi HAKSIZ yere susturuldu"
    assert t["pct"] == 100.0, f"300 → 600 beklenirdi, %{t['pct']} geldi"


def test_TOPLANABILIRLIGI_BILINMEYEN_OLCU_FAIL_CLOSED():
    """`cube_meta` yoksa (Discovery/LLM yolu — baskın yol) sınıf **bilinmiyor**dur.
    Trend tarafında doğru cevap **susmaktır**: yanlış bir yüzde, hiç yüzdeden kötüdür."""
    p = {**PIVOT, "columns": ["ay", "makine", "gizemli_olcu"],
         "rows": [{**r, "gizemli_olcu": r["fire_kg"]} for r in PIVOT["rows"]]}
    y = interpret(p, {**CQ, "measures": ["gizemli_olcu"]}, cube_meta=None)
    assert _trend(y) is None, "toplanabilirliği BİLİNMEYEN ölçüde trend yayımlandı"
    assert "hesaplanamaz" in (_sekil(y) or {}).get("text", ""), "gerekçe yazılmamış"


def test_TEK_KALEMDE_TOPLAMIN_PAYI_YAZILMAZ():
    """*"toplamın %100,0'i"* bilgi taşımaz. Kullanıcı: *"boş laf — tek yıl tabii ki %100."*
    Doldurma cümleler, hesaplanmış cümlelere olan güveni de aşındırır.

    ⟳ **SÖZLEŞME GÜÇLENDİ (2026-08-12) — ve bu testin İDDİASI DEĞİŞMEDİ, KAPSAMI BÜYÜDÜ.**

    Bu test *«tek kalemde pay yazılmaz»* diyordu ve `top` olgusunun metnini ölçüyordu.
    `§18.5`'te aynı gerekçe **başlığa** da uygulandı: tek kalemde *«en yüksek»* demek de
    yapılmamış bir kıyası ima eder. Artık tek grup `top` değil **`single`** üretiyor.

    ⚠ Test **gevşetilmedi**: eski yüklem (*«toplamın» geçmesin*) aynen duruyor, üstüne
    üstünlük iddiasının da yokluğu ve **varlık adının korunduğu** ölçülüyor.
    *Bir sözleşme güçlendiğinde, onu ölçen kapı daralmaz — genişler.*
    """
    tek = {"columns": ["yil", "fire_kg"], "row_count": 1,
           "rows": [{"yil": "2026", "fire_kg": 454477}]}
    y = interpret(tek, {"cube": "fire", "measures": ["fire_kg"], "dimensions": ["yil"]},
                  cube_meta=META_TOPLANABILIR)
    ust = next(f for f in y["facts"] if f["type"] in ("top", "single"))
    assert "toplamın" not in ust["text"], \
        f"tek kalemde 'toplamın %100'i' basıldı: {ust['text']}"
    assert "En yüksek" not in ust["text"], \
        f"tek kalemde ÜSTÜNLÜK iddia edildi (§18.5): {ust['text']}"
    assert "2026" in ust["text"], f"varlık adı düştü: {ust['text']}"


def test_TOPLANAMAYAN_OLCUDE_SIRALAMA_TOPLAMA_YAPMAZ():
    """İlk düzeltme yalnız **payı** susturmuştu; gövde hâlâ topluyordu. Bir dim değeri
    için birden fazla satır varsa *"En yüksek makine: RAM-1 (…)"* bir **oranlar
    toplamıdır** — payı susturulmuş ama sayının kendisi yanlış."""
    cok = {"columns": ["makine", "renk", "fire_orani_yuzde"], "row_count": 4,
           "rows": [{"makine": "RAM-1", "renk": "kırmızı", "fire_orani_yuzde": 20},
                    {"makine": "RAM-1", "renk": "mavi", "fire_orani_yuzde": 20},
                    {"makine": "RAM-2", "renk": "kırmızı", "fire_orani_yuzde": 30},
                    {"makine": "RAM-2", "renk": "mavi", "fire_orani_yuzde": 5}]}
    y = interpret(cok, {"cube": "fire", "measures": ["fire_orani_yuzde"],
                        "dimensions": ["makine", "renk"]}, cube_meta=META_ORAN)
    assert "**" not in y["summary"] and "`" not in y["summary"], \
        f"sıralama gerekçesinde markdown kaçağı: {y['summary']!r}"
    assert not [f for f in y["facts"] if f["type"] == "top"], (
        "toplanamayan ölçüde sıralama yazıldı — değerler TOPLANMIŞ olurdu "
        f"(RAM-1 40 · RAM-2 35 gibi): {y['summary']}")
    assert "TOPLANAMAZ" in y["summary"], f"neden yazılmadığı söylenmiyor: {y['summary']}"


def test_BILINMIYOR_ASIMETRISI_iki_yonlu_KILITLI():
    """🔴 **Bilinçli asimetri — kapı iki yönü de tutar.**

    `cube_meta=None` (Discovery/LLM yolu, **baskın yol**) sınıfı `BILINMIYOR` yapar:
    · **trend** tarafında **FAIL-CLOSED** — orada kanıtlanmış bir sessiz-yanlış vardı;
    · **sıralama/pay** tarafında **toplanabilir sayılır** — fail-close etmek kapsamı
      geniş biçimde kırpardı (bu tur tam olarak bunu yaptı ve `test_top_n_share_of_total`
      kırmızı verdi), üstelik asıl riskli sınıf ad kalıbıyla zaten yakalanıyor.

    Bu test kaldırılırsa asimetri sessizce bir yöne kayar: ya kapsam kırpılır, ya
    sessiz-yanlış geri döner."""
    # (a) SIRALAMA: metadata yok ama pay YAZILIR
    kat = {"columns": ["cari", "tutar"], "row_count": 2,
           "rows": [{"cari": "A", "tutar": 700}, {"cari": "B", "tutar": 300}]}
    y = interpret(kat, {"measures": ["tutar"], "dimensions": ["cari"]}, cube_meta=None)
    ust = next(f for f in y["facts"] if f["type"] == "top")
    assert "toplamın %70" in ust["text"], (
        f"metadata yokken pay SUSTURULDU — kapsam sessizce kırpıldı: {ust['text']}")

    # (b) TREND: metadata yok, pivot → YAZILMAZ
    p = {**PIVOT, "columns": ["ay", "makine", "tutar"],
         "rows": [{**r, "tutar": r["fire_kg"]} for r in PIVOT["rows"]]}
    y2 = interpret(p, {**CQ, "measures": ["tutar"]}, cube_meta=None)
    assert _trend(y2) is None, \
        "metadata yokken PİVOT trendi yayımlandı — kanıtlanmış sessiz-yanlış geri döndü"

    # (c) Ad kalıbı hâlâ riskli sınıfı yakalıyor (metadata olmasa bile)
    oran = {"columns": ["makine", "fire_orani_yuzde"], "row_count": 2,
            "rows": [{"makine": "RAM-1", "fire_orani_yuzde": 21.9},
                     {"makine": "RAM-2", "fire_orani_yuzde": 17.4}]}
    y3 = interpret(oran, {"measures": ["fire_orani_yuzde"], "dimensions": ["makine"]},
                   cube_meta=None)
    ust3 = next(f for f in y3["facts"] if f["type"] == "top")
    assert "toplamın" not in ust3["text"], (
        "oran ADI metadata'sız da yakalanmalıydı (ad kalıbı: _yuzde) — "
        f"yüzdeler toplandı: {ust3['text']}")
