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

from tests.kapi_ortak import frontend_dir, yorumsuz


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


def test_IKI_KOYU_BLOK_AYNI_PALETI_TASIR():
    """🔴 **Ölçülen kusur — FAZ 5 onu ortaya çıkarana kadar sessizdi.**

    Koyu tema **iki yerde** yazılı: `@media (prefers-color-scheme: dark)` ve
    `:root[data-theme="dark"]`. Ve varsayılan tercih `"sistem"`, o hâlde
    `lib/tema.ts` özniteliği **siliyor** → yani `@media` bloğu *asıl yoldur*.

    O blokta `--surface-*` **hiç yoktu**. FAZ 1'de görünmüyordu (kimse o tokenları
    kullanmıyordu); FAZ 5 tuvali `--surface-1`e bağlar bağlamaz, sistemi karanlık
    olan kullanıcı **kar beyazı bir tuval** görecekti.

    > *Bir tokenı tanımlamak onu doğru tanımlamak değildir; ve kullanılmayan bir
    > token yanlışlığını saklar. Kusuru ortaya çıkaran şey benimsenmesiydi.*

    Kapı iki bloğun **aynı anahtar kümesini** taşımasını ister — değerleri değil,
    **kapsamı**. Bir tema anahtarı yalnız birinde varsa, kullanıcıların yarısı
    onu hiç görmez."""
    media = _blok("@media (prefers-color-scheme: dark)")
    oznitelik = _blok(':root[data-theme="dark"]')
    a = set(re.findall(r"(--[a-z0-9-]+):", media))
    b = set(re.findall(r"(--[a-z0-9-]+):", oznitelik))
    assert a == b, (
        "🔴 iki koyu blok farklı anahtar taşıyor — "
        f"yalnız @media'da: {sorted(a - b)} · yalnız data-theme'de: {sorted(b - a)}"
    )


def test_AYIRICI_TEK_SAHIPLI():
    """🔴 `--hairline` (243 kullanım) ve `--surface-kenar` (17) **aynı şeyi**
    anlatıyordu ve koyu temada **farklı değerlerdeydi** (`#1c1d1f` ≠ `#262a31`) —
    yani aynı ayrım, onu çizen bileşene göre farklı görünüyordu.

    ⚠ Çözüm 17 çağrıyı yeniden yazmak **değil**: ikinci ad `var(--hairline)`e
    bağlandı. *Bir eş anlamlıyı silmek yerine sahibine bağlamak, çağıranları
    kırmadan tek sahibi kurar.*"""
    for blok in ("@media (prefers-color-scheme: dark)", ':root[data-theme="dark"]',
                 ':root[data-theme="light"]'):
        assert "--surface-kenar: var(--hairline)" in _blok(blok), \
            f"🔴 {blok}: ayırıcının ikinci sahibi geri gelmiş"


def test_KOYU_ZEMIN_HALATION_BANDINDA():
    """🔴 `#000` ve ona **çok yakın** tonlarda beyaz metin **halation** üretir:
    parlak harfler koyu zemine *kanar*, göz yorulur. Önerilen taban `#121212`+ bandı.

    ⚠ Kapı yalnız saf siyahı yasaklamak yetmez — `#08090a` saf siyah **değildi** ama
    aynı kusuru üretiyordu. *Bir yasağı en uç değerle sınırlamak, yasağın sebebini
    değil harfini korumaktır.*"""
    koyu = _blok(':root[data-theme="dark"]')
    m = re.search(r"--background:\s*#([0-9a-fA-F]{6})", koyu)
    assert m, "koyu temada --background yok"
    r, g, b = (int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4))
    parlaklik = 0.299 * r + 0.587 * g + 0.114 * b
    assert parlaklik >= 14, (
        f"🔴 koyu zemin fazla karanlık (parlaklık {parlaklik:.1f}) — halation riski; "
        "önerilen taban #121212+ bandı")


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


# ═══════════════════════════════════════════════════════════════════════════════
# FAZ 5 · PROSE ORANTILI, VERİ MONO
# ═══════════════════════════════════════════════════════════════════════════════

#: Sohbetin **insan metni** taşıyan yüzeyleri. ⚠ `ReportCard` bu listede DEĞİL:
#: içinde hem prose hem rozet/sayı var ve hepsini tek kuralla ölçmek yanlış olurdu.
PROSE_YUZEYLERI = ("OutputInsight",)


def test_PROSE_GOVDE_BOYUTUNDA():
    """🔴 Cevabın **anlatımı** 12px'ti — terminal puntosu.

    Ölçülmüştü: 188× 11px · 121× 10px, okunabilir 15px yalnız **3 kez**. Bir sohbet
    ürününde asıl unsur insan metnidir; onu 12 pikselde tutmak, ürünün ne olduğuna
    dair bir açıklamadır.

    ⚠ Kapı **prose yüzeylerine** bakar; sayı/rozet/meta hariç."""
    for ad in PROSE_YUZEYLERI:
        src = (frontend_dir() / "components" / f"{ad}.tsx").read_text(encoding="utf-8")
        assert "--text-body" in src, f"🔴 {ad}: anlatım gövde boyutunda değil"
        assert "--lh-body" in src, f"🔴 {ad}: okuma satır yüksekliği yok"


#: 🔴 **Sohbet akışı** — cevabın kendisi. Panel/çalışma yüzeyleri (`SchemaPanel`,
#: `ReviewPanel`, `DrillDownPanel`, `ContractDetailPanel`…) bilerek DIŞARIDA:
#: planın kapı tanımı birebir *"sohbet yüzeyinde"* diyor ve yoğun veri yüzeyinde
#: sıkı boy savunulabilir. *Bir kapının kapsamını sessizce genişletmek, planı
#: belgelemeden değiştirmektir.*
SOHBET_YUZEYLERI = (
    "ReportCard", "ReportPanel", "OutputInsight", "ChatPanel", "Makbuz",
    "SoruAlani", "KpiCard", "ResultView", "NextStepChips", "AnalysisCanvas",
    "SertifikaBandi", "KartZamanlama", "DcmAkisi", "DurdurDugmesi",
    "HistoryPanel", "KimlikSeridi",
)


def test_SOHBETTE_ON_PIKSEL_ALTI_YOK():
    """🔴 Ölçüldü: sohbet akışında **55 yerde** 9-10px metin vardı.

    10px altı metin normal görme keskinliğinde *okunmuyor* değil — **okumaya zorluyor**;
    ve bir sohbet ürününde okuma maliyeti ürünün kendisidir.

    ⚠ Taban `--text-etiket` (11px), `--text-meta` (12.5px) **değil**: büyük harfli
    mikro-etiketler (`KAYNAK`, `SORU`) 12.5px'te *bağırır* ve asıl metinle yarışır.
    Etiket **tanımlar**, meta **okunur** — iki iş, iki boy."""
    kotu = []
    for ad in SOHBET_YUZEYLERI:
        yol = frontend_dir() / "components" / f"{ad}.tsx"
        for n, satir in enumerate(yorumsuz(yol.read_text(encoding="utf-8")).split("\n"), 1):
            if re.search(r"text-\[(9|10)px\]", satir):
                kotu.append(f"{ad}.tsx:{n}")
    assert not kotu, f"🔴 sohbet yüzeyinde 11px altı metin: {kotu}"


def test_ETIKET_TABANI_ON_BIRDEN_KUCUK_DEGIL():
    """⚠ Tabanın kendisi de denetlenir. *Bir tabanı bir tokene taşımak onu korumaz —
    token da düşürülebilir.* Kapı, kuralın **sebebini** (11px) korur, adını değil."""
    m = re.search(r"--text-etiket:\s*([0-9.]+)rem", _css())
    assert m, "--text-etiket tanımlı değil"
    px = float(m.group(1)) * 16
    assert px >= 11, f"🔴 etiket tabanı {px:.1f}px — 11px'in altına indirilmiş"


def test_VERI_MONO_KALDI():
    """🔴 **Ters yönlü kapı** — ve bu tasarımın yarısı.

    *Sayıyı orantılı yazı tipine çevirmek hizalamayı bozar: bir sütundaki rakamlar
    birbirinin altına düşmez. Mono bir süs değil, sayının okunma biçimidir.*

    ⚠ Bu kapı olmasaydı *"mono'yu azalt"* kuralı sayıları da süpürürdü ve kimse
    neyin kaybolduğunu fark etmezdi."""
    for ad, ne in (("ResultTable", "tablo hücreleri"), ("Makbuz", "SQL ve kanıt"),
                   ("KpiCard", "KPI sayısı")):
        p = frontend_dir() / "components" / f"{ad}.tsx"
        if not p.exists():
            continue
        assert "font-mono" in p.read_text(encoding="utf-8"), \
            f"🔴 {ad}: {ne} mono'dan çıkarılmış — hizalama bozulur"


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
    # ⟳ FAZ 5 — koyu zemin `#08090a` → `#0f1115` **taşındı** (halation).
    # FAZ 1'in sözü *"o fazda dokunma"*ydı, *"asla dokunma"* değil; ve taşıma
    # yüzey ölçeğinin tabanıyla **aynı** değere yapıldı, keyfî bir tona değil.
    assert "--background: #0f1115" in css, \
        "koyu zemin yüzey bandında değil — halation riski"
