r"""🔴 `FAZ 1` — **«EMİN MİYİM?» SORUSUNUN TEK SAHİBİ** (`KAT-1`).

Dört yer aynı soruyu kendi aritmetiğiyle soruyordu. Bu kapı ① sahipliğin **tek**
kaldığını, ② her çağıranın davranışının **bayt bayt** korunduğunu kilitler.

## Planın iki maddesi ölçümle düzeltildi — ikisi de burada

**`④` (*«`:1190`'ı 0–1'e normalize et»*) ve `⑤` (*«normalize edilmemiş skor →
`ValueError`»*) UYGULANMADI.** `_longest_syn_hit` bir **harf sayısıdır**; `[0,1]`'e
sıkıştırmak sabit bir payda **uydurmayı** gerektirir 🅭 ve o payda aşıldığı gün
(*33 harflik bir eşanlamlı*) `ValueError` **küp seçimini çökertir**. Yani `⑤` bir
güvenlik kapısı değil, **kendi ürettiği riskin** bekçisi olurdu.

Yerine sözleşme **birim-bağımsız**dır: skorlar yalnız *tek çağrı içinde*
kıyaslanabilir olmalıdır. Kapı bunu `④'` ile sınar — harf birimi **korunuyor mu**.

⚠ Ve planın *«beş çağıran»*ı **dörttür** — ㉙ ile sayıldı ⑲.
"""

from __future__ import annotations

import ast
import math
import pathlib

from app.emin_miyim import Karar, karar

_APP = pathlib.Path(__file__).resolve().parents[1] / "app"


# ── ① TEK SAHİP: hiçbir çağıran kendi marjını HESAPLAMIYOR (ast ②) ────────────

def test_CAGIRANLAR_KENDI_MARJINI_HESAPLAMIYOR():
    """🔴 `KAT-1`. Marj kıyası tek bir yazılışa sahiptir: `en_iyi − ikinci ≥ marj`.

    ⚠ ② **`ast` ile** aranır, metinle değil: bir yorum satırındaki formül kapıyı
    yanıltmamalı 🅙. Aranan desen *«iki skorun çıkarması bir sabitle kıyaslanıyor»*.
    """
    for ad in ("cube_router.py", "value_index.py"):
        agac = ast.parse((_APP / ad).read_text(encoding="utf-8"))
        for d in ast.walk(agac):
            # `X - Y >= Z` ya da `Y > X - Z` — ikisi de aynı marj kıyasının yazılışı
            if not isinstance(d, ast.Compare):
                continue
            taraflar = [d.left, *d.comparators]
            for t in taraflar:
                if isinstance(t, ast.BinOp) and isinstance(t.op, ast.Sub):
                    # skor çıkarması mı? — her iki tarafı da `.score`/`_score` olan
                    isim = ast.dump(t)
                    assert not ("score" in isim and "score" in isim.split("right=")[-1]), (
                        f"🔴 `{ad}` hâlâ KENDİ marjını hesaplıyor: {ast.unparse(t)} — "
                        "`emin_miyim.karar` çağrılmalı (KAT-1).")


def test_DORT_CAGIRAN_DA_BAGLI():
    """㉕ Modülün **çağrıldığını** sayar. 🆘 *«Yazılmış ama bağlanmamış»* bu depoda
    **beş kez** ölçüldü; `emin_miyim` beşincisi olmasın."""
    cr = (_APP / "cube_router.py").read_text(encoding="utf-8")
    vi = (_APP / "value_index.py").read_text(encoding="utf-8")
    assert cr.count("_emin_karar(") == 3, (
        f"🔴 `cube_router` içinde 3 çağrı bekleniyordu, {cr.count('_emin_karar(')} var.")
    assert "from app.emin_miyim import" in vi and "karar(" in vi


# ── ② ①'in davranışı BİREBİR: value_index.auto_fix ────────────────────────────

def test_auto_fix_ESIK_ve_MARJ_birebir():
    """`AUTO_SCORE`=0,80 · `AUTO_MARGIN`=0,08 — üç sınır vakası.

    🅑 Mutasyon: `taban`↔`marj` yer değiştirirse ya da `>=` `>` olursa kırılır.
    """
    from app.value_index import AUTO_MARGIN, AUTO_SCORE

    assert AUTO_SCORE == 0.8 and AUTO_MARGIN == 0.08, "kalibre sabit DEĞİŞTİ"
    # tam eşikte + tek aday → oto
    assert karar([0.80], taban=AUTO_SCORE, marj=AUTO_MARGIN) is Karar.OTO_ICRA
    # eşiğin altında → oto DEĞİL (öneri kademesi yok → SINIR)
    assert karar([0.79], taban=AUTO_SCORE, marj=AUTO_MARGIN) is Karar.SINIR
    # yakın ikinci aday (fark tam marj) → kabul; marjın altında → red
    assert karar([0.90, 0.82], taban=AUTO_SCORE, marj=AUTO_MARGIN) is Karar.OTO_ICRA
    assert karar([0.90, 0.83], taban=AUTO_SCORE, marj=AUTO_MARGIN) is Karar.SINIR


# ── ③ ②'nin ÜÇ KADEMESİ birebir + `_MID_WIDE` kaybolmadı ─────────────────────

def test_typo_UC_KADEME_ve_MID_WIDE_korundu():
    """`0,82` oto · `0,65` öner · `0,08` marj — ve *«cube çözülemediyse baraj yükselir»*.

    🔴 Bu yüklem `_TYPO_MID_WIDE`'ın **taşındığını** kanıtlar: aynı skor, bağlam
    belirsizken **GOSTER değil SINIR** olmalı. Kaybolsaydı ikisi eşitlenirdi ㊲.
    """
    from app.cube_router import _TYPO_GAP, _TYPO_HIGH, _TYPO_MID, _TYPO_MID_WIDE

    assert (_TYPO_HIGH, _TYPO_MID, _TYPO_GAP) == (0.82, 0.65, 0.08)
    ortak = dict(taban=_TYPO_HIGH, marj=_TYPO_GAP, taban_goster=_TYPO_MID,
                 taban_goster_genis=_TYPO_MID_WIDE)
    # yüksek + net → oto
    assert karar([0.90, 0.50], **ortak) is Karar.OTO_ICRA
    # yüksek ama ikinci yapışık → yalnız öner
    assert karar([0.90, 0.88], **ortak) is Karar.GOSTER
    # orta → öner (cube ÇÖZÜLMÜŞ)
    assert karar([0.70, 0.10], **ortak) is Karar.GOSTER
    # 🔴 aynı orta skor, cube ÇÖZÜLEMEMİŞ → baraj 0,82'ye çıkar → SUS
    assert karar([0.70, 0.10], **ortak, baglam_belirsiz=True) is Karar.SINIR
    # düşük → her hâlde sus
    assert karar([0.40, 0.10], **ortak) is Karar.SINIR


# ── ④' HARF BİRİMİ KORUNDU (planın «normalize et»inin yerine) ────────────────

def test_harf_farki_BIRIMI_KORUNUYOR_normalize_YOK():
    """🔴 `:1190`'ın kuralı *«≥4 harf fark»*tır ve **harf olarak** geçirilir.

    Tablo testi — özgün eşitsizliğin (`a − b >= 4`) her sınırı:
    """
    for a, b, beklenen in [(11, 4, True), (8, 4, True), (7, 4, False),
                           (4, 0, True), (6, 4, False), (4, 4, False)]:
        sonuc = karar([float(a), float(b)], marj=4.0) is Karar.OTO_ICRA
        assert sonuc is beklenen, f"🔴 harf farkı {a}−{b}: {sonuc}, beklenen {beklenen}"
    # ve kaynakta bir «normalize» sabiti YOK — uydurulmuş payda aranıyor ㊱
    kaynak = (_APP / "cube_router.py").read_text(encoding="utf-8")
    assert "_longest_syn_hit(q, c)) / " not in kaynak, (
        "🔴 harf sayısı bir paydaya bölünmüş — `emin_miyim` başlığındaki karar çiğnendi.")


def test_TEK_ADAY_dejenere_hali():
    """④ `len(adaylar)==1` → `marj=∞`. İki aday eşit skorluyken fark `0 < ∞`."""
    assert karar([0.0], marj=math.inf) is Karar.OTO_ICRA
    assert karar([0.0, 0.0], marj=math.inf) is Karar.SINIR
    assert karar([], marj=math.inf) is Karar.SINIR


# ── ⑤' SÖZLEŞME: birim-bağımsız, ve bunu SÖYLÜYOR 🅖 ─────────────────────────

def test_modul_BIRIM_BAGIMSIZLIGINI_ILAN_EDIYOR():
    """🅖 *Eksiği yayına yaz.* Bu modül bir **güven yüzdesi üretmez**; farklı
    çağıranların skorları birbiriyle kıyaslanamaz. İlan kaybolursa biri onu bir
    güven skoru sanır ve `MIMARI.md`'nin *«kalibre edilmemiş sayı bir süstür»*
    kararı sessizce çiğnenir 🅐."""
    metin = (_APP / "emin_miyim.py").read_text(encoding="utf-8")
    for parca in ("birim-bağımsız", "güven", "kalibre"):
        assert parca in metin, f"🔴 sözleşme ilanı eksik: {parca!r}"


def test_bos_ve_tek_elemanli_girdi_PATLAMIYOR():
    """🅡 Naif girdi. `karar` bir karar fonksiyonudur; çağıranı **korumalıdır**."""
    assert karar([], marj=0.0) is Karar.SINIR
    assert karar([0.5], marj=0.0, taban=0.9) is Karar.SINIR
    assert karar([0.5], marj=0.0, taban=0.9, taban_goster=0.4) is Karar.GOSTER
