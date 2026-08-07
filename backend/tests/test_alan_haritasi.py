"""🔴 `G0b.9b` — **ALAN HARİTASI**: garson ile mutfak karışmaz.

## Neden bu kapı

Garson ara fazı iki katmanı birbirine yaklaştırıyor. Karıştırılan her sınır, bu deponun
adını koyduğu kusuru doğurur: **aynı kuralın iki sahibi**. Ayrım testi üç soru:

    ① DOĞAL DİL okuyor/yazıyor mu?           → GARSON
    ② VERİ / SORGU / MOTOR ile mi çalışıyor?  → MUTFAK
    ③ İKİSİ DE mi? → 🔴 KAPI olmak ZORUNDA.
                       Kapı olmayan bir "ikisi de" tanımı gereği bir KUSURDUR.

## ⚠ Bu kapı bir «kimse dokunmasın» kapısı DEĞİL

Sınıflandırma **listelidir ve gerekçelidir**; yeni bir modül eklenince listeye
yazılması gerekir. `test_modul_buyume.py`'nin muafiyet-listesi deseni: *sınıfsız modül
bırakılamaz* — çünkü sınıfsız bir modül, sınırı **düşünülmemiş** bir moduldür.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

APP = pathlib.Path(__file__).resolve().parents[1] / "app"

#: 🗣 GARSON — dil okur/yazar, **hiçbir şey çalıştırmaz**.
GARSON = {
    "niyet.py", "turetme.py", "typo_onerisi.py", "followup.py", "context.py",
    "donem_capasi.py", "netlestirme.py", "belirsizlik_chipi.py", "soz.py",
    "intent_semasi.py", "kapsam.py", "embed_kapsam.py", "yetenek.py",
    "temellendirme.py",   # G1 — CubeQuery → "anladığım şu" (0 LLM, motora dokunmaz)
    "diyalog.py",         # G2 — slot durumu; saf fonksiyon, LLM YOK, motora dokunmaz
    "ek.py",              # G7 — Türkçe ek ÜRETİMİ (doğrulama değil); saf, LLM YOK
    "sinonim_onerici.py", "archetypes.py", "starters.py",
}

#: 🍳 MUTFAK — veri/sorgu ile çalışır, **dil bilmez**.
MUTFAK = {
    "wren_service.py", "compose.py", "contracts.py", "rls.py", "fanout.py",
    "katman_b.py", "stats.py", "contribution.py", "yoy.py", "kpi.py",
    # G6 — `yoy.py`'nin İKİZİ: filtre listesi üstünde saf cebir (çökmüş iki-dönem
    # aralığını `mom`/`yoy` bazına geri açar). Dil okumaz, motora dokunmaz; girdisi
    # bir CubeQuery parçası, çıktısı bir CubeQuery parçası — tanım gereği mutfak.
    "kiyas_cebiri.py",
    "statements.py", "drill.py", "audit_zinciri.py", "lineage.py", "tazelik.py",
    "veri_araligi.py", "result_shape.py", "sensitivity.py",
}

#: 🍳 modüllerin ASLA import edemeyeceği 🗣 modüller — *"mutfak dil ayrıştıramaz"*.
DIL_MODULLERI = {"llm", "soz", "followup", "niyet", "turetme", "typo_onerisi",
                 "belirsizlik_chipi", "netlestirme", "intent_semasi"}

#: 🗣 modüllerin ASLA import edemeyeceği motor yüzeyleri — *"garson çalıştıramaz"*.
MOTOR_MODULLERI = {"wren_service", "katman_b", "compose"}

#: ⚠ GEREKÇELİ MUAFİYETLER — kapı bunları GÖRÜR ve geçirir; **gizlemez**.
#:
#: Bir muafiyet bir çözüm değildir; **görünür bırakılmış bir borçtur**. Listeye giren
#: her satır ya bir sonraki fazda kapanır ya kalıcı gerekçesini yanında taşır.
MUAF_GECISLER = {
    # 🔴 Ölçüldü (G0b, 2026-08-07): `wren_service.py:552,825` → `from app.llm import _norm`.
    # `_norm` bir METİN NORMALLEŞTİRİCİDİR, bir dil anlama yüzeyi değil — ama evi
    # `llm.py` olduğu için mutfak dil modülüne uzanmış görünüyor. Gerçek çözüm `_norm`'u
    # ortak bir yardımcıya taşımak; o **bu fazın konusu değil**. Kapı görüyor, biz
    # adlandırıyoruz: *sınır kokusu var ve kayıtlı.*
    ("wren_service.py", "llm"),
}


def _importlar(dosya: pathlib.Path) -> set[str]:
    agac = ast.parse(dosya.read_text(encoding="utf-8"))
    out: set[str] = set()
    for d in ast.walk(agac):
        if isinstance(d, ast.Import):
            out |= {a.name.split(".")[-1] for a in d.names}
        elif isinstance(d, ast.ImportFrom) and d.module:
            parca = d.module.split(".")
            if parca[0] == "app" and len(parca) > 1:
                out.add(parca[1])
            out.add(parca[-1])
    return out


@pytest.mark.parametrize("ad", sorted(GARSON))
def test_GARSON_motora_dokunamaz(ad):
    """🗣 Garson **sorgu çalıştırmaz**. `route()` bile motora dokunmaz — o yüzden
    garsonun kulağıdır, aşçının tezgâhı değil."""
    yol = APP / ad
    if not yol.exists():
        pytest.skip(f"{ad} henüz yok")
    ihlal = _importlar(yol) & MOTOR_MODULLERI
    assert not ihlal, f"🔴 GARSON modülü {ad} motora dokunuyor: {sorted(ihlal)}"


@pytest.mark.parametrize("ad", sorted(MUTFAK))
def test_MUTFAK_dil_ayristiramaz(ad):
    """🍳 Mutfak **doğal dil bilmez**. Bir mutfak modülü `soz`/`followup` import
    ediyorsa, ya yanlış sınıflandırılmıştır ya bir sınır sızmıştır."""
    yol = APP / ad
    if not yol.exists():
        pytest.skip(f"{ad} henüz yok")
    ihlal = {m for m in _importlar(yol) & DIL_MODULLERI
             if (ad, m) not in MUAF_GECISLER}
    assert not ihlal, f"🔴 MUTFAK modülü {ad} dil modülü import ediyor: {sorted(ihlal)}"


def test_SINIFSIZ_MODUL_BIRAKILAMAZ():
    """🔴 Yeni bir modül eklenip haritaya yazılmazsa **CI kırmızı**.

    Sınıfsız bir modül, sınırı **düşünülmemiş** bir modüldür. Muafiyet listesi
    gerekçelidir: her satır ya bir sınıfa girer ya **neden girmediğini** söyler.
    """
    #: Sınıflandırma DIŞI — gerekçeleriyle. (🚪 kapı · 🌉 köprü · altyapı · teslim)
    MUAF = {
        # 🚪 KAPI — ikisinin arasında durur, ikisine de ait değildir
        "llm_guard.py": "🚪 çıkış kapısı — `safe_call`, fail-closed",
        "yayilim.py": "🚪 korunan yayılım — perdeleme/geri koyma (G0b)",
        "narration_guard.py": "🚪 metin→SAYI kapısı",
        # 📊 TELEMETRİ — kapıların KENDİSİNİ ölçer, hiçbir karara girmez.
        # `Ö5`: guard'lar fail-closed düştüğünde sistem "soğur" ama HİÇBİR ŞEY hata
        # vermez; bu modül o sessizliği bir sayıya çevirir. Ne dil okur ne sorgu kurar —
        # yalnız iki kapının çıktısını sayar. *Ölçen bir modül, ölçtüğü tarafa ait
        # değildir; aksi hâlde kendi sonucunu etkiler.*
        "guard_alarmi.py": "📊 telemetri — guard düşme oranı (Ö5), karara girmez",
        "iddia.py": "🚪 metin→İDDİA kapısı (G4) — §4'ün değişmezinin ikinci yarısı",
        "uyum.py": "🚪 niyet↔sorgu uyum kapısı (beyan-açık)",
        "pii.py": "🚪 maskeleme, tek çıkış",
        "planner.py": "🚪 dört kapı (kayıt·yetki·det-önce·bütçe)",
        "tools.py": "🚪 araç kaydı",
        "cube_router.py": "🚪+🗣 route() garson · parse_cube_query KAPI — bilinçli, §1.2c",
        "answer.py": "🚪 KAPANIŞ ZİNCİRİ — her cevap `seal()`'den geçer",
        "llm.py": "🗣 sağlayıcı katmanı — garsonun ağzı ve kulağı; ama `safe_call`'ı da "
                  "barındırdığı için KAPI'ya da dokunur (tek çıkış geçidi orada sarılı)",
        # 🌉 KÖPRÜ — biri üretir, öteki tüketir
        "interpret.py": "🌉 mutfak üretir, garson tüketir (ham satır SIZDIRMAZ)",
        "value_index.py": "🌉 veri değeri okur, garson kullanır",
        # 🔴 `G0b.6` — `value_index`'in KARDEŞİ ve aynı sınıf: veri değerlerini okur
        # (`sensitivity` süzgeciyle) ama onları **garson için** perdeler. Sayı hesaplamaz,
        # SQL yazmaz, katalog dışına çıkmaz — köprünün tanımı budur.
        "varlik.py": "🌉 veri değeri okur, garson için PERDELER",
        "vqr.py": "🌉 soru→sorgu belleği",
        # 🎨 SUNUM
        "viz.py": "🎨", "report.py": "🎨", "prescribe.py": "🎨", "fmt.py": "🎨",
        "viz_email.py": "🎨", "email_render.py": "🎨", "gorsel_ekleme.py": "🎨",
        "result_shape.py": "🎨",
    }
    hepsi = {p.name for p in APP.glob("*.py")} - {"__init__.py"}
    sinifli = GARSON | MUTFAK | set(MUAF)
    # Altyapı/teslim/yetki katmanı: bu fazın konusu değil, ayrı sahipleri var.
    ALTYAPI_ONEKLERI = (
        "main", "config", "logging_setup", "features", "schemas", "channels",
        "bildirim", "paylasim", "kanal_", "schedules", "eylem", "onay_", "yazma_",
        "eskalasyon", "decision", "hedef", "kpi_pin", "arkaplan_", "istek_",
        "ask_jobs", "mcp", "ossie", "cekirdek", "tercih", "bayrak_", "mali_",
        "rules", "discovery_kuyrugu", "terfi_", "kademeli_", "materialize",
        "db_introspect", "mdl_writer", "packs", "company_registry", "coldstart",
        "dataset", "adhoc_cube", "metrik_kaydi", "certification", "sertifika_",
        "sinonim", "kpi_", "starters", "kapsam", "embed_",
    )
    kalan = {a for a in hepsi - sinifli if not a.startswith(ALTYAPI_ONEKLERI)}
    assert not kalan, (
        f"🔴 SINIFSIZ MODÜL: {sorted(kalan)}\n"
        "Her modül ya 🗣 GARSON, ya 🍳 MUTFAK, ya MUAF (kapı/köprü/sunum) olmalı.\n"
        "Sınıfsız bir modül, sınırı DÜŞÜNÜLMEMİŞ bir modüldür — yol haritası §1.2c.")


def test_YAYILIM_llm_guardin_KOPYASI_DEGIL():
    """🔴 `G0b`'nin kendi dersi: perdeleme `llm_guard`'a yazılmıştı ve
    `test_DESEN_SOZLUGU_KOPYALANMAMIS` **haklı olarak** kırmızı verdi.

    İki ayrı soru, iki ayrı sahip: *"bu yük çıkabilir mi"* ≠ *"ne perdelenecek"*.
    """
    guard = (APP / "llm_guard.py").read_text(encoding="utf-8")
    assert "re.compile" not in guard, "llm_guard'a yine regex sızmış"
    assert "def perdele" not in guard, "perdeleme llm_guard'a geri taşınmış"
    yayilim = (APP / "yayilim.py").read_text(encoding="utf-8")
    assert "def perdele" in yayilim and "def geri_koy" in yayilim
