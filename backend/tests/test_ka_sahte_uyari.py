"""🔴🔴 `§KA` — *«ÇIPASIZ»* İDDİASI, TESLİM EDİLEN **FİŞE** DE BAKMALI.

## Ölçülen kusur (canlı curl, 2026-08-12)

    «cirumuz ne kadar»
      → cube=parti · measures=['toplam_ciro'] · **Ciro ₺137.588.350,68**
      → ve yanında: *«hiçbir ölçüye bağlayamadım — bu rapor bir VARSAYIMDIR»*

⊙ Cevap **doğru**, damga **yanlış**. Ve sebebi bir yazım hatası **değil**: typo'suz
*«ciromuz ne kadar»* da aynı damgayı alıyor (ölçüldü). Kök yapısal —

| katman | ne biliyor | *«ciromuz»* |
|---|---|---|
| `Niyet` (LLM'den **önce**, deterministik) | route'un sözlüğü | 🔴 tanımıyor → `olcu_adaylari=[]` |
| **garson** (fişi yazan) | katalog + dil | ✅ `toplam_ciro` |

Yüklem yalnız birinci satıra bakıyordu; **teslim edilen fişi hiç görmüyordu**.

> *Bir cevabın çıpasız olduğunu söylemeden önce, teslim ettiğin fişe bakmak gerekir.*

🔴 Ve bir yanlış uyarı, **doğru uyarıyı da tüketir**: kullanıcı ikinci kez okumaz
(`§101.1` — *yanlış-pozitifin bedeli, kapattığı kusurdan ağırdır*).

## Ayırt edici — yeni eşleştirici DEĞİL, var olan **ters yön**

`ters_yon.eslesen_terim_cikar` zaten tam bu soruyu cevaplıyor: *«fişteki bu ad,
kullanıcının hangi sözcüğünün karşılığı?»* — deterministik, **0 token**. Ölçüldü:

    «cirumuz ne kadar»     → {'soz': 'cirumuz', 'ad': 'toplam_ciro'}  → SUS
    «ciromuz ne kadar»     → {'soz': 'ciromuz', 'ad': 'toplam_ciro'}  → SUS
    «asdfgh qwerty»        → None (İKİ bilinmeyen → tekillik şartı düşer) → KONUŞ
    «hedefin neresindeyiz» → None                                         → KONUŞ

⚠ `«asdfgh qwerty»` korumasının **yapısal** olduğuna dikkat: kural *«tam bir bilinmeyen
+ tam bir hedef»* ister; anlamsız bir soruda bilinmeyen **iki**dir ve kural kendiliğinden
düşer. Koruma bir kelime listesine değil, **tekillik şartına** dayanıyor (`ADR-0008`).

## Bu kapı NEDEN iki yönlü

`§KA` bu depoda **üç kez** ölçüldü ve iki kez daralttığım koşul kendi düzeltmemi iptal
etti. Bu yüzden burada her iki yön de ölçülür: susması gereken sussun, **konuşması
gereken konuşsun**. *Tek yönü ölçülen bir uyarı, ya gürültüye ya sessizliğe kayar.*
"""

from __future__ import annotations

import types

from app import uyum


class _Niyet:
    """Çıpasız bir okuma — dördü de boş (yüklemin konuşma koşulu)."""

    olcu_adaylari: list = []
    kirilimlar: list = []
    donem_sayisi = 0
    filtreler: list = []


def _resp():
    return types.SimpleNamespace(note=None, trace=[])


# ── yüklem: saf yarı ───────────────────────────────────────────────────────────
def test_KANITSIZ_KONUSUR():
    """⊘ Ön koşul — kanıt yoksa davranış **birebir eskisi** (`KURAL B`)."""
    assert uyum.tanimadan_cevap_notu(_Niyet()) is not None
    assert uyum.tanimadan_cevap_notu(_Niyet(), kanit=None) is not None


def test_KANIT_VARSA_SUSAR():
    """🔴 Kusurun ta kendisi: fiş kullanıcının sözcüğünü karşılamışsa cevap çıpasız
    değildir."""
    assert uyum.tanimadan_cevap_notu(
        _Niyet(), kanit={"soz": "cirumuz", "ad": "toplam_ciro"}) is None


def test_NIYET_DOLUYSA_zaten_SUSAR():
    """Eski yol bozulmadı: ölçü adayı varsa kanıt aranmaz bile."""
    n = _Niyet()
    n.olcu_adaylari = [("parti", "toplam_ciro")]
    assert uyum.tanimadan_cevap_notu(n) is None


# ── iliştirme yarısı ───────────────────────────────────────────────────────────
def test_ILISTIRME_KURAL_B_argumansiz_cagri_AYNI():
    """🔴 `KURAL B`: `soru`/`cq`/`schema` verilmezse davranış **bayt bayt** eskisi."""
    r = _resp()
    assert uyum.uydurma_beyani(r, _Niyet()) is True
    assert "varsayımdır" in (r.note or "")
    assert any("§KA" in t for t in r.trace)


def test_ILISTIRME_KANIT_KANALI_SUSTURUR(monkeypatch):
    """Fiş verildiğinde ve ters yön bir eşleme bulduğunda beyan **iliştirilmez**."""
    monkeypatch.setattr("app.ters_yon.eslesen_terim_cikar",
                        lambda q, cq, s: {"soz": "cirumuz", "ad": "toplam_ciro"})
    r = _resp()
    assert uyum.uydurma_beyani(r, _Niyet(), soru="cirumuz ne kadar",
                               cq={"cube": "parti", "measures": ["toplam_ciro"]},
                               schema={"cubes": []}) is False
    assert not r.note, f"🔴 doğru cevaba yanlış damga kaldı: {r.note!r}"


def test_ILISTIRME_KANIT_YOKSA_KONUSUR(monkeypatch):
    """🔴🔴 **ÖTEKİ YÖN.** `«asdfgh qwerty»`: ters yön eşleme bulamaz → beyan **kalmalı**.

    Bu satır olmadan düzeltme, kapattığı kusurdan pahalı bir kör nokta açardı."""
    monkeypatch.setattr("app.ters_yon.eslesen_terim_cikar", lambda q, cq, s: None)
    r = _resp()
    assert uyum.uydurma_beyani(r, _Niyet(), soru="asdfgh qwerty",
                               cq={"cube": "oee", "measures": ["ort_oee"]},
                               schema={"cubes": []}) is True
    assert "varsayımdır" in (r.note or ""), (
        "🔴 anlamsız bir soruya verilen cevap artık beyansız — `§KA`'nın kurulma sebebi "
        "bu vakaydı (`CC-15`: «asdfgh qwerty» → 11 satırlık OEE raporu).")


def test_KANIT_HESABI_COKERSE_BEYAN_KALIR(monkeypatch):
    """⚠ Fail-**closed**: kanıt hesaplanamıyorsa susmak değil **konuşmak** doğrudur.

    *Bir kanıt kanalının çökmesi, kanıt varmış gibi davranmak için sebep değildir.*"""
    def _patla(q, cq, s):
        raise RuntimeError("ters yön çöktü")

    monkeypatch.setattr("app.ters_yon.eslesen_terim_cikar", _patla)
    r = _resp()
    assert uyum.uydurma_beyani(r, _Niyet(), soru="x", cq={"cube": "oee"},
                               schema={"cubes": []}) is True


def test_IKINCI_KANIT_KATALOG_ISABETI(monkeypatch):
    """🔴🔴 **ÖNCEKİ DÜZELTMEM YARIMDI — ölçüldü (2026-08-12).**

    `ters_yon` **tekillik** ister (tam bir bilinmeyen + tam bir hedef) ve yazım hatası
    sınıfını kapatır. Ama **fazladan sözcük** sınıfını kapatmaz:

        «dolar bazında ciro» → ₺137.588.350 · measures=[toplam_ciro]
                             → ve yanında *«hiçbir ÖLÇÜYE bağlayamadım»*  🔴

    `ciro` katalogda **var** ve bağlanan odur; temsil edilemeyen şey fazladan bir sözcük
    (`dolar`). Eksiklik doğru, **cümle yanlış**.

    ⊙ İkinci kanıt `partial_unknowns`'un **isabet** listesidir; yedi vakada ölçüldü ve
    `«asdfgh qwerty»` (hits=0) korunuyor.

    *Bir soru kataloğa değdiyse, cevabın «hiçbir şeye değmedim» demesi bir ölçüm değil
    bir dil sürçmesidir.*
    """
    monkeypatch.setattr("app.cube_router.partial_unknowns",
                        lambda q, s: (["dolar"], [({"name": "parti"}, "toplam_ciro")]))
    r = _resp()
    assert uyum.uydurma_beyani(r, _Niyet(), soru="dolar bazında ciro",
                               cq={"cube": "parti", "measures": ["toplam_ciro"]},
                               schema={"cubes": []}) is False
    assert not r.note, f"🔴 katalogda karşılığı olan soruya çıpasız damgası: {r.note!r}"


def test_ISABET_YOKSA_KONUSUR(monkeypatch):
    """🔴 Öteki yön — `«asdfgh qwerty»`: isabet yok, ters yön de yok → **beyan kalmalı**."""
    monkeypatch.setattr("app.cube_router.partial_unknowns",
                        lambda q, s: (["asdfgh", "qwerty"], []))
    monkeypatch.setattr("app.ters_yon.eslesen_terim_cikar", lambda q, cq, s: None)
    r = _resp()
    assert uyum.uydurma_beyani(r, _Niyet(), soru="asdfgh qwerty",
                               cq={"cube": "oee", "measures": ["ort_oee"]},
                               schema={"cubes": []}) is True
    assert "varsayımdır" in (r.note or "")


def test_KANIT_KANALI_GERCEKTEN_BAGLI():
    """🔴 Yazılıp bağlanmayan bir kanal, yazılmamış bir kanaldır (bu deponun 8 kez
    ölçtüğü desen).

    ⟳ **YÜKLEM YERE DEĞİL İDDİAYA BAĞLANDI (2026-08-12).** İlk yazımım `ask.py`'de
    `uydurma_beyani(` çağrısının yanında `soru=`/`cq=` arıyordu; büyüme kapısı gövdeyi
    `uyum.ka_beyani`'ye taşıtınca kapı kırıldı — oysa **kanal bozulmamıştı**, yalnız
    yeri değişmişti. *Bir kapıyı çağrının adresine bağlamak, ilk taşınmada onu
    kırar* (ders ㉕: kapıyı ADA değil GÖVDEYE bağla).

    Yeni yüklem iki halkayı da ölçer: `ask()` kanalı **çağırıyor** mu, ve kanal fişi
    **gerçekten taşıyor** mu.
    """
    import inspect
    import pathlib

    kaynak = (pathlib.Path(__file__).parent.parent / "app" / "routers"
              / "ask.py").read_text(encoding="utf-8")
    assert "ka_beyani(" in kaynak, (
        "🔴 `ask()` `§KA` kanalını hiç çağırmıyor → *«cirumuz»* sahte uyarısı geri gelir.")
    govde = inspect.getsource(uyum.ka_beyani)
    for alan in ("soru=", "cq=", "schema="):
        assert alan in govde, (
            f"🔴 kanal `{alan}` taşımıyor → kanıt hiç hesaplanmaz ve yüklem eski "
            "(sahte uyarı veren) hâline döner.")
    assert "resp.cube_query" in govde, (
        "🔴 fişin kaynağı `resp.cube_query` değil — teslim edilmeyen bir fişe bakan "
        "bir kanıt, kanıt değildir.")
