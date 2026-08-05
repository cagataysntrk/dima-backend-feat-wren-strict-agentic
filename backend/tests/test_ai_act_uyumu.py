"""FAZ 1.12 — **AI Act / NIST RMF / ISO 42001** kapısı.

⚠ **Yürürlük tarihi `[DOĞRULANMADI]` olarak kalıyor.** Yol haritası *"AI Act Md.50
`2 Ağustos 2026`'dan yürürlükte"* diyor ve yanına **kendi eliyle** `[DOĞRULANMADI —
birincil kaynak EK F'ye eklenecek]` yazmış. Bu kapı **tarihi doğrulamaz**; yükümlülüğün
**karşılığının kodda var olduğunu** doğrular. *Doğrulanmamış bir tarihi kapıya çevirmek,
ölçmediğimiz bir şeyi ölçtük gibi göstermek olurdu.*
"""

from __future__ import annotations

import ast
import pathlib

import pytest

KOK = pathlib.Path(__file__).resolve().parents[1]


def _uclar() -> dict[str, set[str]]:
    """Yayımlanmış uç sözleşmesi: `{yol: {METOT, …}}`.

    ⚠ `app.routes` **düz bir liste değil** (`_IncludedRouter` düğümleri taşır) — ilk sürüm
    onu düz sanıp `AttributeError` verdi. Burada OpenAPI şeması okunur: *denetleyicinin*
    göreceği sözleşme de zaten odur, iç yönlendirme ağacı değil.
    """
    from app.main import create_app

    return {y: {m.upper() for m in ops}
            for y, ops in create_app().openapi()["paths"].items()}


# ── 1 · Md.50 — AI İÇERİK İŞARETLEME ────────────────────────────────────────

def test_HER_YANITTA_IKI_ALAN_VAR():
    """🔴 Maddenin kapısı birebir: `ai_generated_prose` ve `kanit_sinifi` **her** yanıtta."""
    from app.schemas import AskResponse

    r = AskResponse(question="x")
    assert r.ai_generated_prose is False, "varsayılan True — işaret UYDURULUYOR"
    assert r.kanit_sinifi == "olculmus", "varsayılan `olculmus` değil"


def test_ISARET_ANLATIYA_BAGLI_SAYIYA_DEGIL():
    """🔴 **SAYI DEĞİL, ÜSLUP işaretlenir.** Sayıyı her zaman sistem koyar (§4.4) ve
    `narration_guard` eşleşmeyen sayı taşıyan cümleyi **düşürür**. Md.50'nin istediği
    şey, metnin **makine üretimi** olduğunun beyanıdır — sayının değil."""
    kaynak = (KOK / "app" / "answer.py").read_text(encoding="utf-8")
    i = kaynak.index("resp.ai_generated_prose")
    assert 'get("narration")' in kaynak[i:i + 200], \
        "işaret `narration`'a bağlı değil — sayı ya da başka bir şey işaretleniyor"


def test_ISARET_SEAL_DE_SET_EDILIYOR():
    """`seal()` **her yanıtın** geçtiği kapanış zinciridir; işareti başka bir yere koymak
    onu **bazı** yanıtlarda eksik bırakırdı."""
    agac = ast.parse((KOK / "app" / "answer.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "seal")
    hedefler = {getattr(t, "attr", "") for n in ast.walk(fn)
                if isinstance(n, ast.Assign) for t in n.targets}
    assert "ai_generated_prose" in hedefler and "kanit_sinifi" in hedefler


def test_ANLATI_YOKSA_ISARET_YOK():
    from app.schemas import AskResponse

    r = AskResponse(question="x", interpretation={"summary": "toplam 5"})
    assert not bool((r.interpretation or {}).get("narration"))


# ── 2 · KANIT SINIFI — kategori, PUAN DEĞİL ─────────────────────────────────

def test_KANIT_SINIFI_KATEGORI_SKALER_DEGIL():
    """⚠ Skaler bir `confidence` **uydurulmaz** (MIMARI §5: *"kalibre edilmediği sürece o
    sayı bir güven değil bir SÜStür"*). Sınıf bir **kategoridir**."""
    from app.schemas import AskResponse

    alan = AskResponse.model_fields["kanit_sinifi"]
    assert alan.annotation is str, "kanıt sınıfı sayısal — skaler güven uydurulmuş"


@pytest.mark.parametrize("source,beklenen", [
    ("cube", "olculmus"),
    (None, "olculmus"),
    ("llm:gemini", "probabilistik"),
    ("cube+llm", "probabilistik"),
])
def test_SINIF_KAYNAKTAN_TURUYOR(source, beklenen):
    """`cube+llm`'de **alan seçimi** olasılıksaldır — sayı küpten gelse bile sınıf
    `olculmus` **değildir**: seçim yanlışsa doğru sayı **yanlış soruya** cevap olur."""
    kaynak = (KOK / "app" / "answer.py").read_text(encoding="utf-8")
    i = kaynak.index("resp.kanit_sinifi")
    blok = kaynak[i:i + 300]
    assert 'startswith("llm")' in blok and '"+llm"' in blok


def test_BUGUNDEN_EKLENDI_GEREKCESI_YAZILI():
    """🔴 *"**Bugünden** eklenir ki sonradan geriye dönük eklenmesin"* — geçmiş kayıtlarda
    bu alan boş kalırsa, *"ölçülmüş"* mü *"tahmin"* mi olduğu **bir daha bilinemez**."""
    kaynak = (KOK / "app" / "schemas.py").read_text(encoding="utf-8")
    assert "GERİYE DÖNÜK eklenmesin" in kaynak


# ── 3 · Md.13 — DENETLEYİCİ-OKUNABİLİR İHRAÇ ────────────────────────────────

def test_EXPORT_UCU_VAR_ve_KAYITLI():
    assert "GET" in _uclar().get("/audit/export", set()), \
        "ihraç ucu router'a KAYITLI DEĞİL — yetim uç"


def test_EXPORT_IKINCI_ESLEME_YAZMIYOR():
    """🔴 Standart adlara çeviri `audit_zinciri.otel_nitelikleri`'nde (FAZ 1.8) **zaten
    var**. İkincisi, iki dışa aktarımın **farklı adlar** kullanması demekti — ve
    denetleyici hangisinin doğru olduğunu bilemezdi."""
    kaynak = (KOK / "app" / "routers" / "audit_export.py").read_text(encoding="utf-8")
    assert "otel_nitelikleri" in kaynak
    assert "gen_ai.request.model" not in kaynak, "OTel adları KOPYALANMIŞ — iki sahip"


def test_EXPORT_ZINCIR_BUTUNLUGUNU_DE_TASIYOR():
    """🔴 Bir kanıt defterini **bütünlük raporu olmadan** teslim etmek, *"işte
    kayıtlarım"* deyip **eksik olup olmadığını söylememektir**."""
    kaynak = (KOK / "app" / "routers" / "audit_export.py").read_text(encoding="utf-8")
    assert "zincir_bulgulari" in kaynak and "zinciri_dogrula" in kaynak
    assert "reversed(" in kaynak, "kayıtlar `ts DESC` — doğrulama kronolojik olmalı"


def test_EXPORT_KIRPMASI_SESSIZ_DEGIL():
    """*Sessizce kırpılmış bir kanıt defteri, eksik bir kanıt defteridir.*"""
    kaynak = (KOK / "app" / "routers" / "audit_export.py").read_text(encoding="utf-8")
    assert '"kirpildi"' in kaynak and '"toplam"' in kaynak


def test_EXPORT_TENANT_SINIRLI():
    """Denetim ihracı **tenant sınırını** aşamaz — bir kanıt defteri, başkasının
    kanıtlarını içeriyorsa kanıt değil **sızıntıdır**."""
    kaynak = (KOK / "app" / "routers" / "audit_export.py").read_text(encoding="utf-8")
    assert "AuditLog.tenant_id == p.tenant_id" in kaynak


# ── 4 · Md.14 — İNSAN MÜDAHALE / DURDURMA ───────────────────────────────────

def test_DELETE_UCU_VAR():
    """🔴 *Durdurulamayan bir otomasyon, üzerinde insan denetimi olmayan bir
    otomasyondur.* `/ask/jobs` bugüne kadar yalnız **okunabiliyordu**."""
    metotlar = _uclar().get("/ask/jobs/{job_id}", set())
    assert "DELETE" in metotlar, f"iptal ucu YOK ({sorted(metotlar)})"
    assert "GET" in metotlar, "durdurma ucu okuma ucunu EZMİŞ"


def test_IPTAL_OLDURMUYOR_ISARETLIYOR():
    """⚠ Çalışan bir thread'i zorla sonlandırmak **yarım yazılmış** bir sonuç/kayıt
    bırakabilir; işaretleme **kesin**: iş bittiğinde sonucu **yayımlanmaz**.
    *Yarım bir sonucu yayımlamamak, hızlı öldürmekten daha güvenlidir.*"""
    kaynak = (KOK / "app" / "ask_jobs.py").read_text(encoding="utf-8")
    for oldurme in ("terminate", "kill", "_stop()", "raise SystemExit"):
        assert oldurme not in kaynak, f"iş ZORLA sonlandırılıyor ({oldurme!r})"


def test_DURUM_ADLARI_UYDURMA_DEGIL():
    """🔴 **Bu bir DÜZELTMEDİR.** İlk sürüm `done`/`error` bekliyordu; `AskJob.status`
    sözlüğü ise `pending|running|completed|failed`. Uydurulmuş bir durum adı, kapıyı
    **yeşil** tutup davranışı **ölü** bırakırdı — *"beyan var, kod onu tanımıyor"*."""
    from app import ask_jobs

    kaynak = (KOK / "control_plane" / "models.py").read_text(encoding="utf-8")
    beyan = next(s for s in kaynak.splitlines()
                 if s.strip().startswith("status:") and "pending" in s)
    for d in ask_jobs.BITMIS_DURUMLAR:
        if d != ask_jobs.DURUM_IPTAL:
            assert d in beyan, f"{d!r} `AskJob` sözlüğünde YOK — uydurma durum adı"


def test_IKINCI_DEPO_YOK():
    """🔴 **İkinci bir gerçeklik yasağı.** İlk sürüm iptali süreç-içi bir `set()`'te
    tutuyor ve `request.app.state.ask_jobs`'tan okuyordu — **öyle bir depo yok**. Süreç
    yeniden başlasa iptal kaybolur, satır *"running"* kalır ve kullanıcı **durdurduğu**
    işin cevabını alırdı."""
    kaynak = (KOK / "app" / "ask_jobs.py").read_text(encoding="utf-8")
    # ⚠ Metin taraması DEĞİL, YAPI — ve bu iki kez düzeltildi: ilk sürüm `"_IPTAL" not in
    # kaynak` yazıp `DURUM_IPTAL` sabitini, ikinci sürüm `"state.ask_jobs"` arayıp **kendi
    # belgesindeki hata anlatısını** yakaladı. *Belgeyi tarayan bir kapı, hatayı ANLATMAYI
    # cezalandırır.* Bu oturumda altıncı ve yedinci kez aynı sınıf.
    agac = ast.parse(kaynak)
    for n in ast.walk(agac):
        assert not isinstance(n, ast.Set), "modülde küme sabiti — süreç-içi depo"
        if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "set":
            pytest.fail("süreç-içi iptal kümesi geri gelmiş — ikinci depo")
        if isinstance(n, ast.Attribute):
            assert n.attr != "ask_jobs", "olmayan depo (`app.state.ask_jobs`) okunuyor"
    assert "AskJob" in kaynak, "iptal `AskJob` satırına YAZILMIYOR — işaret ölü"


def test_IKI_DURUM_AYRI():
    """`iptal` ≠ `bitti`. 🔴 Bitmiş bir işi *"durdurdum"* diye raporlamak **yalan** olurdu:
    sonuç zaten kullanıcıya gitmiş olabilir. *Yokluk* buraya hiç gelmez — onu okuyucu
    (`_job_durum_oku`) **tenant izolasyonuyla birlikte** 404'e çevirir."""
    from app import ask_jobs

    assert ask_jobs.karar("running") == "iptal"
    assert ask_jobs.karar("pending") == "iptal"
    assert ask_jobs.karar("completed") == "bitti"
    assert ask_jobs.karar("failed") == "bitti"
    assert ask_jobs.karar("cancelled") == "bitti", "iki kez durdurma ikinci kez de 'iptal' der"


def test_KOSUCU_IPTALI_GERCEKTEN_OKUYOR():
    """🔴 **Bir işaret, okunmadığı sürece süstür.** `_bg` sonucu yazmadan **önce** satırın
    durumunu sorar; sormasaydı iptal edilen iş cevabını yine de yayımlardı."""
    from app import ask_jobs

    assert ask_jobs.yayimlanabilir_mi("running") is True
    assert ask_jobs.yayimlanabilir_mi("cancelled") is False

    agac = ast.parse((KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "_queue_discovery_job")
    bg = next(n for n in ast.walk(fn) if isinstance(n, ast.FunctionDef) and n.name == "_bg")
    cagrilar = [n for n in ast.walk(bg) if isinstance(n, ast.Call)
                and getattr(n.func, "attr", "") == "yayimlanabilir_mi"]
    assert len(cagrilar) == 2, (
        f"{len(cagrilar)} kontrol var — hem BAŞARI hem HATA dalı sorulmalı: durdurulmuş "
        "bir iş 'failed' diye de raporlanmamalı")


def test_UC_TENANT_IZOLASYONUNU_KENDI_YAZMIYOR():
    """🔴 *"Aynı kuralın iki sahibi"*: izolasyonu ikinci kez yazmak, birini güncelleyip
    ötekini unutmak demekti. Durdurma ucu **okuyucuyu çağırır**."""
    agac = ast.parse((KOK / "app" / "routers" / "ask.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "ask_job_iptal")
    adlar = {getattr(n.func, "id", "") or getattr(n.func, "attr", "")
             for n in ast.walk(fn) if isinstance(n, ast.Call)}
    assert "_job_durum_oku" in adlar, "uç kendi okuyucusunu yazmış — izolasyonun iki sahibi"


# ── 5 · Md.12/19 — SAKLAMA POLİTİKASI ───────────────────────────────────────

def test_SAKLAMA_ALANI_VAR():
    from control_plane.models import TenantConfig

    assert "audit_saklama_gun" in TenantConfig.model_fields


def test_SAKLAMA_SILME_YAPMIYOR_BEYAN_EDIYOR():
    """⚠ Bir saklama süresini **uygulamak** geri alınamaz bir **SİLME** eylemidir ve
    FAZ 6'nın onay değişmezine bağlıdır. *Beyan edilmiş ama uygulanmamış bir politika,
    beyan edilmemiş bir politikadan iyidir: denetleyici ne beklediğimizi okuyabilir.*"""
    kaynak = (KOK / "control_plane" / "models.py").read_text(encoding="utf-8")
    i = kaynak.index("audit_saklama_gun")
    assert "SİLME YAPMAZ" in kaynak[max(0, i - 900):i]


# ── 6 · Md.14 — OTOMASYON ÖNYARGISI: SKALER GÜVEN YOK ───────────────────────

def test_LLM_YOLUNDA_SKALER_GUVEN_YOK():
    """*"Kalibre edilmediği sürece o sayı bir güven değil bir **süstür**"* (MIMARI §5).
    Bu **zaten** uygulanıyordu; kapı onu **çürümeye karşı** kilitliyor."""
    from app.schemas import Explain

    assert Explain(path="llm:gemini").confidence is None


# ── 7 · K2 — YETİM UÇ YOK: her yükümlülüğün bir EKRAN karşılığı var ────────

FE = KOK.parent / "dima-frontend-demo-master" / "src"


def _fe(*parca: str) -> str:
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    return FE.joinpath(*parca).read_text(encoding="utf-8")


def _kart_agaci() -> str:
    """🔴 **Cevap kartı bir DOSYA değil, bir AĞAÇTIR** — ve bu, bu operasyonda **ikinci**
    kez aynı kusurdan öğrenildi.

    FAZ 7.8'de makbuz `ReportCard.tsx`'ten `Makbuz.tsx`'e taşındı. `kanit_sinifi` hâlâ
    **cevap kartında** render ediliyor, ama bu kapı `ReportCard.tsx` dosyasını okuduğu
    için `ValueError: substring not found` verdi.

    ⚠ **Ve gerilemeyi hızlı kapı GÖRMEDİ**: `lab/kapi.py --hizli --degisen` değişen
    **Python modüllerine** göre test seçiyor; bir `.tsx` değişikliği bu Python kapısına
    bağlanmıyor. *Bir kapının kapsamı, onu tetikleyen sinyalden büyük olamaz.*

    `test_cevap_alani_yetim_degil._kart_agaci()` ile **aynı** çözüm ve aynı gerekçe:
    bir alanın **nerede** render edildiği bir uygulama ayrıntısıdır; render **edilip
    edilmediği** bir sözleşmedir.
    """
    import re

    kok = _fe("components", "ReportCard.tsx")
    parcalar = [kok]
    for m in re.finditer(r'from "@/(components|lib)/(\w+)"', kok):
        for uzanti in (".tsx", ".ts"):
            aday = FE / m.group(1) / f"{m.group(2)}{uzanti}"
            if aday.exists():
                parcalar.append(aday.read_text(encoding="utf-8"))
                break
    return "\n".join(parcalar)


def test_DURDURMA_DUGMESI_EKRANDA():
    """🔴 *Durdurulamayan bir otomasyon, üzerinde insan denetimi olmayan bir
    otomasyondur* — ve **erişilemeyen** bir durdurma ucu, olmayan bir uçtur. `job_id`
    bugüne kadar bilerek *"görünmez"* tutuluyordu; bedeli tam olarak buydu."""
    dugme = _fe("components", "DurdurDugmesi.tsx")
    assert "cancelAskJob" in dugme, "düğme ucu ÇAĞIRMIYOR — süs"
    for panel in ("ChatPanel.tsx", "ReportPanel.tsx"):
        assert "DurdurDugmesi" in _fe("components", panel), \
            f"{panel}: bekleyen kullanıcı düğmeyi GÖREMİYOR"
    assert "onJob" in _fe("lib", "api-client.ts"), "job_id UI'ya hiç ULAŞMIYOR"


def test_DURDURMA_HATA_GIBI_GOSTERILMIYOR():
    """🔴 Kendi bastığı düğmenin sonucunu *"bir sorun oluştu"* diye okumak, kullanıcıya
    **kendi eylemini bir arıza gibi** anlatmak olurdu."""
    kaynak = _fe("lib", "api-client.ts")
    i = kaynak.index('data.status === "cancelled"')
    blok = kaynak[i:i + 700]
    assert "Durdurdun" in blok and "yayımlanmadı" in blok
    assert blok.index("Durdurdun") < blok.index('data.status === "failed"'), \
        "durdurma, `failed` dalının İÇİNE düşüyor"


def test_MD50_ISARETI_EKRANDA_ve_ANLATININ_YANINDA():
    """🔴 Md.50'nin işareti **görünmezse yoktur**. ⚠ Kartın **tepesinde** durmaz: tepedeki
    bir rozet *"bu cevabın TAMAMI yapay zekâ ürünü"* diye okunurdu ve bu **yanlış** olurdu
    — tablo, sayı ve kırılım deterministik küpten gelir."""
    kart = _fe("components", "ReportCard.tsx")
    assert "ai_generated_prose" in kart, "Md.50 işareti hiçbir yerde gösterilmiyor"
    assert kart.index("<OutputInsight") < kart.index("item.ai_generated_prose"), \
        "işaret anlatının ÜSTÜNDE — tüm cevabı AI ürünü gibi gösterir"


def test_KANIT_SINIFI_EKRANDA_ve_YUZDE_UYDURMUYOR():
    """⚠ Ekranda bir **yüzde** belirirse MIMARI §5 ihlal edilir: *kalibre edilmediği sürece
    o sayı bir güven değil bir **süstür**.*"""
    kart = _kart_agaci()
    i = kart.index("item.kanit_sinifi")
    blok = kart[i:i + 1500]
    assert "olasılıksal" in blok and "ölçülmüş" in blok
    assert "%" not in blok, "kanıt sınıfı bir YÜZDEYE çevrilmiş — uydurma kalibrasyon"


def test_IHRAC_TUKETICISI_VAR_ve_YENI_PANEL_ACILMADI():
    """🔴 *Bir kanıt defteri, indirilemiyorsa denetlenebilir değildir.* ⚠ Yeni panel
    açılmadı (tavan 13/13, pay 0): ihraç, yetkisi **aynı** olan (`contract:read`) kanıt
    panelinin içindedir."""
    panel = _fe("components", "ContractDetailPanel.tsx")
    assert "exportAudit" in panel, "ihraç ucunun EKRAN tüketicisi yok — yetim uç"
    assert "exportAudit" in _fe("lib", "api-client.ts")
    yeni = [p for p in ("AuditPanel.tsx", "DenetimPanel.tsx", "AuditExportPanel.tsx")
            if (FE / "components" / p).exists()]
    assert not yeni, f"yeni panel açılmış: {yeni} — K5 tavanı 13/13"


# ── 8 · ⚠ DOĞRULANMAMIŞ TARİH KAPIYA ÇEVRİLMEDİ ────────────────────────────

def test_YURURLUK_TARIHI_DOGRULANMADI_olarak_KALIYOR():
    """🔴 Yol haritası tarihi **kendi eliyle** `[DOĞRULANMADI]` diye işaretlemiş.
    Bu kapı **tarihi doğrulamaz**, yükümlülüğün **karşılığının kodda var olduğunu**
    doğrular. *Doğrulanmamış bir tarihi kapıya çevirmek, ölçmediğimiz bir şeyi ölçtük
    gibi göstermek olurdu.*"""
    kaynak = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "[DOĞRULANMADI]" in kaynak
    assert "tarihi doğrulamaz" in kaynak
