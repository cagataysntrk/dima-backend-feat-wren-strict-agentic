"""FAZ 3.4 — **APACHE OSSIE İTHALİ** kapısı. [bayrak: `ossie_ithal`]

Sektörün fiili standardı (eski adı OSI, Haziran 2026'da **ASF**'e bağışlandı). YAML
üst-yapıları **bizim `packs/` yapımızla neredeyse birebir** — bu yüzden yazılan şey bir
**çeviricidir**, ikinci bir semantik motor değil.

⚠ MIMARI §3.4'ün *"Bilerek ALINMAYANLAR: `osi`"* kararı **bilinçli olarak geri alındı**;
gerekçe standardın ASF'e geçmesi ve ithal tarafının **kapsam tavanına küratörlük emeği
olmadan saldıran tek kaldıraç** olması.
"""

from __future__ import annotations

import pathlib

import pytest

from app import ossie

KOK = pathlib.Path(__file__).resolve().parents[1]

_BELGE = {
    "version": "0.1.1",
    "datasets": [{
        "name": "siparis",
        "table": "orders",
        "ai_context": ["sipariş", "order"],
        "metrics": [{"name": "toplam_tutar", "expression": "SUM(amount)",
                     "label": "toplam tutar",
                     "ai_context": ["ciro", "bu bizim aylık toplam sipariş tutarımızdır"]}],
        "fields": [{"name": "musteri", "type": "dimension", "ai_context": ["müşteri"]}],
    }],
    "relationships": [{"name": "siparis_musteri", "datasets": ["siparis", "musteri"],
                       "type": "MANY_TO_ONE", "condition": "siparis.mid = musteri.id"}],
}


# ── 1 · ÇEVİRİCİ, MOTOR DEĞİL ───────────────────────────────────────────────

def test_ESLEME_HEDEF_SEKLIMIZE_OTURUYOR():
    """🔴 *Hedef şekil zaten bizimki* — bu bir **eşlemedir**, yeni bir model değil."""
    out = ossie.cevir(_BELGE)
    c = out["cubes"][0]
    assert c["name"] == "siparis" and c["base_object"] == "orders"
    assert c["measures"][0]["name"] == "toplam_tutar"
    assert c["measures"][0]["expression"] == "SUM(amount)"
    assert c["dimensions"][0]["name"] == "musteri"


def test_AI_CONTEXT_SINONIME_DONUSUYOR():
    """🔴 **Standardın en değerli alanı budur:** kullanıcı kelimeleri, küratörlük emeği
    olmadan gelir."""
    c = ossie.cevir(_BELGE)["cubes"][0]
    assert "ciro" in c["measures"][0]["synonyms"]
    assert "müşteri" in c["dimensions"][0]["synonyms"]


def test_SERBEST_METIN_SINONIM_SAYILMIYOR():
    """⚠ *"Bu bizim aylık toplam sipariş tutarımızdır"* bir **sinonim değildir**. Katalogu
    cümlelerle şişirmek, `_uncovered` kapısının her soruda çekilmesine yol açardı —
    yani ithal, **kapsamı artırmak yerine düşürürdü**."""
    syn = ossie.cevir(_BELGE)["cubes"][0]["measures"][0]["synonyms"]
    assert not any(len(s) > 40 or s.count(" ") > 3 for s in syn), syn


def test_ITHAL_KAYNAGI_DAMGALANIYOR():
    """*Kaynağı gizlemek, bir gün "bu cube nereden geldi" sorusunu cevapsız bırakırdı.*"""
    assert ossie.cevir(_BELGE)["cubes"][0]["ithal_kaynak"] == "ossie"


# ── 2 · 🔴 İTHAL İLİŞKİ `olculmedi` DAMGASIYLA GELİR ───────────────────────

def test_ILISKI_SESSIZ_SAGLIKLI_DEGIL():
    """🔴 **Maddenin kapısı, birebir.** *İthal bir ilişki, sessiz "sağlıklı" değildir:*
    bir başkasının modelinin doğru olduğunu **varsaymak**, bu deponun en pahalı hatasının
    (sessiz-yanlış) **ithal edilmiş hâli** olurdu."""
    r = ossie.cevir(_BELGE)["relationships"][0]
    assert r["certified"] == "olculmedi"
    assert r["certified"] != "olculdu:saglikli"


def test_SERTIFIKA_SOZLUGU_TEK_SAHIPLI():
    """⚠ İkinci bir sertifika sözlüğü yazmak, iki damganın **ayrışması** demekti."""
    assert ossie.SERTIFIKA_OLCULMEDI == "olculmedi"
    fe_tip = (KOK.parent / "dima-frontend-demo-master" / "src" / "lib" / "types.ts")
    if fe_tip.exists():
        assert "olculmedi" in fe_tip.read_text(encoding="utf-8"), \
            "damga adı frontend sözlüğüyle AYRIŞMIŞ"


# ── 3 · FAIL-CLOSED ─────────────────────────────────────────────────────────

@pytest.mark.parametrize("bozuk,ne", [
    ({"datasets": [{"table": "x"}]}, "dataset"),
    ({"datasets": [{"name": "a", "metrics": [{"expression": "SUM(x)"}]}]}, "metric"),
    ({"datasets": [{"name": "a", "fields": [{"type": "dimension"}]}]}, "field"),
    ({"relationships": [{"datasets": ["a", "b"]}]}, "relationship"),
])
def test_ADSIZ_KAYIT_REDDEDILIYOR(bozuk, ne):
    """🔴 Adsız bir şeyi *"varsayılan"* bir adla içeri almak, katalogda **kimsenin
    arayamayacağı** bir kayıt bırakırdı — ve o kayıt bir gün bir soruya cevap olurdu."""
    with pytest.raises(ossie.OssieIthalHatasi):
        ossie.cevir(bozuk)


def test_BILINMEYEN_SURUM_REDDEDILMIYOR_UYARILIYOR():
    """⚠ Bir standardın ilerlemesini ithal kapısını **kapatarak** karşılamak, kapsamı
    dondururdu. Ama sessiz kalmak da yanlış: eşleme eksik kalabilir ve kullanıcı bunu
    **bilmeli**."""
    out = ossie.cevir({"version": "9.9", "datasets": []})
    assert out["uyarilar"] and "9.9" in out["uyarilar"][0]
    assert ossie.surum_uyarisi({}) is not None, "sürümsüz belge SESSİZCE geçiyor"


def test_CEVIRICI_DOSYA_YAZMIYOR():
    """🔴 *Yarım ithal edilmiş bir model, ithal edilmemiş bir modelden kötüdür.* Çevirici
    **saf**: yazma, sihirbazın `confirm` adımının işidir ve oradaki fail-closed kapılardan
    (`validate_project()` + üye taraması) geçer."""
    kaynak = (KOK / "app" / "ossie.py").read_text(encoding="utf-8")
    for yazma in ("write_text", "open(", "mkdir", "yaml.safe_dump"):
        assert yazma not in kaynak, f"çevirici DOSYA YAZIYOR ({yazma!r})"


# ── 4 · UÇ + BAYRAK ─────────────────────────────────────────────────────────

def test_UC_VAR():
    from app.main import create_app

    yollar = {y: {m.upper() for m in o} for y, o in create_app().openapi()["paths"].items()}
    assert "POST" in yollar.get("/connections/{cid}/import-semantic", set())


def test_BAYRAK_KAPALIYKEN_UC_404():
    """**GERİ AL:** `ossie_ithal=off` → uç **404**. 403 değil: kapalı bir özellik
    *"yetkin yok"* demez, **yok** der."""
    kaynak = (KOK / "app" / "routers" / "connections.py").read_text(encoding="utf-8")
    i = kaynak.index("def import_semantic")
    # ⚠ Dilim, docstring büyüyünce **yanlış-kırmızı** verdi (bu turda ölçüldü): kural
    # yerindeydi, kapı bir BAYT PENCERESİ ölçüyordu. Doğru sınır fonksiyonun **kendi
    # gövdesidir** — bir sonraki `def`e kadar. *Bir kapıyı sabit bir dilime bağlamak,
    # onu bir gün yalnız uzayan bir yorum yüzünden kırar.*
    j = kaynak.find("\ndef ", i + 1)
    govde = kaynak[i:j if j > 0 else len(kaynak)]
    assert '"ossie_ithal" not in resolve_for' in govde
    assert "status_code=404" in govde


def test_BAYRAK_BETA_ve_PILOTU_KOSULDU():
    """⟳ **`off` → `beta` (2026-08-12) — iki gerekçesi de ÖLÇÜMLE DÜŞTÜ.**

    Bayrak kapalı tutuluyordu; gerekçesi *«o bir YAZMA yoludur ve gerçek bir müşteri
    modeliyle pilotu YAPILMADI»* idi. İkisi de ölçüldü:

    | gerekçe | ölçülen |
    |---|---|
    | *«YAZMA yolu»* | ⊘ `ossie.cevir()` **saf fonksiyon** (kendi docstring'i), `ossie.py`'de sıfır yazma ilkeli, uç sonucu yalnız **döndürüyor** |
    | *«gerçek modelle pilot yok»* | ⊘ `test_f6_ossie_canli_sekil::test_ROUND_TRIP_canli_katalogda_KAYIPSIZ` **canlı katalogda** koşuyor ve yeşil |

    🔴 **CANLI PİLOT (2026-08-12):** kendi ihracımız (`GET …/export-semantic` → **200**,
    58.465 bayt) `POST …/import-semantic`'e geri beslendi:

        HTTP 200 · 53.761 bayt
        23 dataset → 23 cube   ·   31 ilişki → 31 ilişki
        kayıp dataset: YOK     ·   uyarı: YOK

    ⊙ Ve pilot **bir kusur buldu**: ilişkiler `olculdu:saglikli` olarak içeri geçiyordu —
    yani belgenin **üst düzey** `certified` iddiasına güveniliyordu. Ucun kendi yazılı
    değişmezi bunun tersini söylüyordu; kural iki yerde yazılı, kod **gevşek** olanı
    uyguluyordu. Kesildi: sertifika artık yalnız `x-dima`dan okunur.

    *Bir pilotun değeri, geçmesinde değil; geçerken ne gösterdiğindedir.*
    """
    import yaml

    d = yaml.safe_load((KOK / "demo" / "packs" / "features.yml").read_text(encoding="utf-8"))
    assert (d.get("features") or d).get("ossie_ithal") == "beta", (
        "bayrak değişmiş — değişiklik bir ÖLÇÜMLE gelmelidir (canlı pilot: beslenen "
        "`datasets` sayısı = dönen `cubes` sayısı).")


def test_YABANCI_SERTIFIKA_IDDIASI_KABUL_EDILMEZ():
    """🔴 Pilotun bulduğu kusur — kapı hâline getirildi.

    Bir belge **üst düzeyde** `certified: "olculdu:saglikli"` iddia edebilir; Ossie
    şemasında böyle bir alan **yoktur**, yani bu bir ölçüm değil bir **iddiadır**.
    Kabul etmek, *«bir başkasının modelinin doğru olduğunu varsaymak»* — bu deponun en
    pahalı hatasının (sessiz-yanlış) ithal edilmiş hâli olurdu.

    ⚠ Ve `x-dima` beyanı **korunur**: round-trip sadakati onu ister. Ayrım yapısaldır —
    bizim ad alanımız ile yabancı bir üst düzey alan.
    """
    b = {"version": "0.2", "datasets": [],
         "relationships": [{"name": "r", "datasets": ["a", "b"],
                            "certified": "olculdu:saglikli"}]}
    assert ossie.cevir(b)["relationships"][0]["certified"] == "olculmedi", (
        "🔴 yabancı bir belgenin sertifika İDDİASI ölçüm sayıldı")

    b2 = {"version": "0.2", "datasets": [],
          "relationships": [{"name": "r", "datasets": ["a", "b"],
                             ossie.UZANTI: {"certified": "olculdu:saglikli"}}]}
    assert ossie.cevir(b2)["relationships"][0]["certified"] == "olculdu:saglikli", (
        "🔴 KENDİ beyanımız düştü — round-trip sadakati bozuldu "
        "(`ossie_ihrac` bayrağının açılış şartı tam olarak budur)")


def test_CEKIRDEK_KATMANA_INIYOR_ERP_YE_DEGIL():
    """⚠ ERP katmanına inseydi `cari`/`ticaret`'in **dördüncü kopyası** doğardı — FAZ
    2.1'in ölçtüğü kusurun ta kendisi."""
    kaynak = (KOK / "app" / "ossie.py").read_text(encoding="utf-8")
    assert "ÇEKİRDEK KATMANA İNER" in kaynak and "dördüncü kopyası" in kaynak


# ── 5 · K2 · SİHİRBAZDA İTHAL ADIMI ────────────────────────────────────────

def _fe(*p: str) -> str:
    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    return fe.joinpath(*p).read_text(encoding="utf-8")


def test_SIHIRBAZDA_ITHAL_ADIMI_VAR():
    """🔴 **K2.** İthal ucu, sihirbazda **çağrılmıyorsa** yoktur."""
    panel = _fe("components", "ConnectionReviewPanel.tsx")
    assert "importSemantic" in panel and "içe aktar" in panel
    assert "importSemantic" in _fe("lib", "api-client.ts")


def test_YENI_PANEL_ACILMADI():
    """⚠ K5 tavanı 13/13: ithal, bağlantı sihirbazının **`review` adımının bir bölümü** —
    ayrı bir ekran değil."""
    fe = KOK.parent / "dima-frontend-demo-master" / "src"
    if not fe.exists():
        pytest.skip("frontend mount edilmemiş")
    assert not (fe / "components" / "OssiePanel.tsx").exists()
    assert "function OssieIthal" in _fe("components", "ConnectionReviewPanel.tsx")


def test_EKRAN_OLCULMEDI_DAMGASINI_SOYLUYOR():
    """🔴 *İthal bir ilişki, sessiz "sağlıklı" değildir* — ve kullanıcı bunu **ekranda**
    görmeli, yoksa ithal ettiği modele olduğundan çok güvenir."""
    panel = _fe("components", "ConnectionReviewPanel.tsx")
    assert "ÖLÇÜLMEDİ" in panel and "olculmedi" in panel


def test_EKRAN_ONIZLEME_OLDUGUNU_SOYLUYOR():
    """⚠ *Yarım ithal edilmiş bir model, ithal edilmemiş bir modelden kötüdür.* Kullanıcı
    bu adımın **yazmadığını** bilmeli."""
    panel = _fe("components", "ConnectionReviewPanel.tsx")
    duz = " ".join(panel.split())
    assert "yalnız" in duz and "önizleme" in duz, "önizleme olduğu YAZILI DEĞİL"


def test_BAYRAK_KAPALIYKEN_ADIM_CIZILMIYOR():
    """Kapalı bir özelliği gri bir düğme olarak göstermek, çalışmayan bir şeyi **teklif
    etmek** olurdu."""
    panel = _fe("components", "ConnectionReviewPanel.tsx")
    assert 'useFeature("ossie_ithal")' in panel and "ossieAcik &&" in panel
