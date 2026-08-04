"""FAZ 1.11 — **KADEMELİ DÜŞÜŞ** kapısı.

`FailoverSqlGenerator` **zaten** sırayla deniyordu — yol haritası bu yüzden *"yeni kod
YOK"* diyor. Eksik olan iki şeydi: **kayıt** (bir düşüş `AuditLog`'a hiç yazılmıyordu,
yalnız bir `WARNING` kütüğü vardı ve *"dün kaç kez ikinci seviyeye düştük"* sorusu
**cevapsızdı**) ve **gösterge** (kullanıcı hangi seviyede cevap aldığını göremiyordu).
"""

from __future__ import annotations

import ast
import pathlib

import pytest

from app import kademeli_dusus as K

KOK = pathlib.Path(__file__).resolve().parents[1]
FE = KOK.parent / "dima-frontend-demo-master" / "src"


class _Anthropic:
    _provider = "anthropic"


class _Gemini:
    _provider = "gemini"


class RuleBasedSqlGenerator:      # ad ÖNEMLİ: seviye 3'ün belirteci sınıf adıdır
    pass


# ── 1 · ÜÇ SEVİYE — sağlayıcı sayısı değil, KATEGORİ ───────────────────────

def test_UC_SEVIYE():
    """*Beş seviyeli bir gösterge, kullanıcının kararını değiştirmeyen bir ayrımı ekrana
    taşırdı.* Seviye 2 ile 3 arasındaki fark **kararı değiştirir**; gemini ile groq
    arasındaki fark **değiştirmez**."""
    assert K.SEVIYELER == (1, 2, 3)


def test_BIRINCIL_SEVIYE_1():
    assert K.seviye(_Anthropic(), sira=0) == 1


def test_YEDEK_SEVIYE_2():
    assert K.seviye(_Gemini(), sira=1) == 2
    assert K.seviye(_Gemini(), sira=4) == 2, "dördüncü yedek de seviye 2'dir"


def test_RULE_HER_ZAMAN_SEVIYE_3():
    """🔴 **Sıra 0 her zaman seviye 1 DEĞİLDİR.** Yapılandırma `rule`'u tek başına
    bırakabilir (anahtarsız kurulum) ve o durumda **birinci** sağlayıcı zaten seviye
    **3**'tür. Sırayı seviyeyle karıştırmak, LLM'siz bir kurulumu *"normal"* gösterirdi."""
    assert K.seviye(RuleBasedSqlGenerator(), sira=0) == 3
    assert K.seviye(RuleBasedSqlGenerator(), sira=5) == 3


# ── 2 · DÜŞÜŞ OLAYI — gürültü ÜRETMİYOR ────────────────────────────────────

def test_SEVIYE_DUSUNCE_OLAY_VAR():
    olay = K.dusus_kaydi(_Gemini(), yeni_sira=1)
    assert olay["onceki_seviye"] == 1 and olay["seviye"] == 2
    assert "seviye 1 → 2" in olay["ozet"]


def test_AYNI_SEVIYEDE_OLAY_YOK():
    """gemini'den groq'a geçmek kullanıcı için bir olay **değildir** (ikisi de seviye 2);
    her denemeyi audit'e yazmak kaydı **gürültüye** boğardı — *gürültüyle dolan bir kanıt
    defteri okunmaz olur.*"""
    assert K.dusus_kaydi(_Gemini(), yeni_sira=2, onceki_seviye=2) is None


def test_YUKSELIS_OLAY_DEGIL():
    """Seviye **iyileşiyorsa** düşüş kaydı yazılmaz — bir olay, kötüleşmedir."""
    assert K.dusus_kaydi(_Anthropic(), yeni_sira=0, onceki_seviye=3) is None


def test_ONCEKI_SEVIYE_ACIKCA_VERILIYOR():
    """🔴 **Gizli varsayım açığa çıkarıldı.** İlk sürüm önceki ÜRETİCİYİ alıp seviyesini
    `sira=0` ile hesaplıyordu — *"önceki her zaman listenin başıdır"* varsayımı.
    Kendi sınamam onu gösterdi: aynı üretici, aynı seviye, yine de bir **olay** üretiyordu.
    *Gizli bir varsayım, doğru olduğu sürece görünmez; yanlış olduğu gün açıklanamaz bir
    kayıt bırakır.*"""
    import inspect

    p = inspect.signature(K.dusus_kaydi).parameters
    assert "onceki_seviye" in p, "taban seviye AÇIKÇA verilmiyor — gizli varsayım geri geldi"
    assert p["onceki_seviye"].default == 1


def test_GECERSIZ_TABAN_SEVIYESI_1_E_DUSUYOR():
    assert K.dusus_kaydi(_Gemini(), yeni_sira=1, onceki_seviye=99) is not None


# ── 3 · YAZMA YOLU GERÇEKTEN BAĞLI ──────────────────────────────────────────

def test_FAILOVER_DUSUSU_KAYDEDIYOR():
    """Bir modül yazmak yetmez; kayıt ancak **yazıldığı yerde** vardır."""
    agac = ast.parse((KOK / "app" / "llm.py").read_text(encoding="utf-8"))
    sinif = next(n for n in ast.walk(agac)
                 if isinstance(n, ast.ClassDef) and n.name == "FailoverSqlGenerator")
    assert any(isinstance(n, ast.FunctionDef) and n.name == "_dususu_kaydet"
               for n in sinif.body), "`_dususu_kaydet` YOK"
    fn = next(n for n in sinif.body
              if isinstance(n, ast.FunctionDef) and n.name == "generate_sql")
    assert any(isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "_dususu_kaydet"
               for n in ast.walk(fn)), "`generate_sql` düşüşü kaydetmiyor — modül ölü"


def test_KAYIT_HATASI_CEVABI_DUSURMUYOR():
    """🔴 Kademeli düşüş bir **DAYANIKLILIK** mekanizmasıdır; onu **kayıt** yüzünden
    kırmak, amacının tam tersi olurdu."""
    kaynak = (KOK / "app" / "llm.py").read_text(encoding="utf-8")
    i = kaynak.index("def _dususu_kaydet")
    govde = kaynak[i:i + 1400]
    assert "except Exception" in govde and "dayanıklılığı KIRAMAZ" in govde


# ── 4 · GÖSTERGE — yeni uç AÇILMADI ────────────────────────────────────────

def test_SOZLESME_SCHEMARESPONSE_TA():
    """🔴 **Yeni bir uç açılmadı:** rozet `/schema`'yı **zaten** yokluyor; ikinci bir poll
    aynı bilgiyi iki kanaldan taşımak ve ikisinin **ayrışması** demekti."""
    from app.schemas import SchemaResponse

    for alan in ("llm_seviye", "llm_seviye_etiket", "llm_uretici"):
        assert alan in SchemaResponse.model_fields, alan
    assert SchemaResponse(models=[]).llm_seviye is None, "varsayılan None değil"


def test_RAPOR_SON_BASARILI_URETICIYI_OKUYOR():
    """*"Birinci sağlayıcı tanımlı"* ile *"birinci sağlayıcı cevap veriyor"* aynı şey
    değildir — gösterge kullanıcının **aldığı** cevabın seviyesini söylemelidir."""
    kaynak = (KOK / "app" / "kademeli_dusus.py").read_text(encoding="utf-8")
    i = kaynak.index("def istekten_rapor")
    assert '"_last"' in kaynak[i:i + 1400], "`_last` okunmuyor — liste başı gösterilir"


def test_FRONTEND_UC_SEVIYEYI_GOSTERIYOR():
    """🔴 **K2** + maddenin görsel şartı."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    rozet = (FE / "components" / "ConnectionBadge.tsx").read_text(encoding="utf-8")
    assert "llm_seviye" in rozet, "seviye hiçbir yerde gösterilmiyor"
    assert "seviye === 3" in rozet and "seviye === 2" in rozet


def test_SEVIYE_3_CEVRIMDISI_GIBI_GOSTERILMIYOR():
    """🔴 **Seviye 3 bir HATA DEĞİL bir DURUMDUR:** sistem çalışıyor ama cevaplar
    **kategorik olarak farklı** bir yoldan geliyor. Kırmızı göstermek kullanıcıyı
    **yanlış eyleme** (sistemi yeniden başlatmaya) iterdi."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    rozet = (FE / "components" / "ConnectionBadge.tsx").read_text(encoding="utf-8")
    # ⚠ **Pencere değil, RENK BLOĞU sorulur** — ve bu bir düzeltme: ilk sürüm
    # `seviye === 3`'ün İLK geçişinden 500 karakter alıyordu ve o geçiş etiket (`label`)
    # dalıydı, renk dalı değil. Bu oturumda BEŞİNCİ kez pencere-tabanlı metin taraması
    # yanlış yeri ölçtü. Doğru soru: **renk sınıflarını taşıyan ifadede** seviye 3 hangi
    # renge bağlanmış?
    i = rozet.index("className={`inline-block")
    renk_blogu = rozet[i:i + 700]
    assert "seviye === 3" in renk_blogu, "seviye 3 için AYRI bir renk dalı yok"
    j = renk_blogu.index("seviye === 3")
    assert "amber" in renk_blogu[j:j + 200], "seviye 3 amber DEĞİL — çevrimdışıyla aynı kanal"
    assert "bg-red-500" not in renk_blogu[j:j + 200], "seviye 3 KIRMIZI gösteriliyor"


def test_FRONTEND_ESIK_KOPYALAMIYOR():
    """Seviye kararı **backend'de**; frontend'de ikinci bir sınıflandırma rozet ile
    audit'in **ayrışması** demekti — biri *"seviye 2"* derken öteki *"seviye 3"* gösterirdi."""
    if not FE.exists():
        pytest.skip("frontend bu koşumda mount edilmemiş")
    rozet = (FE / "components" / "ConnectionBadge.tsx").read_text(encoding="utf-8")
    for sizinti in ("RuleBasedSqlGenerator", "_provider", "_gens"):
        assert sizinti not in rozet, f"sınıflandırma frontend'e KOPYALANMIŞ ({sizinti!r})"
