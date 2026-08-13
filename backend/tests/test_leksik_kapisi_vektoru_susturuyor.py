"""🔴 `§78` — **LEKSİK KAPI: daraltma sürüyor, ama vektörün EN EMİN adayı geçiyor.**

## Hikâye — bir satır hem çare hem kusurdu ㊸

`ara()`'daki `if lek:` kapısı gürültüyü kesmek için konmuştu (*«`fire` yazan kullanıcı
«doğalgaz» okuyor»*) ve **işini yapıyordu**. Ama aday kümesini leksiğe **kapatınca**
vektör ayağı *sıralayabilen ama aday ekleyemeyen* bir şeye dönüştü — `MIMARI`'nin
*«vektör bir sıralayıcıdır, süzgeç değil»* cümlesinin tersi.

Ölçüldü (`§77`, 37 vaka): üç **anlamsal/İngilizce** ifade `sıra=None` ile düşüyordu —
aşağı itilmiş değil, **hiç listede yok**.

## Tarama (`§78`) — ve sınırın **aynı taramada** görünmesi 🅜

```
k=0 (eski)  R@3 83,8 · R@5 83,8 · MRR 0,806   gürültü: temiz
k=1         R@3 86,5 · R@5 86,5 · MRR 0,820   gürültü: TEMİZ   ← seçilen
k=2         R@3 86,5 · R@5 91,9 · MRR 0,832   🔴 «ciro» → ik.toplam_prim
k=5         R@3 86,5 · R@5 91,9 · MRR 0,832   🔴 «fire» → parti.toplam_metre
```

🔴 `k≥2`'nin `R@5` kazancı **kapının kurulma sebebini geri getiriyor**: `k=5`'te *«fire»*
yine *«metre»* gösteriyor — kapının kendi şerhinde **adıyla** yazan kusur. *Bir sayı
iyileşirken ekranın bozulabileceğinin kanıtı, aynı taramanın içindeydi.*

⊘ Kalan açık (86,5 ↔ vektör tavanı **91,9**) **kapanmadı**: iki vaka daha ancak **gürültü
ödeyerek** gelir 🆖. Kapatılmaması bir eksik değil, ölçülmüş bir **karar** 🆂.

## Bu kapının dört yüklemi

| # | savunulan |
|---|---|
| 1 | daraltma **duruyor** — kapı kaldırılmadı |
| 2 | vektörün **en emin** adayı geçiyor (`_VEK_GECIS`) |
| 3 | 🆃 geçiş **dar** kalıyor (`≤1`) — `k≥2` gürültüyü geri getirir |
| 4 | 🆃 leksik **boşken** vektör tek çare — o dal korunuyor |
"""

from __future__ import annotations

import inspect

from app import oneri


def _ara_kaynagi() -> str:
    return inspect.getsource(oneri.ara)


def test_DARALTMA_DURUYOR():
    """🔴 Kapı **kaldırılmadı**: gürültü kesmesi hâlâ orada."""
    k = _ara_kaynagi()
    assert "if lek:" in k, "🔴 leksik kapı kaldırılmış — `fire` → `metre` gürültüsü döner"
    assert "puan.items() if i in lek_kume" in k, "🔴 daraltma deseni değişmiş"


def test_VEKTORUN_EN_EMIN_ADAYI_GECIYOR():
    """🔴 **ASIL DEĞİŞMEZ.** Anlamsal aday listeye **girebilmeli**."""
    k = _ara_kaynagi()
    assert "lek_kume.update(vek[:_VEK_GECIS])" in k, (
        "🔴 vektör adayı kapıdan geçmiyor — `§77`'nin üç anlamsal vakası yine `sıra=None` "
        "ile düşer (`«makine verimliliği»` · `«delivery performance»` · `«complaint count»`)")


def test_ZIT_OLCUT_GECIS_DAR_KALIYOR():
    """🆃🅜 Kapının **kurbanı**: geçişi genişletmek `R@5`'i 91,9'a çıkarır **ama** `k=5`'te
    *«fire»* sorgusu yine *«metre»* gösterir. Sayı iyileşirken ekran bozulur."""
    assert oneri._VEK_GECIS <= 1, (
        f"🔴 `_VEK_GECIS={oneri._VEK_GECIS}` — tarama `k≥2`'de gürültü ölçtü "
        "(«ciro» → `ik.toplam_prim`, «fire» → `parti.toplam_metre`). Büyütüyorsan "
        "`§78` taramasını **yeniden koş** ve gürültü kontrolünü ㊳ raporla.")
    assert oneri._VEK_GECIS >= 1, "🔴 geçiş kapatılmış — anlamsal vakalar geri düşer"


def test_ZIT_OLCUT_LEKSIK_BOSKEN_VEKTOR_TEK_CARE():
    """🆃 Kapı **koşullu** kalmalı: leksik hiçbir şey bulamadığında (`zayiat` · `vardya`)
    liste vektörden kurulur. `if lek:` koşulsuz hâle gelirse o dal ölür."""
    k = _ara_kaynagi()
    onces = k.split("if lek:")[0][-140:]
    assert "if not lek" not in onces, "🔴 daraltma koşulsuz olmuş — leksik boşken de susar"
