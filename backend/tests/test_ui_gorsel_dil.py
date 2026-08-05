"""GÖRSEL DİL KAPISI — *ölçülmüş bir kusur, ölçülebilir bir kuralla kapatılır.*

## 🔴 Neden bu kapı

Kullanıcı arayüzü *"bembeyaz dikdörtgen, demode ve göz yorucu"* diye tarif etti.
Ölçüldü — kanaat değil, sayı:

| ölçüm | değer |
|---|---|
| baskın yazı boyutu | **188× 11px · 121× 10px**, hatta 6× 9px |
| okunabilir 15px | **3 kez** |
| `font-mono` | **387 kez** |
| kenarlık ↔ gölge | **222 ↔ 17** |
| en büyük yarıçap | **4px**, `rounded-*` yalnız **7 kullanım** |

Yani: *beyaz zemin üzerine, 10-11 piksel, tamamı monospace, keskin köşeli, 222
çizgiyle bölünmüş.* Bir **terminal/cihaz paneli** estetiği — sohbet ürününün değil.

> 🔴 **Ve asıl tuzak:** panelleri yeniden dizip bu dördünü korumak, *aynı çirkin şeyi
> yeni bir düzende* yapmaktır. Düzen değişir, görüntü aynı kalır. Bu kapı o tuzağı
> kapatır: taahhüt bir sözde değil, bir **testte** yaşar.

⚠ **FAZ 1 kapsamı:** yalnız belirteçlerin **varlığı**. Bileşenlerin onları
benimsemesi FAZ 5'in işi ve kapı orada genişleyecek — bugün genişletmek, henüz
yapılmamış bir işi kırmızı göstermek olurdu.
"""

from __future__ import annotations

import pathlib
import re

from tests.kapi_ortak import frontend_dir


def _css() -> str:
    return (frontend_dir() / "app" / "globals.css").read_text(encoding="utf-8")


def _blok(secici: str) -> str:
    """Bir CSS bloğunun **yalnız kendisi** — kapanış süslü ayracına kadar.

    🔴 İlk yazımda `css[css.index(secici):]` yazdım ve blok **kendinden sonraki her
    şeyi** kapsadı: koyu tema denetimi açık temanın değerlerini de görüp *"yüzeyler
    ayrışmıyor"* dedi. Kapı **kendi dilimleme hatamı** yakaladı.

    *Bir bloğun başlangıcını bilmek, bittiği yeri bilmek değildir.*"""
    css = _css()
    bas = css.index(secici)
    son = css.index("}", bas)
    return css[bas:son]


BEKLENEN_BELIRTECLER = (
    # (belirteç, ne için)
    ("--surface-1", "tuval — yüzey ölçeğinin tabanı"),
    ("--surface-2", "panel/kart"),
    ("--surface-3", "yükseltilmiş kart"),
    ("--surface-4", "açılır menü/tooltip — gerçekten yüzen"),
    ("--surface-kenar", "yüzeyler arası 1px ayırıcı"),
    ("--radius-lg", "panel/kart 12px"),
    ("--radius-btn", "düğme/girdi 8px"),
    ("--radius-chip", "çip/rozet 6px"),
    ("--text-body", "sohbet gövdesi 16px"),
    ("--lh-body", "sohbet satır yüksekliği 1.6"),
    ("--text-panel", "panel içi 14px"),
    ("--text-meta", "meta 12.5px"),
    ("--measure", "okunabilir satır uzunluğu 68ch"),
    ("--motion-md", "panel/çubuk geçişi 200ms"),
    ("--ease-standard", "standart yumuşatma"),
    ("--cubuk-genis", "sol çubuk 256px"),
    ("--cubuk-ray", "ray 56px"),
    ("--panel-min", "panel alt sınırı 400px"),
    ("--panel-varsayilan", "panel varsayılanı 480px"),
    ("--sohbet-min", "sohbet alt sınırı 520px"),
)


def test_BELIRTECLER_VAR():
    """Her düzen/görsel sayı **tek kaynakta** yaşar.

    ⚠ *Bileşen CSS'ine yazılmış bir sihirli sayı, ikinci bir sahiptir* — biri
    güncellenir, öteki kalır ve arayüz kendi içinde tutarsızlaşır."""
    css = _css()
    eksik = [f"{t} ({ne})" for t, ne in BEKLENEN_BELIRTECLER if t not in css]
    assert not eksik, f"🔴 eksik belirteç: {eksik}"


def test_DORT_YUZEY_SEVIYESI_KOYU_TEMADA_AYRISIR():
    """🔴 Derinlik **gölgeyle değil parlaklıkla** kurulur — 2026'nın hâkim yönü.
    Koyu temada dört seviye birbirinden **ayrı** olmalı; aynı olsalar yüzey ölçeği
    bir isimden ibaret kalırdı."""
    koyu = _blok(':root[data-theme="dark"]')
    degerler = re.findall(r"--surface-([1-4]):\s*(#[0-9a-fA-F]{6})", koyu)
    bulunan = {n: v.lower() for n, v in degerler}
    assert len(bulunan) == 4, f"koyu temada dört yüzey yok: {bulunan}"
    assert len(set(bulunan.values())) == 4, \
        f"🔴 koyu yüzeyler ayrışmıyor (aynı değer): {bulunan}"


def test_SAF_SIYAH_ZEMIN_YOK():
    """🔴 `#000000` zeminde beyaz metin **halation** üretir: parlak harfler koyu
    zemine *kanar*, göz yorulur. Önerilen taban `#121212`+ bandı.

    ⚠ Kapı `--surface-*` üzerinde: FAZ 1 `--background`'a **dokunmuyor** (sıfır
    görsel değişim kuralı), o FAZ 5'te taşınacak."""
    css = _css()
    for m in re.finditer(r"--surface-[1-4]:\s*(#[0-9a-fA-F]{3,6})", css):
        renk = m.group(1).lower()
        assert renk not in ("#000", "#000000"), "saf siyah yüzey — halation riski"


def test_SAF_BEYAZ_METIN_YOK():
    """Koyu temada birincil metin **kırık beyaz** olmalı, saf `#fff` değil."""
    koyu = _blok(':root[data-theme="dark"]')
    m = re.search(r"--foreground:\s*(#[0-9a-fA-F]{3,6})", koyu)
    assert m, "koyu temada --foreground yok"
    assert m.group(1).lower() not in ("#fff", "#ffffff"), \
        "saf beyaz metin — halation riski"


def test_REDUCED_MOTION_transform_kapatir():
    """🔴 WCAG 2.3.3 (AAA): etkileşimle tetiklenen hareket **kapatılabilmeli**.
    Kayan paneller vestibüler rahatsızlık tetikleyicisidir.

    ⚠ Hareketi **tümden** kapatmak da yanlış: bir panelin açıldığını hiçbir ipucu
    vermeden değiştirmek, kullanıcıyı içeriğin nereden geldiği konusunda kör bırakır.
    Doğrusu **kaydırmayı kaldır, sönümlemeyi kısalt**."""
    css = _css()
    blok = css[css.index("@media (prefers-reduced-motion: reduce)"):]
    assert "transform: none" in blok, "reduced-motion transform'u kapatmıyor"
    assert "opacity" in blok, "opaklık alternatifi yok — hareket tümden kayboluyor"


def test_MEVCUT_DEGERLER_DEGISMEDI():
    """🔴 **FAZ 1'in sözü: sıfır görsel değişim.** Belirteçler *eklenir*, mevcut
    hiçbir değer değişmez (deponun kendi göç usulü).

    *Bir göçün ilk adımı görüntüyü değiştirirse, o adımın neyi bozduğu bir daha
    ayrıştırılamaz.*"""
    css = _css()
    for belirtec, deger in (("--radius-sm", "2px"), ("--radius-md", "4px"),
                            ("--opacity-disabled", "0.38"), ("--opacity-soluk", "0.62")):
        assert f"{belirtec}: {deger}" in css, \
            f"🔴 mevcut belirteç DEĞİŞMİŞ: {belirtec} artık {deger} değil"
    assert "--background: #ffffff" in css, "açık tema zemini değişmiş"
    assert "--background: #08090a" in css, \
        "koyu tema zemini FAZ 1'de değişmemeliydi (FAZ 5'in işi)"
