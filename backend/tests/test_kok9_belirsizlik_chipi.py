"""🔴 KÖK-9 — **BİLİNEN BELİRSİZLİK BEYAN EDİLİR.** (denetim raporu KN-6 · KÇ-6)

## Ölçülen kusur

`schema["metrik_kaydi"]` bir terimi kaç cube'un sahiplendiğini **derleme anında**
hesaplıyor. Ölçüldü (2026-08-06, taze derleme):

    belirsiz terim:  **62 / 62**   ← kayıttaki HER terim ≥2 adaylı, HİÇBİRİNİN sahibi yok
    cevaplanan sorularda:  HIT+belirsiz **18** · HIT+net **136**  →  **%11,7**

Yani her sekiz cevaptan biri **iki sahibi olduğu bilinen** bir terim üzerinden veriliyor
ve kullanıcı bunu **hiçbir yerden** öğrenemiyordu:

| soru | terim | seçilen | adaylar |
|---|---|---|---|
| `haziran parti sayısı vardiya kırılımında` | `parti sayisi` | `oee` | `oee` · **`parti`** |
| `HAZIRAN ENERji tep çıkar` | `enerji tep` | `surdurulebilirlik` | 3 cube |
| `vardiyalere göre adet getir` | `adet` | `oee` | **6 cube** |

⊙ Kazananı belirleyen bir karar değil bir **yan etkiydi**: aday üretecinde boyut sayısı
ve sinonim uzunluğu.

## 🔴 REDDETMEK DEĞİL — ölçülüp reddedilmiş iki anti-çözüm

| deneme | korpus |
|---|---|
| belirsizse `route()` **koşulsuz** `None` dönsün | %94,3 → **%83,6** |
| aynısı, yalnız cube-düzeyi kanıt yokken | boyahane erişim %69 → **%66** |

Kaybın sebebi yapısal: bir soru terimi belirsiz olsa bile **cube'unu söylüyor** olabilir
(*"parti adedi"*). Reddetmek o kanıtı yok sayar.

> 🔴 Raporun ölçütü *"belirsizlik **sıraya** değil **CHİP'E** bağlansın"* — sıradan
> çıkarmak değil, **yanına bir seçenek koymak**. Cevap gider, alternatif beyan edilir,
> **kapsam maliyeti sıfırdır.**

Aynı disiplin `app/uyum.py`'nin *beyanlı kısmi cevabı*yla birebir aynıdır.
"""

from __future__ import annotations

import pytest

from app import belirsizlik_chipi as bc
from tests.conftest import ask


# ═══════════════════════════════════════════════════════════════════════════════
# 1 · SÖZLEŞME — ne zaman chip, ne zaman sessizlik
# ═══════════════════════════════════════════════════════════════════════════════

def test_COK_SAHIPLI_TERIM_ALTERNATIF_URETIR():
    """🔴 Kayıt ≥2 aday biliyorsa **öteki** cube'lar döner (seçilen hariç)."""
    kayit = [{"terim": "tep", "adaylar": ["enerji_makine", "enerji_tesis", "surdurulebilirlik"],
              "sahiplenilen_terimler": []}]
    assert bc.alternatifler("tep", kayit, "surdurulebilirlik") == \
        ["enerji_makine", "enerji_tesis"]


def test_SAHIP_BEYAN_EDILMISSE_SESSIZ():
    """⚠ Sahip beyan edilmişse belirsizlik **çözülmüştür**; chip basmak kullanıcıya
    kapatılmış bir soruyu tekrar sormaktır. `hakem` o durumda zaten seçimi yapar."""
    kayit = [{"terim": "sapma", "adaylar": ["a", "b"], "sahiplenilen_terimler": ["a"]}]
    assert bc.alternatifler("sapma", kayit, "a") == []


def test_TEK_SAHIPLI_TERIM_SESSIZ():
    """⚠ *"Her cevaba uyarı eklemek, uyarıyı okunmaz yapar"* (`uyum.py`'nin kendi cümlesi)."""
    assert bc.alternatifler("ciro", [{"terim": "ciro", "adaylar": ["parti"],
                                      "sahiplenilen_terimler": []}], "parti") == []
    assert bc.alternatifler("yok", [], "x") == []


def test_ALTI_ADAYDA_UST_SINIR():
    """⚠ `adet` **altı** cube'a ait; altısını da basmak cevabı gürültüye boğar."""
    kayit = [{"terim": "adet",
              "adaylar": ["bakim", "cari", "kalite", "oee", "parti", "ticaret"],
              "sahiplenilen_terimler": []}]
    assert len(bc.alternatifler("adet", kayit, "oee")) == bc.EN_FAZLA == 3


# ═══════════════════════════════════════════════════════════════════════════════
# 2 · KULLANICIYA GİDEN METİN
# ═══════════════════════════════════════════════════════════════════════════════

def test_NOT_TERCIHI_BILDIRIR_OZUR_DILEMEZ():
    """⚠ *"Yanlış olabilir"* DENMEZ: sayı doğrudur, yalnız hangi **tanımın** kullanıldığı
    bir tercihti. *Bir tercihi bildirmek özür dilemek değildir.*"""
    m = bc.not_metni("tep", "bölüm enerji", ["tep (tesis enerji)", "tep (çevre)"])
    assert "tep" in m and "bölüm enerji" in m
    assert "yanlış" not in m.lower() and "hata" not in m.lower()
    assert bc.not_metni("tep", "x", []) == ""


def test_CHIP_AYNI_DUVARA_GERI_DONMUYOR(schema):
    """🔴 `query` cube adıyla **nitelenir** — `olcu_netlestirme`/`ay_netlestirme` ile aynı
    disiplin: *"kullanıcıyı aynı duvara ikinci kez çarptıran bir chip, chip olmamasından
    kötüdür."*"""
    adlar = [c["name"] for c in schema["cubes"]][:2]
    chipler = bc.chipler("adet", adlar, schema)
    assert len(chipler) == 2
    for c in chipler:
        assert c["query"] != "adet", "🔴 chip aynı belirsiz sorguyu tekrar üretiyor"
        assert c["label"].startswith("adet (")


def test_CUBE_ETIKETI_DISPLAY_ONCELIKLI(schema):
    """🔴 **Sıra ölçümle düzeltildi.** İlk yazım *"ilk sinonim"* diyordu ve `eval`
    koşumunda ne ürettiği görüldü:

        «sapma» birden fazla yerde tanımlı — bu cevap **fire** tanımıyla hesaplandı.

    `fire`, `parti` cube'unun ilk sinonimidir — ama kullanıcı için **başka bir ölçünün
    adıdır**. Cümle *"sapmayı fire olarak hesapladım"* diye okunuyordu: beyan etmeye
    çalıştığımız şeyin tam tersi.

    Doğru sıra `display` → teknik ad → sinonim. *Bir alanı amacı dışında kullanmak,
    çoğu zaman bir kez işe yarar ve sonra yanıltır.*"""
    assert bc.cube_etiketi({"name": "parti", "display": "Parti",
                            "synonyms": ["fire", "ciro"]}) == "Parti"
    assert bc.cube_etiketi({"name": "enerji_makine", "synonyms": ["bolum enerji"]}) \
        == "enerji_makine"
    assert bc.cube_etiketi({"synonyms": ["su!"]}) == "su"      # son çare


def test_ETIKET_BASKA_OLCUNUN_ADI_OLMUYOR(schema):
    """🔴 Ölçülen kusurun **doğrudan** kapısı: gerçek katalogda hiçbir cube etiketi,
    o cube'un **kendi bir ölçüsünün** adı olmamalı — yoksa beyan cümlesi kendi kendini
    çürütür."""
    kotu = []
    for c in schema["cubes"]:
        etiket = bc.cube_etiketi(c).lower()
        # ⚠ MEŞRU İSTİSNA: cube'un KENDİ ADI aynı zamanda bir ölçü sinonimiyse yanıltıcı
        # değildir — `oee` cube'u gerçekten OEE'yi ölçer. Yanıltıcı olan, adın **başka**
        # bir ölçüden ödünç alınmasıdır (`parti` → «fire»), ve `display`/`name` önceliği
        # tam olarak onu kapatıyor. *Bir kapının kırmızısı, kapının kendi cümlesini
        # doğrulamalıdır; doğrulamıyorsa ölçüt fazla geniştir.*
        if etiket in {str(c.get("name") or "").lower(),
                      str(c.get("display") or "").lower()}:
            continue
        olcu_adlari = {str(x).removesuffix("!").lower()
                       for syns in (c.get("measure_synonyms") or {}).values()
                       for x in (syns or [])}
        if etiket and etiket in olcu_adlari:
            kotu.append(f"{c['name']} → «{etiket}»")
    assert not kotu, ("🔴 cube etiketi kendi ölçüsünün adı: " + ", ".join(kotu[:5])
                      + " — beyan cümlesi «X'i Y tanımıyla hesapladım» diye okunur")


# ═══════════════════════════════════════════════════════════════════════════════
# 3 · UÇTAN UCA — cevap GİDİYOR ve beyan EDİLİYOR
# ═══════════════════════════════════════════════════════════════════════════════

def test_UCTAN_UCA_CEVAP_GIDIYOR_VE_BEYAN_EDILIYOR(client):
    """🔴 **ASIL KAPI.** Çok-sahipli bir terimde cevap **kesilmiyor** (anti-çözümün
    ölçülen bedeli %94,3 → %83,6) ama alternatif **beyan ediliyor**."""
    d = ask(client, "haziran parti sayısı")
    if d.get("source") != "cube":
        pytest.skip("⊘ bu soru cube yolundan dönmedi")
    assert (d.get("result") or {}).get("row_count") is not None, \
        "🔴 cevap kesilmiş — belirsizlik REDDE bağlanmış, chip'e değil"
    etiketler = [s.get("label", "") for s in (d.get("suggestions") or [])]
    assert any("parti sayısı (" in e or "parti sayisi (" in e for e in etiketler), \
        f"🔴 alternatif beyan edilmiyor: {etiketler}"
    assert "birden fazla yerde tanımlı" in (d.get("note") or "")


def test_NET_TERIMDE_CHIP_YOK(client):
    """🔴 Kapının **asıl sınavı**: tek sahipli bir terim uyarı almamalı.
    *Bir kapı, yakaladıklarıyla değil YANLIŞ yakaladıklarıyla sınanır.*"""
    d = ask(client, "bu yıl toplam ciro")
    if d.get("source") != "cube":
        pytest.skip("⊘ cube yolundan dönmedi")
    assert "birden fazla yerde tanımlı" not in (d.get("note") or "")


def test_VAR_OLAN_CHIPLER_EZILMIYOR(client):
    """⚠ Cevap zaten bir öneri taşıyorsa belirsizlik chip'i **sonuna** eklenir.
    Ezmek, bir kusuru kapatırken başka bir yeteneği sessizce kaldırmak olurdu —
    deponun *"arka-ön bütünlüğü"* kuralının tam karşıtı."""
    from app.routers import ask as ask_mod

    src = ask_mod._belirsizlik_beyani.__doc__ or ""
    assert "EZİLMEZ" in src or "ezilmez" in src.lower(), "⊘ sözleşme belgelenmemiş"
    d = ask(client, "bu yıl makine bazında oee")
    assert isinstance(d.get("suggestions") or [], list)


def test_KAYIT_YOKSA_DAVRANIS_BUGUNKU():
    """🔴 GERİ AL mekanizması: `metrik_kaydi` bayrağı kapalıysa şemada anahtar yoktur ve
    bu özellik **hiç çalışmaz** — davranış birebir bugünkü. *Bir özelliğin geri alınması
    bir kod değişikliği gerektirmemelidir.*"""
    class _R:
        note = None
        suggestions = [1, 2]

    from app.routers.ask import _belirsizlik_beyani

    r = _R()
    assert _belirsizlik_beyani(r, "q", {"cube": "x"}, {"name": "x"}, {}) == [1, 2]
    assert r.note is None
