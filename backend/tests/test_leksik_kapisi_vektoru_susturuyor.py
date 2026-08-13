"""🔴 `§77` — **TEŞHİS DONDURULDU**: leksik kapı, vektörün getirdiği adayı **eliyor**.

## Ölçülen kayıp (`§76`, 37 vaka)

| ayak | `R@3` | `MRR` |
|---|---|---|
| vektör | **91,9** | 0,868 |
| birleşik (max) | **91,9** | 0,854 |
| 🔴 **ürün (RRF)** | **83,8** | 0,806 |

## Sebep — koda yazılı, tahmin değil ③

```python
if lek:                                   # app/oneri.ara
    lek_kume = set(lek)
    puan = {i: p for i, p in puan.items() if i in lek_kume}
```

Leksik ayak **bir şey** bulduğunda aday kümesi ona **kapanır**; vektör ayağı yalnız
**sıralayabilir**, aday **ekleyemez**. Düşen üç vaka `sıra=None` ile düşüyor — yani
*«aşağı itilmiş»* değil, **hiç listede yok**:

| ifade | ürün ilk-5 | vektörün bulduğu |
|---|---|---|
| *«makine verimliliği»* | `parti.ort_hiz_m_dk` (tek aday) | `oee.ort_oee` **1.** |
| *«delivery performance»* | `oee.ort_performans` · … | `siparis.zamaninda_teslim_yuzde` **1.** |
| *«complaint count»* | `bakim.ariza_sayisi` · … | `sikayet.sikayet_adedi` **3.** |

⊙ Üçü de **anlamsal/İngilizce** — leksik ayağın zayıf, vektörün güçlü olduğu tam yer.

## ⚠ Kapı bu satırı **savunmuyor**, **kaydediyor** ㊸

O satır bir kusur değil, **ölçülmüş bir çare**: kendi şerhi *«`fire` için leksik ayak 3
aday buluyor, ekranda 7 görünüyordu … kullanıcı «fire» yazıp «doğalgaz» okuyor»* diyor.
Yani iki gerçek bir arada: **gürültüyü kesiyor** ve **anlamsal adayı da kesiyor**.

## Ölçülmüş bir aday çare (uygulanmadı)

Deney (mutasyonla, sonra **geri alındı**): kapıya *«vektörün **birincisi** geçsin»*
eklendi →

| | `R@1` | `R@3` | `MRR` |
|---|---|---|---|
| bugün | 78,4 | 83,8 | 0,806 |
| deney | 78,4 | **86,5** | **0,820** |

Gürültü kontrolü ㊳ (`fire` · `ciro` · `ram 3`) **kontrol grubuyla birebir aynı** çıktı —
yani deney bir gerileme üretmedi. Ama **91,9'a da ulaşmıyor**: üç vakanın **ikisi** hâlâ
düşüyor. *Bir çarenin ölçüsü, kapattığı açığın tamamıdır; yarısını kapatan bir çare bir
karardır, bir düzeltme değil.* Bu yüzden **uygulanmadı** — kendi turunu, korpusunu ve
canlı doğrulamasını ister.

## Bu kapının üç yüklemi

| # | savunulan |
|---|---|
| 1 | kapı **hâlâ orada** — biri kaldırırsa `§77` kararı yeniden okunmalı ㉕ |
| 2 | vektör ayağı **süzgeç değil** (`MIMARI`) — ama kapı onu **fiilen** süzgeçleştiriyor |
| 3 | 🆃 leksik **boşken** vektör tek çare — o dal **korunmalı** |
"""

from __future__ import annotations

import inspect

from app import oneri


def _ara_kaynagi() -> str:
    return inspect.getsource(oneri.ara)


def test_LEKSIK_KAPISI_YERINDE():
    """㉕ Bu satır değişirse `§77`'nin ölçümü **bayatlar** — kırmızı, bir hatırlatmadır."""
    k = _ara_kaynagi()
    assert "if lek:" in k, (
        "🔴 leksik kapı kaldırılmış/değişmiş. `ONGORU-DURUM.md §77`: bu satır hem "
        "gürültüyü hem **anlamsal adayı** kesiyor (`R@3` 83,8 ↔ vektör 91,9). "
        "Değiştiriyorsan ölçümü **yeniden koş** ve `§77`'yi güncelle.")
    assert "lek_kume" in k, "🔴 kapının gövdesi değişmiş — ölçüm bayatlamış olabilir"


def test_VEKTOR_AYAGI_ADAY_EKLEYEMIYOR():
    """🔴 **ASIL TEŞHİS.** Kapı açıkken puan sözlüğü **leksik kümeye** daraltılıyor;
    vektörün birinci sırası bile listeye giremiyor."""
    k = _ara_kaynagi()
    i = k.index("if lek:")
    govde = k[i:i + 260]
    assert "puan.items() if i in lek_kume" in govde, (
        f"🔴 daraltma deseni değişmiş — teşhis yeniden yapılmalı:\n{govde[:180]}")


def test_ZIT_OLCUT_LEKSIK_BOSKEN_VEKTOR_TEK_CARE():
    """🆃 Kapı **koşullu** olmalı: leksik hiçbir şey bulamadığında (`zayiat` · `vardya`)
    vektör tek çaredir ve liste ondan kurulur. `if lek:` koşulu kalkarsa o dal ölür."""
    k = _ara_kaynagi()
    assert "if lek:" in k and "if not lek" not in k.split("if lek:")[0][-120:], (
        "🔴 daraltma koşulsuz hâle gelmiş — leksik boşken vektör de susturulur")
