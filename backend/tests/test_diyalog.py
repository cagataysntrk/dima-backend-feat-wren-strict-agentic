"""🔴 `G2` — **DİYALOG BELLEĞİ**: sistem sorduğunu HATIRLAR.

## Neden

JPMorgan (arXiv 2605.26394): çok-turlu text-to-SQL'de **tur-3 durumsuz koşulduğunda
beş modelin beşi de %0**; iki turluk çalışma penceresiyle **%87,6–100**. Durum taşımak
bir iyileştirme değil, **var olma koşuludur**.

⚠ Bu dosya `G2`'nin **ilk yarısını** kilitler: slot durumu **kaydedilir**, davranış
**değişmez**. Devam/onarım davranışı `G2.7`/`G2.8`'de gelir. *Bir belleği önce görünür
kılarsın, sonra kullanırsın.*
"""

from __future__ import annotations

from app.diyalog import (
    SLOT_CUBE,
    SLOT_DONEM,
    SLOT_OLCU,
    acik_slotlar,
    bekleyen_yanit_mi,
    devam_edilebilir,
    durum,
    onarim_hedefi,
)

_TAM = {"cube": "satis", "measures": ["ciro"],
        "filters": [{"dimension": "tarih", "value": "2026-03"}]}


# --- AÇIK SLOT --------------------------------------------------------------------


def test_tam_sorguda_acik_slot_YOK():
    assert acik_slotlar(_TAM, donem_gerekli=True) == []


def test_eksik_yuvalar_SIRAYLA_bildirilir():
    """Sıra anlamlıdır: cube → ölçü → dönem. Kullanıcıya önce **hangi konu** sorulur."""
    assert acik_slotlar({}, donem_gerekli=True) == [SLOT_CUBE, SLOT_OLCU, SLOT_DONEM]


def test_DONEM_GEREKLILIGI_disaridan_gelir():
    """🔴 *"Dönem şart mı"* kararı bu modülün değil, `_period_gate`'in bilgisi.
    İki yerde ayrı hesaplamak, farklı cevap veren iki sahip doğururdu."""
    cq = {"cube": "satis", "measures": ["ciro"]}
    assert acik_slotlar(cq, donem_gerekli=False) == []
    assert acik_slotlar(cq, donem_gerekli=True) == [SLOT_DONEM]


def test_timeDimensions_de_DONEM_sayilir():
    cq = {"cube": "s", "measures": ["m"],
          "timeDimensions": [{"dimension": "tarih", "granularity": "month"}]}
    assert acik_slotlar(cq, donem_gerekli=True) == []


# --- DURUM ------------------------------------------------------------------------


def test_tur_no_ARTAR():
    d1 = durum({}, donem_gerekli=True)
    d2 = durum({}, onceki=d1, donem_gerekli=True)
    assert d1["tur_no"] == 1 and d2["tur_no"] == 2


def test_DOLAN_yuva_bildirilir():
    """Bir yuva dolduysa bu **görünür** olmalı — kullanıcı ilerlediğini görmeli."""
    d1 = durum({"cube": "satis"}, donem_gerekli=False)          # ölçü açık
    d2 = durum(_TAM, onceki=d1, donem_gerekli=True)             # ölçü doldu
    assert SLOT_OLCU in (d2.get("dolu") or [])


def test_TASINACAK_SEY_YOKSA_None():
    """Boş bir durum bir beyan değil, **gürültüdür**."""
    assert durum(_TAM, donem_gerekli=True) is None


def test_sorulan_yuva_TASINIR():
    d = durum({}, sorulan=SLOT_DONEM, donem_gerekli=True)
    assert d["sorulan"] == SLOT_DONEM


# --- BEKLEYEN YANIT ---------------------------------------------------------------


def test_bekleyen_yanit_TETIKLEYICI():
    """🔴 `devam` davranışının tetikleyicisi: bekleyen soru varken gelen kısa ifade
    (*"geçen ay"*) **yeni bir soru değildir**, bir **cevaptır**."""
    assert bekleyen_yanit_mi({"sorulan": SLOT_DONEM}) == SLOT_DONEM
    assert bekleyen_yanit_mi({"acik_slotlar": [SLOT_DONEM]}) is None   # sorulmadıysa yok
    assert bekleyen_yanit_mi(None) is None
    assert bekleyen_yanit_mi({"sorulan": "uydurma_yuva"}) is None      # kapalı liste


# --- ONARIM -----------------------------------------------------------------------


def test_TEK_yuva_degistiyse_ONARIM():
    """*"Yok ya mart demiştim"* → yalnız DÖNEM değişir; ölçü ve cube korunur."""
    eski = dict(_TAM)
    yeni = {**_TAM, "filters": [{"dimension": "tarih", "value": "2026-04"}]}
    assert onarim_hedefi(None, yeni, eski) == SLOT_DONEM


def test_COK_yuva_degistiyse_ONARIM_DEGIL():
    """🔴 İki yuva birden değiştiyse bu bir onarım değil, **yeni bir sorudur**.
    Onarım sanmak, kullanıcının kastetmediği bir bağlamı taşımak olurdu."""
    eski = dict(_TAM)
    yeni = {"cube": "uretim", "measures": ["fire"],
            "filters": [{"dimension": "tarih", "value": "2026-04"}]}
    assert onarim_hedefi(None, yeni, eski) is None


def test_HICBIR_SEY_degismediyse_None():
    assert onarim_hedefi(None, dict(_TAM), dict(_TAM)) is None


def test_granulerlik_degisimi_DONEM_onarimidir():
    """*"aylık göster"* bir dönem beyanıdır — ölçü değişmemiştir."""
    eski = {"cube": "s", "measures": ["m"],
            "timeDimensions": [{"dimension": "t", "granularity": "month"}]}
    yeni = {"cube": "s", "measures": ["m"],
            "timeDimensions": [{"dimension": "t", "granularity": "day"}]}
    assert onarim_hedefi(None, yeni, eski) == SLOT_DONEM


# --- SINIRLAR ---------------------------------------------------------------------


def test_LLM_COAGRISI_YOK():
    """🔴 Diyalog katmanı **deterministiktir**: ne LLM çağırır, ne sayı üretir, ne şema
    iddiası kurar. §G.0c'nin *"güven modeline HİÇ dokunmaz"* cümlesinin kod karşılığı."""
    import pathlib
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app" / "diyalog.py").read_text(encoding="utf-8")
    for yasak in ("from app.llm", "import llm", "safe_call", "requests", "re.compile"):
        assert yasak not in kaynak, f"diyalog.py sınırı aştı: {yasak}"


def test_IKINCI_SLOT_TEMSILI_YOK():
    """🔴 KAT-1: *açık slot* ikinci bir veri yapısı DEĞİL, `Niyet`'in boş alanıdır.
    `diyalog.py` kendi dataclass'ını tanımlarsa iki sahip doğar."""
    import pathlib
    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app" / "diyalog.py").read_text(encoding="utf-8")
    assert "@dataclass" not in kaynak, "diyalog.py kendi durum nesnesini tanımlamış"
    assert "class " not in kaynak, "diyalog.py sınıf tanımlamış — saf fonksiyon olmalı"


def test_PENCERE_GENISLETILMEDI():
    """🔴 BASİTLİK KİLİDİ. Aynı JPMorgan çalışması karmaşık belleğin **−12,6 puana**
    kadar ZARAR verdiğini ölçtü. `context.py`'nin iki turluk penceresi bir sınır değil
    bir **karardır** ve `G2` onu genişletmez."""
    import pathlib
    ctx = (pathlib.Path(__file__).resolve().parents[1]
           / "app" / "context.py").read_text(encoding="utf-8")
    assert "(history or [])[-2:]" in ctx, "bağlam penceresi değişmiş — basitlik kilidi kırıldı"


# --- G2.7 · DEVAM ------------------------------------------------------------------


def test_kismi_sorgu_TASINIR():
    """Netleştirme `cube_query=None` döndürür ama o turda cube ANLAŞILMIŞ olabilir.
    Taşınmazsa bir sonraki tur onu yeniden bulmak zorunda kalır."""
    d = durum(None, sorulan=SLOT_DONEM, kismi_cq={"cube": "satis", "measures": ["ciro"]},
              donem_gerekli=True)
    assert d["kismi_cq"] == {"cube": "satis", "measures": ["ciro"]}


def test_devam_IKISI_BIRDEN_ister():
    """🔴 Bir soru sorulmuş OLMALI **ve** o an ne anlaşıldığı taşınmış OLMALI.
    Yalnız biri varsa devam edilemez — ve bu dürüstçe `None`'dır, tahmin değil."""
    assert devam_edilebilir({"sorulan": SLOT_DONEM,
                             "kismi_cq": {"cube": "s"}}) == {"cube": "s"}
    assert devam_edilebilir({"sorulan": SLOT_DONEM}) is None          # kısmi yok
    assert devam_edilebilir({"kismi_cq": {"cube": "s"}}) is None      # soru yok
    assert devam_edilebilir(None) is None


def test_KURAL_DEVAM_TAZEnin_ONUNE_gecer():
    """🔴 `G2`'nin davranış çekirdeği: bekleyen bir soruya verilen cevap **yeni bir soru
    DEĞİLDİR**. Eskiden `KURAL_TAZE` ateşleniyor ve tur SIFIRDAN koşuyordu."""
    from app.context import KURAL_DEVAM, KURAL_TAZE, coz

    dd = {"sorulan": SLOT_DONEM, "kismi_cq": {"cube": "satis", "measures": ["ciro"]}}
    b = coz(history=["fire kg"], diyalog_durumu=dd)
    assert b.kural == KURAL_DEVAM
    assert b.cube_query == {"cube": "satis", "measures": ["ciro"]}
    # Bekleyen soru YOKKEN davranış BİREBİR eskisi
    assert coz(history=["fire kg"]).kural == KURAL_TAZE


def test_YAPISAL_baglam_DEVAMdan_GUCLU():
    """İstemci `cube_query` yolluyorsa o daha güçlü bir sinyaldir — devam onu ezmez."""
    from app.context import KURAL_YAPISAL, coz

    dd = {"sorulan": SLOT_DONEM, "kismi_cq": {"cube": "eski"}}
    b = coz(cube_query={"cube": "yeni"}, diyalog_durumu=dd)
    assert b.kural == KURAL_YAPISAL and b.cube_query["cube"] == "yeni"


# --- 🔴 DA-5 — KILL-SWITCH YOKTU ---------------------------------------------------


def test_G2_KILL_SWITCH_VAR():
    """🔴 `G2` indiğinde GERİ AL sözleşmesi yazılmıştı (*"`off` → davranış birebir
    bugünkü"*) ama **bayrak hiç yaratılmamıştı** — bir denetim ajanı buldu.

    `MIMARI §9.11`'in kendi dersi: *bir kill-switch yalnız KODDA varsa yarımdır.*
    Bayrağı olmayan bir katman geri alınamaz; geri alınamayan bir katman, ölçülmüş bir
    kazanç olmadan **kalıcıdır**.
    """
    import pathlib

    kok = pathlib.Path(__file__).resolve().parents[1]
    yml = (kok / "demo/packs/features.yml").read_text(encoding="utf-8")
    assert "diyalog_bellegi:" in yml, "🔴 `G2` bayrağı YAML'de yok — geri alınamaz"

    kaynak = (kok / "app/routers/ask.py").read_text(encoding="utf-8")
    assert '"diyalog_bellegi" in resolve_for' in kaynak, (
        "🔴 bayrak okunmuyor — YAML'de bir ad var ama kod onu hiç sormuyor; "
        "bu, kill-switch'in olmamasından daha kötüdür: VAR sanılır")


def test_KILL_SWITCH_TEK_NOKTADA():
    """⚠ Kesme noktası **girişte**: durum sunucuya hiç girmezse `devam_edilebilir(None)`
    zaten `None` döner ve `KURAL_DEVAM` ateşlenmez.
    *Tek noktada kesmek, on dalda ayrı ayrı sormaktan hem ucuz hem dürüsttür.*"""
    import pathlib

    kaynak = (pathlib.Path(__file__).resolve().parents[1]
              / "app/routers/ask.py").read_text(encoding="utf-8")
    assert kaynak.count('"diyalog_bellegi" in resolve_for') == 1, (
        "🔴 bayrak birden çok yerde soruluyor — ikinci sahip riski")
