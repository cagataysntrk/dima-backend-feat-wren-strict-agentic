"""ANALİZ PANELİ — *panel modal DEĞİLDİR* sözü, testte yaşar.

## 🔴 Neden bu kapı

Kullanıcının gerekçesi: *"panel açıkken hem grafiğe bakıp hem yorum yazabilir;
modalda kapatmak zorunda kalır."* Bu, NN/g'nin modal kuralının birebir kendisi —
modal yalnız **geri alınamaz eylem**, **zorunlu bilgi** ve **kesintiyi hak eden
durum** için meşrudur.

> ⚠ *Bir paneli modale çevirmek dört küçük eklemeyle olur* — `role="dialog"`,
> focus trap, `inert`, `aria-modal`. Dördü de tek tek makul görünür ve dördü de
> ürünün **tek vaadini** iptal eder. Bu yüzden dördü de **yasak**, ve yasak bir
> sözde değil bir **testte** yaşamalı.

*Ölçülmüş kusur (Claude Code #60980): "yan sohbetler modal diyalog gibi davranıyor —
ya tamamen var ya yok."*
"""

from __future__ import annotations

import pathlib

from tests.kapi_ortak import frontend_dir, yorumsuz


def _src() -> str:
    """🔴 **YORUMSUZ** kaynak — ve bu bir kusurun anısı.

    İlk yazımda ham metni taradım ve kapı **kendi belgemi** yakaladı: `aria-modal`
    yasağı, o yasağı **anlatan yorumda** geçiyordu. Bu deponun defterindeki en sık
    tekrar eden küçük kusur — bir yasağı arayan tarama, yasağın **metnini** de bulur
    ve kendi yazarını suçlar.

    ⚠ Deponun kendi `yorumsuz()` yardımcısı tam bunun için var; kendi ayıklayıcımı
    yazmak *"aynı kuralın iki sahibi"* olurdu."""
    return yorumsuz(
        (frontend_dir() / "components" / "AnalizPaneli.tsx").read_text(encoding="utf-8"))


def test_ROL_complementary_dialog_DEGIL():
    """🔴 `role="dialog"` ekran okuyucuya *"bu bir kesinti, bitirmeden devam
    edemezsin"* der. Vaadimiz tam tersi: arkadaki sohbet **canlı kalır**."""
    s = _src()
    assert 'role="complementary"' in s, "panel `complementary` rolü taşımıyor"
    assert 'role="dialog"' not in s, "🔴 panel `dialog` rolü almış — modale dönüştü"


def test_MODAL_YAPAN_UC_SEY_YOK():
    """`aria-modal` · `inert` · focus trap — üçü de paneli modale çevirir.

    ⚠ Her biri tek başına makul görünür; ürünün vaadini iptal eden şey **birlikte
    ne yaptıklarıdır**: arkadaki yüzeyi ölü hâle getirirler."""
    s = _src()
    for yasak, ne in (("aria-modal", "ekran okuyucuya kesinti der"),
                      ("inert", "arkadaki sayfayı ölü hâle getirir"),
                      ("useOdakTuzagi", "focus trap — odak panelden çıkamaz")):
        assert yasak not in s, f"🔴 panel modale dönüşmüş: `{yasak}` ({ne})"


def test_ESCAPE_yalniz_odak_panelde():
    """🔴 Escape'i **global** yakalamak, kullanıcı composer'da yazarken paneli
    kapatırdı — ürünün tek vaadi *"hem bak hem yaz"*tı ve bu onu kırardı.

    ## ⚠ Bu test bir kez YANLIŞ YERE bakıyordu

    İlk hâli mantığı `AnalizPaneli.tsx`'te arıyordu. Ama `A11Y-3` klavye kuralının
    **tek sahibi** olmasını istiyor (`lib/odakTuzagi.ts`) ve kapı beni haklı olarak
    kırmızı verdi. Mantığı oraya taşıdım — ve bu test **kendi eski varsayımıyla**
    kırıldı.

    *Bir kuralı doğru yere taşımak, onu arayan testi de taşımayı gerektirir; yoksa
    test doğru davranışı kusur sanar.*

    Yeni hâli **iki** şeyi sınıyor: panel elle dinleyici yazmıyor (tek sahibi
    kullanıyor) **ve** tek sahip gerçekten kapsam denetimi yapıyor."""
    panel = _src()
    assert "useKapsamliEscape" in panel, \
        "panel kapsamlı Escape kancasını kullanmıyor"
    assert "addEventListener" not in panel or '"Escape"' not in panel, \
        "🔴 panel elle Escape dinleyicisi yazmış — A11Y-3 ihlali"

    sahip = yorumsuz((frontend_dir() / "lib" / "odakTuzagi.ts").read_text(encoding="utf-8"))
    assert "useKapsamliEscape" in sahip, "kanca tek sahipte tanımlı değil"
    assert "contains(" in sahip, \
        "🔴 tek sahip kapsam denetimi yapmıyor — Escape GLOBAL yakalanıyor"


def test_KAPANISTA_ODAK_acan_dugmeye_doner():
    """*Odak yönetiminde ana fikir: kullanıcıyı kaybetme.* Kapanışta odağı geri
    taşımamak, onu boşluğa ya da belgenin başına düşürür."""
    s = _src()
    assert "acanRef" in s and ".focus?.()" in s, \
        "kapanışta odak açan düğmeye dönmüyor"


def test_ACILISTA_ODAK_TASINMAZ():
    """⚠ Panel açılınca odağı **zorla** panele taşımak, kullanıcının imlecini
    kaçırır — o an yazıyor olabilir. Başlık `tabindex={-1}` ile **ulaşılabilir**
    kalır ama odak kendiliğinden gitmez."""
    s = _src()
    assert "tabIndex={-1}" in s, "panel başlığı programlı odaklanabilir değil"
    assert ".focus()" not in s.split("const kapat")[0], \
        "🔴 açılışta odak zorla taşınıyor"


def test_AYIRICI_klavyeyle_de_calisir():
    """WAI-ARIA Window Splitter: `role="separator"` · `tabindex=0` · `aria-valuenow` ·
    ok tuşları · Home/End. ⚠ Ayırıcıyı klavyesiz bırakmak **fare zorunluluğu** doğurur."""
    s = _src()
    for gerek in ('role="separator"', "tabIndex={0}", "aria-valuenow",
                  "ArrowLeft", "ArrowRight", '"Home"', '"End"'):
        assert gerek in s, f"ayırıcıda eksik: {gerek}"


def test_ALT_SINIR_VAR_sinirsiz_kucultme_yok():
    """🔴 Ölçülmüş kusur: alt sınırsız yeniden boyutlandırmada kullanıcılar paneli
    minimuma çekiyor ve *"metin okunamaz hâle geliyor"*.

    Ve ikinci sınır: panel **sohbeti** okunamaz yaparak kendine yer açamaz."""
    s = _src()
    assert "PANEL_MIN = 400" in s, "panel alt sınırı yok"
    assert "SOHBET_MIN = 520" in s, "sohbetin okunabilirlik tabanı korunmuyor"
    assert "0.55" in s, "panel üst sınırı (%55vw) yok"


def test_TAM_GENISLIK_MODU_YOK():
    """🔴 Tam genişlik modu sohbeti **gizler** → konuşma bağlamı kaybolur ve
    *"hem bak hem yaz"* vaadi iptal olur. Claude'un teardown'ı bunu açık kusur
    olarak işaretliyor."""
    s = _src()
    assert "w-full" not in s.replace("max-lg:!w-full", ""), \
        "🔴 masaüstünde tam genişlik modu var — sohbeti gizler"


def test_COKLU_ANALIZ_sekme_seridi_DEGIL():
    """`‹ 3/5 ›` — sekme şeridi **değil**: beş analizden sonra şerit taşar ve
    kullanıcı hangi sekmede olduğunu kaybeder."""
    s = _src()
    assert "sira" in s and "toplam" in s, "çoklu analiz gezinmesi yok"
    assert 'role="tablist"' not in s, "🔴 sekme şeridi kurulmuş — taşma riski"
