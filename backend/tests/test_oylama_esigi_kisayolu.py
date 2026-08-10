"""🔴🔴 `§D2/K` — **«TEK ADAY» KISAYOLU EŞİĞİ ATLIYORDU.**

`D2` (`oylama_paydasi`) bir **yalanı** kapatmıştı: 1 cevap + 2 çekimser, payda
`cands` ile **%100 «oy birliği»** görünüyordu. Bayrak paydayı düzeltti ve makbuz artık
**%33** yazıyor.

🔴 Ama **kararı** düzeltmedi: `if len(votes) == 1 or agreement >= 2/3` dalı eşiği hiç
sormadan dönüyordu. Canlı kanıt (curl, 2026-08-10):

    «bunu nasıl yorumlarsın» → trace: self-consistency %33 (3 örnek) → CEVAP VERDİ

⊙ Makbuz *«%33 uyum»* yazarken sistem **oy birliğiyle** davranıyordu.
*Bir sayıyı dürüst yazmak, ona göre davranmakla aynı şey değildir.*
"""

from app.routers.ask import _canon_cq


def _oyla(oylar, tam_payda):
    """`_select_consistent`'ın karar çekirdeği — sağlayıcısız yeniden kurulmuş hâli.

    ⚠ Fonksiyonun kendisi bir LLM istemcisi ister; burada sınanan şey **karar kuralı**
    ve o kural saf aritmetiktir. *Bir kuralı sınamak için onu taşıyan boruyu kurmak
    gerekmez — ama kuralın kopyası orijinaliyle aynı olmalıdır.*
    """
    cands = [c for c in oylar if c]
    if not cands:
        return None, 0.0
    votes: dict[str, list[dict]] = {}
    for c in cands:
        votes.setdefault(_canon_cq(c), []).append(c)
    best = max(votes.values(), key=len)
    agreement = len(best) / (len(oylar) if tam_payda else len(cands))
    return (best[0] if agreement >= 2 / 3 else None), agreement


_CQ = {"cube": "oee", "measures": ["ort_oee"]}


def test_BIR_CEVAP_IKI_CEKIMSER_ARTIK_CEVAP_VERMEZ():
    """🔴 **Kapının kalbi.** Üç örneğin ikisi *«bilmiyorum»* dediyse, cevap veren tek
    örneğin kendisiyle hemfikir olması bir **oy birliği değildir**."""
    kazanan, uyum = _oyla([_CQ, None, None], tam_payda=True)
    assert abs(uyum - 1 / 3) < 1e-9
    assert kazanan is None, "🔴 %33 uyumla cevap verilemez — netleştirmeye düşmeli"


def test_IKI_CEVAP_BIR_CEKIMSER_GECER():
    """⚠ Kapı fazla ileri gitmemeli: 2/3 eşiktir ve **tam eşikte geçer**."""
    kazanan, uyum = _oyla([_CQ, dict(_CQ), None], tam_payda=True)
    assert abs(uyum - 2 / 3) < 1e-9
    assert kazanan is not None


def test_UC_CEVAP_HEMFIKIR_GECER():
    """Gerçek oy birliği aynen geçer — düzeltme bir **kırpma** değil."""
    kazanan, uyum = _oyla([_CQ, dict(_CQ), dict(_CQ)], tam_payda=True)
    assert uyum == 1.0 and kazanan is not None


def test_BAYRAK_KAPALIYKEN_DAVRANIS_BIREBIR_AYNI():
    """🔴🔴 **`KURAL B`.** Bayrak kapalıyken payda `cands`'tir ve tek adayda oran
    **her zaman 1.0** — yani kısayolu kaldırmak eski davranışı **birebir korur**.
    Yeni koşul yalnız bayrak açıkken ısırır: ölçülen kusurun tam yaşandığı yerde."""
    kazanan, uyum = _oyla([_CQ, None, None], tam_payda=False)
    assert uyum == 1.0 and kazanan is not None


def test_IKI_FARKLI_CEVAP_BIR_CEKIMSER_DUSER():
    """Üç örnek, iki farklı cq, biri çekimser → en iyi aday %33 → netleştirme.
    *Bölünmüş bir oy, azınlığın kazandığı bir seçim değildir.*"""
    kazanan, uyum = _oyla([_CQ, {"cube": "parti", "measures": ["toplam_ciro"]}, None],
                          tam_payda=True)
    assert abs(uyum - 1 / 3) < 1e-9 and kazanan is None


def test_HEPSI_CEKIMSER_CEVAP_YOK():
    """Üç *«bilmiyorum»* bir cevap üretemez — ve bu satır kapının **dekor olmadığını**
    kilitler: bir yolda mutlaka `None` dönmeli."""
    kazanan, uyum = _oyla([None, None, None], tam_payda=True)
    assert kazanan is None and uyum == 0.0
