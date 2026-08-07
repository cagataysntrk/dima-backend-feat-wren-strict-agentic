"""🔴 **OPENROUTER ANAHTAR ZİNCİRİ** — ölçüm aracının durmaması için.

## Neden var

Ücretsiz katman dolunca `402 Payment Required` gelir ve **tüm LLM yolu susar**. Bu bir
kez oldu: ölçüm turu ürünün davranışını değil **faturayı** ölçmeye başladı.

*Bir ölçüm aracının durması, ölçtüğü şeyin bozulmasından daha sinsidir: biri kırmızı
verir, öteki sessizce sıfır ölçer.*

## Zincir DÖNGÜSELDİR

Anahtarlar sırayla denenir; tur başa döndüğünde ilkinin kotası çoktan tazelenmiştir.
Yani bu bir yedek değil bir **rotasyon** — kesintisiz ölçüm için.

## ⚠ İki tasarım kararı

1. **Rotasyon çağrı başına değil, HATA başına.** Her istekte anahtar değiştirmek
   sağlayıcının kota muhasebesini okunamaz kılar ve hangi anahtarın dolduğunu **hiç**
   öğrenemezdik. *Bir yedek, ancak öncekinin neden düştüğü bilinirse yedektir.*
2. **Yalnız `402`/`429` rotasyona sebep olur.** Şema hatası ya da `500`, anahtar
   değiştirmekle düzelmez ve zinciri boşuna tüketirdi.
3. **Yeniden denenmez**: çağrı bu tur düşer, sonraki tur yeni anahtarla açılır. Aynı
   istek içinde denemek bir hatayı gizleyip süreyi ikiye katlardı.
   *Bir yedeğe geçmek, hatayı silmek değil bir sonrakini kurtarmaktır.*
"""

from __future__ import annotations

import inspect

from app.llm import OpenAICompatibleSqlGenerator as Gen


def test_TEK_ANAHTAR_BUGUNKU_DAVRANIS():
    """`KURAL B` ruhu: zincir yoksa davranış **birebir bugünkü**."""
    g = Gen("http://x/v1", "tek-anahtar", "m")
    assert g._keys == ["tek-anahtar"] and g._key_ix == 0


def test_ZINCIR_AYRISTIRILIYOR():
    g = Gen("http://x/v1", " a , b ,, c ", "m")
    assert g._keys == ["a", "b", "c"], "🔴 boşluk/boş eleman temizlenmiyor"


def test_KOTA_HATASI_SIRADAKINE_GECER():
    """🔴 `402`/`429` → rotasyon. Sıra **döngüsel**: sonuncudan ilkine döner."""
    g = Gen("http://x/v1", "a,b,c", "m")
    src = inspect.getsource(Gen._chat)
    assert '"402" in _m or "429" in _m' in src, "🔴 rotasyon koşulu yok"
    assert "(self._key_ix + 1) % len(self._keys)" in src, "🔴 döngüsel değil"


def test_BASKA_HATA_ZINCIRI_TUKETMEZ():
    """⚠ Bir şema hatası ya da 500, anahtar değiştirmekle düzelmez."""
    src = inspect.getsource(Gen._chat)
    i = src.index("self._key_ix = (")
    assert "402" in src[max(0, i - 300):i], "🔴 rotasyon her hatada tetikleniyor"


def test_AYNI_ISTEK_ICINDE_YENIDEN_DENEMIYOR():
    """*Bir yedeğe geçmek, hatayı silmek değil bir sonrakini kurtarmaktır.*"""
    src = inspect.getsource(Gen._chat)
    i = src.index("self._key_ix = (")
    sonrasi = src[i:i + 400]
    assert "raise" in sonrasi or "return" not in sonrasi.split("\n")[1], (
        "🔴 rotasyondan sonra aynı istek yeniden deneniyor olabilir")


def test_TEK_ANAHTAR_ROTASYON_YAPMAZ():
    """Tek anahtarla `len(self._keys) > 1` koşulu rotasyonu kapatır — yoksa aynı anahtara
    sonsuz dönerdik ve log gürültüsü gerçek kusuru gizlerdi."""
    src = inspect.getsource(Gen._chat)
    assert "len(self._keys) > 1" in src
