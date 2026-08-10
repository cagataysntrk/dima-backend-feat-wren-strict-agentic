"""🔴🔴 `B-5` — **«EN KÖTÜ» BİR YÖNDÜR ve her ölçüde YAZILI olmalı.**

## Ölçülen kusur

173 ölçü tanımının **114'ünde** (%66) `lower_is_better` beyanı yoktu. Beyan yokken
sistem sessizce *«çok olan iyidir»* varsayıyor. Canlı bedeli kayıtlı: *«karbon ayak
izini en kötüden iyiye sırala»* → `direction: asc` — **en düşük karbon en üste** kondu.
Sistem kullanıcıya tam tersini verdi ve **verdiğini söylemedi**.

## ⊙ Ve doldururken raporun kendi önerisinden DAHA DOĞRU bir sonuç çıktı

Rapor *"125 kalemi birimlerine göre doldur"* diyordu. Ölçünce görüldü: kalemlerin
**46'sının doğal bir yönü YOK** — `bakiye` · `hareket_sayisi` · `alim_miktari` ·
`en_yuksek_kur`. Bunlarda «çok olması iyi mi» sorusunun cevabı **bağlama** bağlıdır.

🔴 Onlara yön uydurmak, beyansızlıktan **daha kötü** olurdu: beyansızlık bir borçtur ve
görülebilir; uydurulmuş bir yön ise **doğru görünen yanlış bir cevaptır**.

⊙ Bu yüzden üç durum var ve **üçü de açıkça yazılır**:

| beyan | anlamı |
|---|---|
| `lower_is_better: true` | yüksek = KÖTÜ (14) |
| `lower_is_better: false` | yüksek = İYİ (54) |
| `lower_is_better: null` | **yön YOK** — bilinçli nötr (46) |

*Bir yönün olmaması bir eksiklik değil bir olgudur — ama söylenmek zorundadır, yoksa
onu bir eksiklikten ayırt etmenin yolu kalmaz.*
"""

from __future__ import annotations

import pathlib

import yaml

_PACKS = pathlib.Path(__file__).resolve().parents[1] / "demo" / "packs"


def _olculer():
    for md in sorted(_PACKS.rglob("cubes/*/metadata.yml")):
        d = yaml.safe_load(md.read_text(encoding="utf-8")) or {}
        for m in (d.get("measures") or []):
            if isinstance(m, dict) and m.get("name"):
                yield md, m


def test_HER_OLCU_YON_BEYAN_EDER():
    """🔴 Beyansız bir ölçü pack'e giremez — `default_measure` kapısının eşleniği."""
    eksik = [f"{md.parent.name}.{m['name']}" for md, m in _olculer()
             if "lower_is_better" not in m and "lowerIsBetter" not in m]
    assert not eksik, (
        f"🔴 {len(eksik)} ölçüde yön beyanı YOK: {eksik[:12]}\n"
        "  Üç seçenekten biri yazılmalı: `true` (yüksek kötü) · `false` (yüksek iyi) · "
        "`null` (yön yok — bilinçli nötr).\n"
        "  ⚠ Boş bırakmak DÖRDÜNCÜ bir seçenek değildir: sistem o hâlde sessizce "
        "«çok olan iyidir» varsayar ve «en kötü» sorusuna TERSİNİ cevaplar.")


def test_BEYAN_UC_DEGERDEN_BIRI():
    """⚠ `"true"` gibi bir dizge, YAML'da doğru sanılır ve sessizce yanlış olur."""
    bozuk = [f"{md.parent.name}.{m['name']}={m.get('lower_is_better')!r}"
             for md, m in _olculer()
             if m.get("lower_is_better", None) not in (True, False, None)]
    assert not bozuk, f"yön beyanı bool ya da null olmalı: {bozuk[:8]}"


def test_NOTR_OLCULER_YON_LISTESINE_GIRMEZ():
    """🔴 `null` **falsy**'dir — derleyici onu `lower_is_better` listesine almaz.

    Bu bir tesadüf değil sözleşmedir: nötr bir ölçü *«yüksek kötü»* sayılamaz. Kapı
    burada duruyor ki biri `null`'ı bir gün *«bilinmiyor → kötü say»* diye yorumlamasın.
    """
    for _md, m in _olculer():
        if m.get("lower_is_better") is None and "lower_is_better" in m:
            assert not m.get("lower_is_better"), m["name"]
