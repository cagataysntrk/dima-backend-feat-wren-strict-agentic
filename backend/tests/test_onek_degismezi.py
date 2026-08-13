"""🔴 `§47` — **ÖNEK DEĞİŞMEZİ**: öngörü yazılanı **sürdürür**.

## Ölçülen kusur (2026-08-13)

| girdi | yazılanı taşımayan satır | yargı |
|---|---|---|
| `ram 3` · `fire` · `durus` | **0** | ✅ zaten sürdürüyor |
| `ci` | **2** — *«bu ay sipariş tutarı ne kadar?»* · *«bu ay ağır şikayet oranı ne kadar?»* | 🔴 anlamca komşu ama **tamamlama değil** |
| `firee` *(yazım hatası)* | **2** — *«bu ay fire ne kadar…»* | ✅ **doğru**; katı kural bunları öldürürdü |

Son satır bu kapının **zıt ölçütüdür** 🆃: kural bir **süzgeç** olsaydı ürünün yazım
hatası toleransı ölürdü. Bu yüzden kural bir **sıralama**dır — yazılanı taşıyanlar üste,
ötekiler altta ve **kaybolmadan**.

*Bir gürültüyü susturmanın yolu onu silmek değil, doğrunun sesini yükseltmektir.*
"""

from __future__ import annotations

from app import oneri, oneri_cumle
from app.oneri import _norm


def _cumleler(q: str, schema):
    return oneri_cumle.cumleler(oneri.ara(q, schema), capa=None, schema=schema, soru=q)


def _tasiyor(metin: str, q: str) -> bool:
    return all(t in _norm(metin) for t in _norm(q).split() if t)


def test_YAZILANI_TASIYAN_SATIRLAR_USTTE(schema):
    """Yazılanı sürdüren satır, sürdürmeyenin **üstünde** olmalı."""
    for q in ("ci", "fire", "ram 3"):
        cu = _cumleler(q, schema)
        if len(cu) < 2:
            continue
        bayraklar = [0 if _tasiyor(o.metin, q) else 1 for o in cu]
        assert bayraklar == sorted(bayraklar), (
            f"🔴 «{q}»: yazılanı taşımayan satır üste çıkmış → "
            f"{[o.metin for o in cu][:4]}")


def test_ILK_SATIR_YAZILANI_SURDURUR(schema):
    """En üstteki öneri — `Enter`'ın seçeceği satır — yazılanı **taşımalı**."""
    for q in ("fire", "ram 3", "durus"):
        cu = _cumleler(q, schema)
        assert cu, f"🔴 «{q}» için hiç öneri yok"
        assert _tasiyor(cu[0].metin, q), f"🔴 «{q}» → ilk satır sürdürmüyor: {cu[0].metin}"


def test_ZIT_OLCUT_YAZIM_HATASI_ONERISI_KAYBOLMAZ(schema):
    """🔴 🆃 **Kural bir süzgeç değildir.**

    `firee` yazan kullanıcı *«bu ay fire ne kadar…»* önerisini **görmeye devam etmeli**;
    o satır önek değişmezini **ihlal eder** ve bu **doğrudur** — yazım hatası düzeltmesi
    tam olarak budur. Bu test, sıralamanın bir gün süzgece dönüşmesini engeller.
    """
    cu = _cumleler("firee", schema)
    assert cu, "🔴 yazım hatasında öneri tamamen düştü — süzgeç hâline gelmiş"
    assert any("fire" in _norm(o.metin) for o in cu), (
        f"🔴 düzeltme önerisi yok: {[o.metin for o in cu]}")
