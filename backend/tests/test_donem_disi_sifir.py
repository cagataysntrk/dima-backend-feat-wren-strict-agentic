"""🔴🔴 `§SD` — **SIFIR BİR CEVAPTIR, «VERİ YOK» BİR YOKLUKTUR; SAYIM İKİSİNİ BİRLEŞTİRİR.**

## Ölçülen kusur (curl `N` turu, 2026-08-10) — ve onu gizleyen kardeş

    «bu ay kaç parti üretildi»   → {"parti_sayisi": 0}    beyan: YOK      🔴
    «geçen ay ortalama oee»      → {"ort_oee": null}      beyan: TAM ✅

İki soru, aynı veri ufku (`30.06.2026`), aynı dönem-dışı pencere — **farklı** davranış.
Fark ölçünün türünde: `AVG` boş kümede **NULL** döner ve `bos_mu` NULL'u görür; `COUNT`
boş kümede **0** döner ve sıfır, bir yokluk gibi **görünmez**.

⊙ *Bir dedektörün çalıştığı vaka, çalışmadığı vakayı gizleyebilir* — bu dosyanın
kardeşi (`bos_mu`) aynı cümleyi kendi şerhinde zaten yazmıştı.

🔴 Ve sıfırı *«boş»* saymak bir çözüm **değildir**: gerçek bir sıfır (o ay hakikaten
üretim yoksa) meşru bir cevaptır ve onu susturmak yeni bir sessiz-yanlış olurdu. Bu
yüzden yüklem **sonuca değil KAPSAMA** bakar.
"""

from app import veri_araligi as va

_SEMA = {"cubes": [{"name": "parti", "time_dimensions": ["tarih"]}]}


class _Svc:
    """Aralık ölçümünü sabitler — sınanan şey karşılaştırma, ölçüm değil."""


def _not(cq, aralik=("2024-01-01", "2026-06-30"), monkeypatch=None):
    monkeypatch.setattr(va, "aralik", lambda s, c: aralik)
    return va.donem_disi_notu(_Svc(), cq, _SEMA)


def _cq(bas=None, son=None):
    f = []
    if bas:
        f.append({"dimension": "tarih", "operator": "gte", "value": bas})
    if son:
        f.append({"dimension": "tarih", "operator": "lte", "value": son})
    return {"cube": "parti", "measures": ["parti_sayisi"], "filters": f}


def test_TAMAMEN_ILERIDEKI_DONEM_BEYAN_EDILIR(monkeypatch):
    """🔴 **Kapının kalbi** — ölçülen soru: *«bu ay kaç parti üretildi»* (Ağustos 2026)."""
    n = _not(_cq("2026-08-01", "2026-08-31"), monkeypatch=monkeypatch)
    assert n and "tamamen dışında" in n
    assert "veri sınırıdır" in n


def test_TAMAMEN_GERIDEKI_DONEM_DE_BEYAN_EDILIR(monkeypatch):
    """Ufuk iki yönlüdür: verinin **başlangıcından** önceki bir pencere de dışarıdadır."""
    n = _not(_cq("2020-01-01", "2020-12-31"), monkeypatch=monkeypatch)
    assert n and "tamamen dışında" in n


def test_KISMEN_KESISEN_DONEMDE_SUSAR(monkeypatch):
    """🔴🔴 **Kapının en önemli satırı: fazla ileri gitmemek.**

    Pencere aralığa **değiyorsa** dönen sayı gerçek bir sayıdır. Orada da beyan yazmak,
    doğru bir cevabı kusurlu ilan etmek olurdu (`§101.1`)."""
    assert _not(_cq("2026-01-01", "2026-12-31"), monkeypatch=monkeypatch) is None


def test_TAM_ICERIDEKI_DONEMDE_SUSAR(monkeypatch):
    assert _not(_cq("2025-01-01", "2025-12-31"), monkeypatch=monkeypatch) is None


def test_ACIK_UCLU_PENCERE_SONSUZA_UZANIR(monkeypatch):
    """`gte 2026-01-01` (üst uç yok) veriye değer — açık uç bir dışlama değildir."""
    assert _not(_cq("2026-01-01"), monkeypatch=monkeypatch) is None
    assert _not(_cq("2027-01-01"), monkeypatch=monkeypatch) is not None


def test_DONEM_FILTRESI_YOKSA_SUSAR(monkeypatch):
    """Pencere yoksa karşılaştıracak bir şey yok — `KURAL B`."""
    assert _not(_cq(), monkeypatch=monkeypatch) is None


def test_ARALIK_OLCULEMEZSE_SUSAR(monkeypatch):
    """*Bir ölçümün susması, ölçtüğü şeyin yokluğu değildir.*"""
    assert _not(_cq("2026-08-01", "2026-08-31"), aralik=None, monkeypatch=monkeypatch) is None


def test_BILINMEYEN_KUPTE_SUSAR(monkeypatch):
    monkeypatch.setattr(va, "aralik", lambda s, c: ("2024-01-01", "2026-06-30"))
    assert va.donem_disi_notu(_Svc(), {"cube": "yok", "filters": []}, _SEMA) is None


def test_BEYAN_GERCEK_ARALIGI_YAZAR(monkeypatch):
    """Beyan bir *«veri yok»* değildir: elde **ne olduğunu** adıyla söyler."""
    n = _not(_cq("2026-08-01", "2026-08-31"), monkeypatch=monkeypatch)
    assert "30.06.2026" in n and "01.01.2024" in n


# --- `§KY` · KIYASIN YARISI BOŞKEN SESSİZ KALINMAZ -----------------------------------

def test_KIYAS_YARIM_BEYAN_EDILIR():
    """🔴🔴 `§KY` — ölçüldü (curl `X` turu, 5 turluk thread'in 4. turu):
    *«geçen yıla göre nasıl»* → `toplam_ciro` dolu, `toplam_ciro_gecen` **tümü null**,
    ve **not YOK**. Okuyucu boşluğu kendi varsayımıyla doldurur: *«geçen yıl sıfır
    mıydı?»*

    `§SD-2` burada haklı olarak susar (sonuç boş değil); boş olan **kıyasın öteki
    yarısıdır** — ayrı bir yokluk biçimi.

    *Bir yokluğu tanımayan kapı, onu yokluk saymaz — var saymaz da; hiç görmez.*"""
    from app import veri_araligi as va

    res = {"columns": ["kumas", "toplam_ciro", "toplam_ciro_gecen"],
           "rows": [{"kumas": "A", "toplam_ciro": 1, "toplam_ciro_gecen": None},
                    {"kumas": "B", "toplam_ciro": 2, "toplam_ciro_gecen": None}],
           "row_count": 2}
    n = va.kiyas_yarim_notu(res)
    assert n and "Kıyas kurulamadı" in n


def test_KISMEN_DOLU_KIYAS_BIR_KUSUR_DEGIL():
    """⚠ Yüklem **kanıtlı**: bir kısmı doluysa bu bir kusur değil bir **olgudur** (o
    segment geçen yıl yoktu) ve satırın kendisi bunu zaten gösterir. Konuşmak, bir
    olguyu bir arıza gibi sunmak olurdu (`§101.1`)."""
    from app import veri_araligi as va

    res = {"columns": ["kumas", "toplam_ciro", "toplam_ciro_gecen"],
           "rows": [{"kumas": "A", "toplam_ciro": 1, "toplam_ciro_gecen": 9},
                    {"kumas": "B", "toplam_ciro": 2, "toplam_ciro_gecen": None}],
           "row_count": 2}
    assert va.kiyas_yarim_notu(res) is None


def test_KIYASSIZ_SONUCA_KARISMAZ():
    """`KURAL B` — `_gecen` kolonu yoksa yol bayt bayt bugünküdür."""
    from app import veri_araligi as va

    assert va.kiyas_yarim_notu({"columns": ["a"], "rows": [{"a": None}]}) is None
    assert va.kiyas_yarim_notu(None) is None
