"""FAZ 7.5 kapısı — **a11y, EK I'nin on kuralı.** [bayraksız: kapı]

## Ölçüldü, varsayılmadı — ve teşhis kısmen DOĞRU çıktı

| kural | yol haritasının iddiası | **ölçüm** |
|---|---|---|
| A11Y-4 | *"bugün **4 kullanım** var"* | ✅ **tam olarak 4** (`AnalysisCanvas` · `DashboardsPanel`×2 · `ReportCard`) |
| A11Y-3 | *"modallerde focus trap"* | 🔴 `focus-trap`/`trapFocus` **0 kullanım** — üç modal `role="dialog"` basıyor, hiçbiri odağı tutmuyordu |
| A11Y-7 | *"her ikon-only buton `aria-label`"* | ◐ 158 butonun **2**'si eksikti (ikisi de `×`, ikisi de yalnız `title` taşıyordu) |
| A11Y-9 | *"renk tek kanal olamaz"* | 🔴 **en ciddisi** — aşağıda |

### 🔴 A11Y-9'un ölçülen ihlali

`opacity-40` deponun içinde **14 kez `disabled:`** ve **14 kez düz** (tıklanabilir)
kullanılıyordu; `opacity-50` için 14/16, `opacity-30` için 2/4. Yani *"soluk ama
tıklanabilir"* ile *"devre dışı"* **birebir aynı pikseli** üretiyordu.

> Kullanıcı hangisinin tıklanabildiğini **deneyerek** öğreniyordu — ve bir arayüzde
> *"denemek"*, bir bilgi kanalı değildir.

⚠ `title` bir `aria-label` **değildir**: dokunmatik cihazda hover yoktur, ekran okuyucu
onu yalnız bazı ayarlarda okur. *Bir etiketi hover'a bağlamak, onu fareye bağlamaktır.*

## ⊘ ÖLÇÜLEMEDİ — ve neden gizlenmiyor

**A11Y-5/A11Y-6'nın gerçek klavye gezinmesi** (Tab sırası, odak görünürlüğü) bir
**tarayıcı** ister; bu kapı statik kaynağı okur. Burada ölçülen şey *"tuzağın kurulu
olduğu"*dur, *"çalıştığı"* değil. **Bu bir sınırdır, bir geçiş değil.**
"""

from __future__ import annotations

import re

import pytest

from tests.kapi_ortak import fe_dosyalari, fe_kaynak

#: `<button …>iç</button>` — attribute'lar ve görünür içerik ayrı yakalanır.
_BTN = re.compile(r"<button\b(?P<attrs>[^>]*?)>(?P<ic>.*?)</button>", re.S)

#: Modal sayılan bileşenler: `role="dialog"` basan **ve** kalıcı olarak açılan yüzeyler.
#: ⚠ `Select`/`ResultView`'ün `fixed inset-0`'ı bir **tıklama-perdesi**dir (dropdown
#: kapatıcı), modal değil — ikisini aynı kefeye koymak kapıyı yanlış yerde kırmızı yapardı.
_MODALLER = ("DrillDownPanel.tsx", "ContractDetailPanel.tsx", "SettingsDrawer.tsx",
             "AdSor.tsx")


def _gorunur_metin(ic: str) -> str:
    return re.sub(r"<[^>]+>", "", ic).strip()


# --- A11Y-4: `window.prompt()` birincil yüzey DEĞİL -----------------------------------

def test_A11Y4_window_prompt_BIRINCIL_YUZEY_DEGIL():
    """🔴 `window.prompt` **hata gibi görünmez, iptal gibi görünür**: tarayıcı onu
    bastırdığında (iframe, arka plan sekmesi) çağrı `null` döner ve kullanıcı panonun
    neden oluşmadığını **asla öğrenemez**.

    ⚠ Tarama **yorumsuz** kaynakta: `AdSor.tsx`'in kendi belgesi `window.prompt`'tan
    söz eder ve bu operasyonda metin taramaları **kendi belgesini** altı kez yakaladı.
    """
    kaynak = fe_kaynak()  # yorumlar ayıklanmış
    assert "window.prompt(" not in kaynak, (
        "🔴 `window.prompt()` geri gelmiş. EK I/A11Y-4: stillenemez (karanlık modda "
        "beyaz sistem kutusu), ana iş parçacığını kilitler, doğrulama yapamaz ve "
        "tarayıcı tarafından SESSİZCE bastırılabilir. Yerine `useAdSor()`.")


def test_A11Y4_YERINE_GECEN_yuzey_ERISILEBILIR():
    """Yasak koymak yetmez — **yerine geçen** yüzeyin kendisi kurallı olmalı."""
    src = fe_dosyalari()["components/AdSor.tsx"]
    for beklenen in ('role="dialog"', 'aria-modal="true"', "aria-labelledby",
                     "useOdakTuzagi"):
        assert beklenen in src, f"🔴 `AdSor` eksik: {beklenen}"


def test_A11Y4_IPTAL_ANLAMI_KAYMADI():
    """⚠ `null` = iptal — `window.prompt` ile **aynı**. Çağıranların mevcut
    `if (!title) return` kontrolleri geçerli kalmalı; sessiz bir anlam kayması, dört
    çağrı yerinde birden sessiz bir hata olurdu."""
    src = fe_dosyalari()["components/AdSor.tsx"]
    assert "Promise<string | null>" in src


@pytest.mark.parametrize("dosya", ["components/AnalysisCanvas.tsx",
                                   "components/DashboardsPanel.tsx",
                                   "components/ReportCard.tsx"])
def test_A11Y4_DORT_CAGRI_YERI_de_gecti(dosya):
    """🔴 *Bir yüzeyi üç yerde değiştirip dördüncüsünü bırakmak, hiç değiştirmemekten
    kötüdür*: kullanıcı aynı işi iki farklı kutuyla yapar."""
    src = fe_dosyalari()[dosya]
    assert "useAdSor" in src and "adSorAlani" in src, (
        f"🔴 {dosya} `useAdSor` kullanıyor ama kutuyu **render etmiyor** — söz hiç "
        f"çözülmez ve çağıran sonsuza kadar bekler.")


# --- A11Y-3 / A11Y-6: odak tuzağı -----------------------------------------------------

@pytest.mark.parametrize("dosya", _MODALLER)
def test_A11Y3_MODALLER_odak_tuzagi_kullanir(dosya):
    """🔴 Ölçüldü: `focus-trap`/`trapFocus` deponun **hiçbir yerinde** yoktu."""
    src = next(v for k, v in fe_dosyalari().items() if k.endswith(dosya))
    assert "useOdakTuzagi" in src, (
        f"🔴 {dosya} odağı tutmuyor — Tab, modalin **arkasındaki** sayfaya kaçar ve "
        f"ekran okuyucu kapalı bir yüzeyi okumaya devam eder.")


def test_A11Y3_TUZAGIN_TEK_SAHIBI_var():
    """🔴 *Aynı kuralın iki sahibi ayrışır* — bu deponun en sık tekrarlayan kusur sınıfı.

    Üç modal **kendi** Esc dinleyicisini yazıyordu; dördü de `shift+Tab`'ı unutabilirdi
    ve **hangisinin doğru olduğu ölçülemez** hâle gelirdi.
    """
    dosyalar = fe_dosyalari()
    sahipler = [y for y, s in dosyalar.items()
                if "addEventListener" in s and '"Escape"' in s and "odakTuzagi" not in y]
    assert not sahipler, (
        f"🔴 Modal dışında elle yazılmış Esc dinleyicisi: {sahipler}. Kural TEK yerde "
        f"(`lib/odakTuzagi.ts`) yazılır.")


def test_A11Y3_ODAK_GERI_VERILIYOR():
    """⚠ *Odağı geri vermek, açmaktan daha kolay unutulur* — çünkü açılış **görünür**,
    kapanış görünmez. Kullanıcı listedeki yerini kaybederse modal kapanmış sayılmaz."""
    src = fe_dosyalari()["lib/odakTuzagi.ts"]
    assert "cagiran" in src and "isConnected" in src, (
        "🔴 Kapanışta odak çağırana dönmüyor ya da silinmiş bir ögeye odaklanılıyor "
        "(odak sessizce `<body>`'ye düşer).")


def test_A11Y3_KAPALIYKEN_tuzak_KURULMAZ():
    """🔴 `SettingsDrawer` durumludur (`open`): kapalıyken tuzak kurulursa **arkadaki
    sayfa klavyeyle gezilemez** hâle gelir — erişilebilirlik adına erişilebilirliği
    kırmak."""
    src = fe_dosyalari()["components/SettingsDrawer.tsx"]
    assert "useOdakTuzagi<HTMLElement>(open," in src


def test_A11Y5_ESC_ve_ENTER_fareye_bagimli_DEGIL():
    """A11Y-5: fareye **zorunlu** bağımlılık yok."""
    tuzak = fe_dosyalari()["lib/odakTuzagi.ts"]
    adsor = fe_dosyalari()["components/AdSor.tsx"]
    assert '"Escape"' in tuzak and '"Tab"' in tuzak
    assert '"Enter"' in adsor, "🔴 Ad kutusu Enter ile onaylanamıyor"


# --- A11Y-2 / A11Y-7: etiketsiz glif butonu yok ---------------------------------------

def test_A11Y7_GORUNUR_METNI_OLMAYAN_buton_aria_label_TASIR():
    """🔴 `title` bir `aria-label` **değildir**: dokunmatik cihazda hover yoktur.
    *Bir etiketi hover'a bağlamak, onu fareye bağlamaktır.*"""
    eksik = []
    for yol, kaynak in fe_dosyalari().items():
        for m in _BTN.finditer(kaynak):
            metin = _gorunur_metin(m.group("ic"))
            harf = re.sub(r"[^0-9A-Za-zçğıöşüÇĞİÖŞÜ]", "", metin)
            if len(harf) >= 3:
                continue  # okunabilir bir metni var — etiket zaten metnin kendisi
            if "aria-label" not in m.group("attrs"):
                eksik.append(f"{yol}: {metin[:20]!r}")
    assert not eksik, (
        "🔴 Görünür metni olmayan ama `aria-label` taşımayan buton(lar):\n  "
        + "\n  ".join(eksik))


#: 🔴 **EMOJİ**, tipografik glif DEĞİL. Bu ayrım kapıyı yazarken **ölçümle** öğrenildi:
#: ilk sürüm `✕` ve `?`'i de yakaladı ve beş yanlış-pozitif verdi. `✕`/`×`/`?` bir
#: **yazı karakteridir**; her yazı tipinde aynı çizilir, kültürler arası okunur ve
#: "kapat"/"yardım" anlamı otuz yıllık bir yerleşiktir. 🔔/📎/🕐 ise **resimdir**:
#: platforma göre farklı çizilir ve anlamı **tahmin edilir**. A11Y-1'in hedefi budur.
#:
#: \u26A0 **\u0130kinci daraltma, yine \u00F6l\u00E7\u00FCmle.** \u0130lk regex `\U00002600-\U000027BF`'\u0131 (Dingbats)
#: b\u00FCt\u00FCn olarak ald\u0131 ve `\u2715` (U+2715) o aral\u0131ktad\u0131r \u2014 yani kap\u0131, kendi gerek\u00E7esiyle
#: **\u00E7eli\u015Fiyordu**. Yaz\u0131 glifleri bu y\u00FCzden **ad\u0131yla** d\u0131\u015Flan\u0131yor: bir aral\u0131\u011F\u0131n ad\u0131
#: ("Dingbats") i\u00E7eri\u011Finin ne oldu\u011Funu s\u00F6ylemez.
_YAZI_GLIFLERI = "\u2715\u2713\u2717\u00D7\u2192\u2190\u2191\u2193\u21E7\u2318\u22EE\u2026\u00B7"
_EMOJI = re.compile(
    r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F0FF\uFE0F]")


def test_A11Y1_ISLEVSEL_KONTROL_yalniz_EMOJI_olamaz():
    """A11Y-1 — ve bu, A11Y-7'nin **aynısı değildir**: `aria-label`'lı bir emoji butonu
    ekran okuyucuya konuşur ama **gören** kullanıcıya hâlâ bir bilmecedir.

    ⚠ **Kapının kendisi bir kez daraltıldı** ve gerekçesi yukarıda yazılı: tipografik
    glif (`✕` `×` `?`) bir emoji değildir. *Bir kuralı gereğinden geniş yazmak, onu
    kırmızıya boğup güvenilmez yapar — ve güvenilmeyen bir kapı, olmayan bir kapıdır.*
    """
    eksik = []
    for yol, kaynak in fe_dosyalari().items():
        for m in _BTN.finditer(kaynak):
            metin = _gorunur_metin(m.group("ic"))
            sade = "".join(c for c in metin if c not in _YAZI_GLIFLERI)
            if not _EMOJI.search(sade):
                continue
            harf = re.sub(r"[^0-9A-Za-zçğıöşüÇĞİÖŞÜ]", "", metin)
            if len(harf) >= 3:
                continue  # emoji + okunabilir metin — emoji tek başına taşımıyor
            if "title=" not in m.group("attrs"):
                eksik.append(f"{yol}: {metin[:20]!r}")
    assert not eksik, (
        "🔴 Yalnız **emoji** taşıyan ve hover ipucu OLMAYAN buton(lar) — emoji platforma "
        "göre farklı çizilir ve anlamı TAHMİN EDİLİR:\n  " + "\n  ".join(eksik))


def test_A11Y8_RAIL_ikonlari_ETIKET_ve_TOOLTIP_tasir():
    """A11Y-8 rail için **ikisini birden** ister: `aria-label` **ve** hover ipucu.

    Ölçüldü: altı rail düğmesinin **dördü** `title` taşıyordu, *Yardım* ve *Ayarlar*
    taşımıyordu. ⚠ *Bir kuralın %67'si, o kuralın uygulanmadığı anlamına gelir* — çünkü
    kullanıcı hangi ikonun ipucu vereceğini önceden bilemez ve **hepsine güvenmez**.
    """
    src = fe_dosyalari()["components/FloatingControls.tsx"]
    eksik = [m.group(0)[:60] for m in _BTN.finditer(src)
             if "aria-label" in m.group("attrs") and "title=" not in m.group("attrs")]
    assert not eksik, f"🔴 Rail düğmesi `aria-label` taşıyor ama tooltip YOK: {eksik}"


# --- A11Y-9: renk/opaklık TEK KANAL olamaz --------------------------------------------

def test_A11Y9_DEVRE_DISI_ile_SOLUK_ayni_TOKENI_paylasmaz():
    """🔴 **EK I'nin en ciddi ihlaliydi.** Ölçüm: `opacity-40` **14 kez `disabled:`**,
    **14 kez düz**; `opacity-50` 14/16; `opacity-30` 2/4.

    *Kullanıcı hangisinin tıklanabildiğini **deneyerek** öğreniyordu — ve bir arayüzde
    "denemek" bir bilgi kanalı değildir.*
    """
    kaynak = fe_kaynak()
    sayisal = sorted(set(re.findall(r"disabled:opacity-(\d+)", kaynak)))
    assert not sayisal, (
        f"🔴 `disabled:` hâlâ **sayısal** opaklık kullanıyor: {sayisal}. Aynı sayı düz "
        f"(tıklanabilir) bir ögede de geçtiği anda iki durum **birebir aynı pikseli** "
        f"üretir. Devre dışı olan `var(--opacity-disabled)` üzerinden gider.")


def test_A11Y9_TOKEN_DEGERLERI_CAKISMIYOR():
    """⚠ İki ayrı token yazıp **aynı değeri** vermek, sorunu bir dolaylama katmanının
    altına saklamaktır."""
    from tests.kapi_ortak import frontend_dir
    # ⚠ `fe_dosyalari()` yalnız `.ts*` okur — CSS onun dışındadır ve bunu varsaymak
    # kapıyı `KeyError` ile kırmızı yapmıştı (ölçüm aracının kendisi de bir bağımlılıktır).
    css = (frontend_dir() / "app/globals.css").read_text(encoding="utf-8")
    d = re.search(r"--opacity-disabled:\s*([\d.]+)", css)
    s = re.search(r"--opacity-soluk:\s*([\d.]+)", css)
    assert d and s, "🔴 iki opaklık token'ından biri yok"
    assert float(d.group(1)) != float(s.group(1)), (
        "🔴 `--opacity-disabled` ile `--opacity-soluk` **aynı değerde** — iki isim, tek "
        "piksel; ayrım yine yok.")


def test_A11Y9_IKINCI_KANAL_var():
    """🔴 Opaklık **tek kanal olamaz** (K6). Renk-körü ya da düşük kontrastlı bir ekranda
    %38 ile %62 ayırt edilemez; `cursor-not-allowed` ikinci kanaldır."""
    for yol, kaynak in fe_dosyalari().items():
        if "disabled:opacity-[var(--opacity-disabled)]" not in kaynak:
            continue
        assert "disabled:cursor-not-allowed" in kaynak, (
            f"🔴 {yol}: devre dışı yalnız **opaklıkla** bildiriliyor — ikinci kanal yok.")


def test_A11Y9_HATA_METNI_de_var_renk_TEK_kanal_degil():
    """`AdSor`'un doğrulama hatası yalnız kenarlık rengiyle bildirilseydi, kırmızı-yeşil
    körü bir kullanıcı **hiçbir şey** görmezdi."""
    src = fe_dosyalari()["components/AdSor.tsx"]
    assert "aria-invalid" in src and "aria-describedby" in src
    assert "En çok" in src, "🔴 sınır aşımı METİNLE söylenmiyor"


# --- Sınırın kendisi kilitli ----------------------------------------------------------

def test_OLCULEMEYEN_kisim_YAZILI():
    """⊘ *Ölçülemeyen bir şeyi ölçülmüş göstermek, ölçmemekten kötüdür.*"""
    from pathlib import Path
    assert "⊘ ÖLÇÜLEMEDİ" in Path(__file__).read_text(encoding="utf-8")
