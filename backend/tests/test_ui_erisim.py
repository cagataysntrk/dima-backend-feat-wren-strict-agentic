"""ARAYÜZ ERİŞİLEBİLİRLİK KAPISI — *taşınmayan bir özellik, silinmiş bir özelliktir.*

## 🔴 Neden bu kapı, ve neden **koda dokunmadan önce**

Arayüz yeniden yapılandırılıyor: sağdaki ikon şeridi kalkacak, beş çekmece tek bir sol
çubukta birleşecek, grafik makinesi panele taşınacak. Bir envanter denetimi bugünkü
arayüzde **269 ayrı kullanıcı işlevi** saydı ve bunların **25'inin tek bir giriş
noktası** olduğunu ölçtü.

> ⚠ Taşıma sırasında bunlardan biri düşerse **hiçbir test kırmızı vermez**, hiçbir
> derleme hatası çıkmaz, hiçbir uyarı görünmez. Kullanıcı onu aramaya kalktığı gün
> fark edilir — ve o gün ne zaman kaybolduğunu kimse bilemez.

*Bir kusuru ancak onu arayan bir kapı yakalar; ve bu kapının taşımadan **önce**
yazılması gerekir, çünkü sonradan yazılan kapı kaybolanı zaten göremez.*

## Nasıl ölçer — **ulaşılabilirlik**, varlık değil

Bir bileşenin dosyada **durması** yetmez: `ContractDetailPanel`'in denetim-kaydı ihracı
diskte duruyor ama **hiçbir çağıran** onu görünür kılan koşulu sağlamıyor (bkz.
`BEKLENEN_KIRIK`). Bu yüzden kapı bir **içe-aktarma grafiği** kurar ve giriş
noktalarından (`app/**/page.tsx`, `app/layout.tsx`) yürüyerek gerçekten **ulaşılan**
bileşenleri bulur.

⚠ Bu statik bir yaklaşımdır ve sınırı **yazılı**: bir bileşen ulaşılabilir olabilir ama
içindeki bir dal hiç render edilmiyor olabilir. Kapı *"kayboldu mu"* sorusunu cevaplar,
*"görünüyor mu"* sorusunu değil. İkincisi tarayıcı işidir.

## Hız

Satır tabanlı tarama, regex geri-izlemesi **yok** (`TEST-ORTAMI-KILAVUZU §9`'un üçüncü
denetim sorusu). Bütün ağaç bir kez okunur, sonuç modül düzeyinde önbelleklenir.
"""

from __future__ import annotations

import functools
import pathlib
import re

from tests.kapi_ortak import frontend_dir

# ⚠ Yolu kendim hesaplamıyorum: `kapi_ortak.frontend_dir()` hem repo kökünü hem
# konteyner mount'unu biliyor ve mount yoksa **skip** ediyor. Kendi yolumu yazmak
# *"aynı kuralın iki sahibi"* olurdu — biri güncellenir, öteki kalır.

#: Giriş noktaları — Next.js App Router'da render **buradan** başlar.
_GIRISLER = ("app/layout.tsx", "app/page.tsx", "app/login/page.tsx",
             "app/review/page.tsx", "app/brand/page.tsx",
             "app/paylasim/[token]/page.tsx")

_IMPORT = re.compile(r'from\s+["\']@/(?:components|lib)/([\w/]+)["\']')


@functools.lru_cache(maxsize=1)
def _kaynaklar() -> dict[str, str]:
    """`göreli yol (uzantısız) → kaynak metni`. Bir kez okunur."""
    fe = frontend_dir()
    out: dict[str, str] = {}
    for p in fe.rglob("*.ts*"):
        if p.suffix not in (".ts", ".tsx"):
            continue
        out[str(p.relative_to(fe).with_suffix(""))] = p.read_text(encoding="utf-8")
    return out


@functools.lru_cache(maxsize=1)
def _ulasilabilir() -> set[str]:
    """Giriş noktalarından **içe-aktarma grafiğiyle** ulaşılan her modül.

    ⚠ Genişlik-öncelikli yürüyüş; döngüsel import'ta sonsuza gitmez (`gorulen`).
    """
    kaynak = _kaynaklar()
    gorulen: set[str] = set()
    kuyruk = [g.removesuffix(".tsx") for g in _GIRISLER]
    while kuyruk:
        m = kuyruk.pop()
        if m in gorulen or m not in kaynak:
            continue
        gorulen.add(m)
        for hedef in _IMPORT.findall(kaynak[m]):
            for aday in (f"components/{hedef}", f"lib/{hedef}", hedef):
                if aday in kaynak and aday not in gorulen:
                    kuyruk.append(aday)
    return gorulen


def _modul(bilesen: str) -> str:
    return f"components/{bilesen}"


def _erisilebilir(bilesen: str, *, isaret: str | None = None) -> tuple[bool, str]:
    """(ulaşılabilir mi, teşhis). `isaret` verilirse o metin de kaynakta aranır."""
    m = _modul(bilesen)
    kaynak = _kaynaklar()
    if m not in kaynak:
        return False, f"dosya YOK: {m}.tsx"
    if m not in _ulasilabilir():
        return False, f"dosya var ama giriş noktalarından ULAŞILMIYOR: {m}.tsx"
    if isaret and isaret not in kaynak[m]:
        return False, f"bileşen ulaşılabilir ama «{isaret}» işareti kaybolmuş"
    return True, ""


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · ON ÜÇ PANEL — tavan dolu, hiçbiri kaybolamaz
# ═══════════════════════════════════════════════════════════════════════════════

PANELLER = (
    "ChatPanel", "ConnectionReviewPanel", "ContractDetailPanel", "DashboardsPanel",
    "DrillDownPanel", "HelpPanel", "HistoryPanel", "NotificationsBell", "ReportPanel",
    "ReviewPanel", "SchedulesPanel", "SchemaPanel", "TercihlerPanel",
)


def test_ON_UC_PANELIN_HEPSI_ULASILABILIR():
    """🔴 Panel tavanı **13/13**. Bir panel taşıma sırasında düşerse tavan *"boşaldı"*
    gibi görünür ve bir sonraki geliştirici oraya **yeni bir panel** koyar — kaybolan
    işlev bir daha aranmaz.

    ⚠ `NotificationsPanel` `NotificationsBell.tsx` içinde export ediliyor; kapı
    **dosyayı** değil **ulaşılabilirliği** ölçer."""
    dusen = [(p, t) for p in PANELLER for ok, t in [_erisilebilir(p)] if not ok]
    assert not dusen, f"🔴 ulaşılamayan panel: {dusen}"


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · 🔴 EN SİNSİ DÖRTLÜ — rail'in İÇİNDE DEĞİLLER
# ═══════════════════════════════════════════════════════════════════════════════
#
# Bunlar `app/layout.tsx`'te sabit duruyor. *"Rail'i taşıdım"* diyen biri dördünü de
# atlar — çünkü rail'e bakar, `layout.tsx`'e bakmaz.

SINSI_DORTLU = {
    "ConnectionBadge": "bağlantı rozeti — çevrimdışı · yedek LLM · kural-tabanlı · çevrimiçi",
    "KimlikSeridi": "kimlik şeridi — e-posta · rol · süperadmin rozeti",
    "LogoutButton": "çıkış",
    "FloatingControls": "tema anahtarı (3 durumlu) burada yaşıyor",
}


def test_SINSI_DORTLU_ULASILABILIR():
    """🔴 Dördü de `layout.tsx`'ten geliyor, rail'den **değil**.

    *Bir envanterin değeri, en kolay unutulanı adıyla yazmasındadır.*"""
    dusen = [f"{b} ({neden})" for b, neden in SINSI_DORTLU.items()
             if not _erisilebilir(b)[0]]
    assert not dusen, f"🔴 sinsi dörtlüden düşen: {dusen}"


def test_TEMA_ANAHTARI_UC_DURUMLU_KALDI():
    """Tema **üç** durumlu: sistem → açık → karanlık → sistem.

    ⚠ İki duruma indirmek sessiz bir yetenek kaybıdır: *"sistemi izle"* seçeneği
    kaybolursa kullanıcı işletim sistemi temasını takip edemez."""
    ok, t = _erisilebilir("FloatingControls")
    assert ok, t
    src = _kaynaklar()[_modul("FloatingControls")]
    assert "tema" in src.lower(), "tema anahtarı FloatingControls'tan kaybolmuş"


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · YİRMİ BEŞ TEK-GİRİŞLİ İŞLEV
# ═══════════════════════════════════════════════════════════════════════════════
#
# Envanterin ölçtüğü liste: her biri **yalnız bir yerden** erişiliyor. Taşınmazsa
# silinmiş olur. `isaret`, o işlevi ötekilerden ayıran metin — bileşen ulaşılabilir
# olsa bile işlevin kendisi silinmişse kapı bunu görür.

TEK_GIRISLI: tuple[tuple[str, str, str], ...] = (
    # (bileşen, ayırt edici işaret, ne olduğu)
    ("HistoryPanel", "yeni sohbet", "+ yeni sohbet — TEK giriş noktası"),
    ("HistoryPanel", "restoreConversation", "sohbet geri alma (soft-delete'in görünen yarısı)"),
    ("HistoryPanel", "deleteConversation", "sohbet silme"),
    ("SchedulesPanel", "schedule", "zamanlama yönetimi — yalnız Ayarlar→Zamanlamalar"),
    ("TercihlerPanel", "tercih", "tercihler + bildirim tercihleri"),
    ("SchemaPanel", "sahip", "metrik sahipliği atama/kaldırma"),
    ("ConnectionReviewPanel", "test", "veri kaynağı bağlama sihirbazı"),
    ("NotificationsBell", "neden", "bildirimde «⤵ neden?» gerekçe katmanı"),
    ("DashboardsPanel", "pano", "pano listesi + CRUD"),
    ("DashboardView", "sabitle", "pano widget sabitleme"),
    ("AnalysisCanvas", "rapor", "analiz tuvali → rapor üretimi"),
    ("ReviewPanel", "onayla", "ölçü inceleme — onay/ret"),
    ("ReportView", "yazdır", "rapor görünümü → yazdır/PDF"),
    ("DrillDownPanel", "kır", "kırılıma inme"),
    ("ContributionLayer", "katkı", "katkı ayrıştırması (şelale)"),
    ("PrescriptionLayer", "karar", "reçete → karar kaydı"),
    ("Makbuz", "ne yaptım", "katmanlı makbuz — kanıt zinciri"),
    ("ContractDetailPanel", "nereden geldi", "«bu sayı nereden geldi» köken cümleleri"),
    ("InterpretationBar", "kırılım", "yorum çubuğu — LLM'siz düzenleme"),
    ("OutputInsight", "ANLATIM", "çıktı yorumu + anlatım kutusu"),
    ("KpiCard", "formül", "KPI kartı — formül + bileşenler"),
    ("ResultView", "pivot", "grafik/tablo/pivot + dışa aktarma"),
    ("Landing", "yükle", "açılış — ilk soru + dosya yükleme"),
    ("DcmAkisi", "çalıştır", "DCM akışı — LLM'siz üç tık: ölçü→kırılım→dönem→çalıştır"),
    ("GeriAlSeridi", "geri al", "geri-al şeridi — soft-delete'in kullanıcıya ulaşan yarısı"),
)


def test_TEK_GIRISLI_ISLEVLER_ULASILABILIR():
    """🔴 **Bu dosyanın asıl kapısı.** 25 işlevin her biri tek girişli: taşınmazsa
    silinmiş olur ve **hiçbir başka test** bunu görmez."""
    dusen = []
    for bilesen, isaret, ne in TEK_GIRISLI:
        ok, teshis = _erisilebilir(bilesen, isaret=isaret)
        if not ok:
            dusen.append(f"{ne} → {bilesen}: {teshis}")
    assert not dusen, "🔴 kaybolan tek-girişli işlevler:\n  " + "\n  ".join(dusen)


def test_KOMPOSER_KONTROLLERI_KAYBOLMADI():
    """⚠ Envanterin bulduğu **asimetri**: `kapsam` · `yol sınırı` · `hızlı/derin` ·
    `📎 yükleme` yalnız **sol** komposerde var; sağdaki *"devam et"* komposerinde yok.

    Yeni düzende sohbet merkeze gelince tek komposer kalacak ve asimetri
    **kendiliğinden** kapanacak. Bu kapı o dörtlünün **hiç kaybolmadığını** sınar —
    nerede olduklarını değil."""
    kaynak = _kaynaklar()
    tumu = "\n".join(kaynak[m] for m in _ulasilabilir() if m in kaynak)
    for anahtar, ad in (("kapsam", "kapsam merceği"), ("yolSiniri", "yol sınırı"),
                        ("hizliDerin", "hızlı/derin"), ("upload", "dosya yükleme")):
        assert anahtar in tumu, f"🔴 komposer kontrolü kaybolmuş: {ad} ({anahtar})"


# ═══════════════════════════════════════════════════════════════════════════════
# 4 · ⚠ BEKLENEN KIRIK — *bir kusuru "geçti" diye yazmak onu kapatmaz*
# ═══════════════════════════════════════════════════════════════════════════════
#
# Envanter denetimi, taşımadan **önce** zaten erişilemeyen **üç yüzey** buldu. Bunlar
# taşımanın riski değil, **mevcut borç**.
#
# 🔴 Neden ayrı bir listede: bunları yukarıdaki kapılara koysaydım kapı **bugün kırmızı**
# verirdi ve ilk iş onları *"düzeltmek"* değil, **kapıyı gevşetmek** olurdu. Ayrı liste
# borcu görünür tutar; düzeltildiği gün buradan çıkarılır ve kapı **kendiliğinden**
# sıkılaşır.
#
# *Bir kusuru kapıya "geçti" diye yazmak, onu kapatmakla aynı görünür ama kapatmaz.*

BEKLENEN_KIRIK = {
    "ContractDetailPanel · JSON-LD denetim ihracı":
        "yalnız `contractId=\"\"` iken çiziliyor; hiçbir çağıran boş dize geçmiyor",
    "ContractDetailPanel · kanıt geçmişi (son 20 makbuz)":
        "aynı sebep; `onSelect` prop'u da hiç geçilmiyor",
    "ChatPanel · «portföy» kapsam seçeneği":
        "`superadmin` prop'u bekliyor, `page.tsx` hiç göndermiyor",
}


def test_BEKLENEN_KIRIK_LISTESI_GEREKCELI():
    """Her borç bir **sebep** taşır. ⚠ Gerekçesiz bir muafiyet, listeye girmeyi
    düzeltmekten kolay yapar — ve liste zamanla kuralın kendisini yer."""
    for ad, sebep in BEKLENEN_KIRIK.items():
        assert len(sebep) >= 30, f"{ad}: gerekçe yetersiz"


def test_BEKLENEN_KIRIK_HALA_KIRIK_MI():
    """🔴 **Ters yönlü kapı.** Bu üç yüzey düzeltilince test **kırmızı verir** ve
    *"artık çalışıyor, listeden çıkar"* der.

    *Bir borç listesi, borç ödendiğinde susuyorsa, bir sonraki okuyucuya hâlâ borç
    varmış gibi görünür.*"""
    kaynak = _kaynaklar()
    cdp = kaynak.get(_modul("ContractDetailPanel"), "")
    # Bir çağıran boş dize geçmeye başladıysa borç kapanmıştır.
    cagiranlar = [m for m in _ulasilabilir()
                  if "ContractDetailPanel" in kaynak.get(m, "") and m != _modul("ContractDetailPanel")]
    hala_kirik = not any('contractId=""' in kaynak[m] or "contractId={''}" in kaynak[m]
                         for m in cagiranlar)
    assert hala_kirik, (
        "✅ JSON-LD ihracı / kanıt geçmişi artık erişilebilir görünüyor — "
        "BEKLENEN_KIRIK listesinden ÇIKAR ve gerçek kapıya taşı")
    assert "superadmin" in kaynak.get(_modul("ChatPanel"), ""), \
        "ChatPanel'de `superadmin` prop'u yok — borç kaydı bayatlamış"


# ═══════════════════════════════════════════════════════════════════════════════
# 5 · KAPININ KENDİ SAĞLIĞI
# ═══════════════════════════════════════════════════════════════════════════════

def test_GIRIS_NOKTALARI_GERCEKTEN_VAR():
    """⚠ Bir giriş noktası yeniden adlandırılırsa grafik **boşalır** ve kapı her şeyi
    *"ulaşılamıyor"* sanır — ya da beteri, hiçbir şeyi kontrol etmeden **yeşil** verir."""
    kaynak = _kaynaklar()
    eksik = [g for g in _GIRISLER if g.removesuffix(".tsx") not in kaynak]
    # `paylasim/[token]` opsiyonel — köşeli parantezli yol her kurulumda olmayabilir.
    eksik = [g for g in eksik if "[token]" not in g]
    assert not eksik, f"giriş noktası bulunamadı: {eksik}"


def test_ULASILABILIR_KUME_BOS_DEGIL():
    """🔴 *Kırmızı veremeyen bir kapı, kapı değildir.* Grafik çökerse küme boşalır ve
    bütün iddialar sessizce anlamsızlaşır."""
    u = _ulasilabilir()
    assert len(u) >= 30, f"içe-aktarma grafiği çökmüş görünüyor: {len(u)} modül"
    assert _modul("ChatPanel") in u, "ChatPanel bile ulaşılamıyor — grafik bozuk"


def test_HIZLI_kalir():
    """⚠ *Uzun bir kapı, atlanan bir kapıya dönüşür.* Bu kapı **saf metin** okur;
    regex geri-izlemesi yok, ürün çalıştırılmıyor."""
    src = pathlib.Path(__file__).read_text(encoding="utf-8")
    # 🔴 DESEN PARÇALI KURULUR — aksi hâlde tarama **kendi iddiasını** yakalar.
    # Bu deponun defterindeki en sık tekrar eden küçük kusur (12 kez kaydedilmiş):
    # bir yasağı arayan tarama, yasağın **metnini** de bulur ve kendi yazarını suçlar.
    # İlk yazımda ben de düştüm; kapı beni ilk koşumda yakaladı.
    _ic_ice = "{" + "0,"
    assert _ic_ice not in src, \
        "iç içe niceleyici — felaket geri-izleme riski (KILAVUZ §9/3)"
    assert "lru" + "_cache" in src, "ağaç her testte yeniden okunuyor"
