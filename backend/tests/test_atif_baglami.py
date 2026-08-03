"""FAZ E · ATIF BAĞLAMI — *"az önce dediğin gibi…"* artık cevabı ÖLDÜRMÜYOR.

## Ölçülen kusur (3 Ağustos 2026)

**Aynı** isteğin atıflı hâli ölüyordu:

    "makine bazında ayır"                        → source=cube  dim=['makine']   ✅
    "az önce dediğin gibi makine bazında ayır"   → source=None  CEVAPSIZ         ❌
    "yukarıdaki raporu vardiya bazında ver"      → source=rule  dim=None         ❌❌

Üçüncüsü en kötüsü: cevap **verdi** ama Discovery'ye düşüp **kırılımı kaybetti** —
`source=rule` rozetiyle gelen sessiz-yanlış. Beş atıflı ifadenin **dördü** ölmüştü;
atıfsız hâllerinin **beşi de** çalışıyordu, yani kayıp tamamen atıf sözcüklerindendi.

Kesen kapı `deterministic_refine`'ın **kendi** `_coverage_ok`'uydu: atıf sözcükleri
"açıklanamayan kelime" sayılıyordu.

## İkinci kusur: `history` yalnız BOOLEAN olarak okunuyordu

`context.coz` `prev_sql and history` diye bakıyor, **içeriğine hiç bakmıyordu**. Yapısal
bağlam yokken atıflı bir mesaj `KURAL_HAM`'a düşüp **ham SQL** üretiyordu — kullanıcının
işaret ettiği rapor değil, uydurulmuş bir sorgu.

Çözüm LLM değil **muhasebe**: önceki turun metni deterministik `route()` ile yeniden
çözülür ve çıkan sorgu yapısal çapa yerine konur. İkinci bir cevap hattı YAZILMAZ.
"""

from __future__ import annotations

import pytest

from app import context as app_context
from app import cube_router
from tests.conftest import ask

TABAN = "bu yıl oee"

#: (atıflı istek, ATIFSIZ eşdeğeri, beklenen kırılım)
CIFTLER = [
    ("az önce dediğin gibi makine bazında ayır", "makine bazında ayır", "makine"),
    ("yukarıdaki raporu vardiya bazında ver", "vardiya bazında ver", "vardiya"),
    ("bir önceki soruyu hat bazında tekrarla", "hat bazında", "hat"),
    ("bahsettiğin raporu makine bazında ayır", "makine bazında ayır", "makine"),
    ("demin sorduğumu hat bazında göster", "hat bazında göster", "hat"),
]


@pytest.fixture
def taban(client):
    d = ask(client, TABAN)
    assert d.get("cube_query"), "taban rapor yok — ölçüm önkoşulu sağlanmadı"
    return d


# --- 1) ATIF, ATIFSIZ EŞDEĞERİYLE AYNI SONUCU VERİR --------------------------------

@pytest.mark.parametrize("atifli,atifsiz,beklenen", CIFTLER)
def test_ATIFLI_ve_ATIFSIZ_AYNI_sonucu_verir(client, taban, atifli, atifsiz, beklenen):
    """Kapının ölçütü *"cevap geldi mi"* değil, **aynı cevap mı**. Atıf sözcükleri
    cevabı ne öldürmeli ne de BAŞKA bir cevaba kaydırmalı."""
    a = ask(client, atifli, cube_query=taban["cube_query"])
    b = ask(client, atifsiz, cube_query=taban["cube_query"])
    assert a.get("source") == "cube", f"atıflı hâl deterministik yolu kaybetti: {a.get('source')}"
    assert (a.get("cube_query") or {}).get("dimensions") == [beklenen], a.get("cube_query")
    assert a.get("cube_query") == b.get("cube_query"), (
        "atıflı ve atıfsız istek FARKLI rapor üretti:\n"
        f"  atıflı : {a.get('cube_query')}\n  atıfsız: {b.get('cube_query')}")


# --- 2) history İÇERİĞİ OKUNUYOR (yapısal bağlam yokken) ---------------------------

@pytest.mark.parametrize("atifli,_a,beklenen", CIFTLER)
def test_YAPISAL_BAGLAM_YOKKEN_ONCEKI_TUR_geri_kazanilir(client, taban, atifli, _a, beklenen):
    """`cube_query` YOK, yalnız `history` var → önceki turun metni deterministik
    `route()` ile çözülür. ÖNCEDEN burada `source=rule` ham SQL üretiliyordu."""
    d = ask(client, atifli, history=[TABAN], prev_sql=taban.get("sql"))
    assert d.get("source") == "cube", (
        f"atıf ham-SQL yoluna düştü ({d.get('source')}) — uydurma sorgu riski")
    assert (d.get("cube_query") or {}).get("dimensions") == [beklenen], d.get("cube_query")


def test_ONCEKI_TUR_COZULEMEZSE_HICBIR_SEY_UYDURULMAZ(client):
    """`route()` önceki turu çözemiyorsa bağlam olduğu gibi kalır — yapay bir çapa
    ÜRETİLMEZ. Uydurma bir çapa, bu fazın kapatmak için var olduğu kusurun kendisi."""
    d = ask(client, "az önce dediğin gibi makine bazında ayır",
            history=["asdf qwerty zxcv"], prev_sql="SELECT 1")
    assert (d.get("cube_query") or {}).get("cube") != "oee", d.get("cube_query")


# --- 3) BAĞLAM MODELİ: iki turluk pencere + makbuz ----------------------------------

def test_PENCERE_IKI_TURLA_SINIRLI():
    """Üç ve üzeri tur *"hangi tur kastedildi"* sorusunu doğurur ve o bir **retrieval**
    problemidir — raporun kendi ölçümü retrieval'ı reddetti (+14/−16)."""
    b = app_context.coz(history=["bir", "iki", "üç", "dört"], atif=True)
    assert b.ham_ifade == ("üç", "dört"), b.ham_ifade


def test_MAKBUZ_HAM_PENCEREYI_TASIR():
    """Atıf yolunda *"neden bu bağlam?"* sorusunun cevabı METİNDİR. Yazılmasaydı o
    yolla üretilen her cevap gerekçesiz kalırdı."""
    b = app_context.coz(history=["bu yıl oee"], atif=True)
    assert b.kural == app_context.KURAL_ATIF
    assert b.makbuza()["resolved_context"]["raw_window"] == ["bu yıl oee"]


def test_ATIF_KURALI_HAMDAN_ONCE_gelir():
    """Ham-SQL zinciri *"bağlam yok"* der ve çağıranı Discovery'ye bırakır; atıf
    *"bağlam VAR, ham ifadededir"* der. Sıra ters olsaydı kusur geri gelirdi."""
    b = app_context.coz(prev_sql="SELECT 1", history=["bu yıl oee"], atif=True)
    assert b.kural == app_context.KURAL_ATIF
    yapisal = app_context.coz(cube_query={"cube": "oee"}, history=["x"], atif=True)
    assert yapisal.kural == app_context.KURAL_YAPISAL, "yapısal çapa atıftan ÖNCE gelmeli"


def test_ATIF_YOKSA_DAVRANIS_BIREBIR_AYNI():
    """KURAL B: atıf bayrağı kapalıyken bugünkü kurallar değişmez."""
    assert app_context.coz(prev_sql="SELECT 1", history=["x"]).kural == app_context.KURAL_HAM
    assert app_context.coz().kural == app_context.KURAL_TAZE


# --- 4) AYIKLAMA DİSİPLİNİ: span tabanlı, kelime kümesi DEĞİL -----------------------

def test_SPAN_TABANLI_AYIKLAMA_DONEMI_BOZMAZ():
    """Kelime-kümesi yöntemi (`sosyal_ayikla`) burada YIKICI olurdu: `onceki soru`
    eşleşince kümeye `onceki` girer ve *"önceki ay"* DÖNEM ifadesindeki `önceki` de
    düşerdi. Span tabanlı silme bu sınıfı tamamen kapatır."""
    cikti = cube_router.atif_ayikla("önceki soruyu önceki aya göre ver")
    assert "onceki ay" in cikti, cikti
    assert "soru" not in cikti, cikti


def test_KALIP_ESLESMEDIYSE_HICBIR_SEY_DUSMEZ():
    """Ayıklama kalıba bağlıdır, kelimeye değil (D1'in aynı ilkesi)."""
    assert cube_router.atif_ayikla("önceki ay ciro") == "onceki ay ciro"
    assert not cube_router.atif_var("önceki ay ciro")


def test_CEKIM_EKI_TOLERANSI_TEK_KAYNAKTAN():
    """`_ek_gecerli` tek kaynak: *"bir önceki soruYU"* eşleşmeli."""
    assert cube_router.atif_ayikla("bir önceki soruyu hat bazında tekrarla") == "hat bazinda"
    assert cube_router.atif_ayikla("yukarıdaki raporu vardiya bazında") == "vardiya bazinda"


def test_HEPSI_AYIKLANIRSA_HAM_HAL_doner():
    """Boş dize aşağıdaki her kapıyı anlamsız kılardı."""
    assert cube_router.atif_ayikla("az önce dediğin") == "az once dedigin"


@pytest.mark.parametrize("q", [
    "önceki ay ciro", "geçen ay fire", "bu yıl makine bazında oee",
    "son 3 ayda vardiya bazında oee", "aynı gün içinde kaç parti",
])
def test_MESRU_SORULAR_ATIF_SAYILMAZ(client, q):
    """Kapı dar: yanlış-pozitif bir atıf, meşru bir soruyu önceki tura bağlardı."""
    assert not cube_router.atif_var(q), q
    d = ask(client, q)
    assert d.get("source") != "rule" or d.get("sql"), d
