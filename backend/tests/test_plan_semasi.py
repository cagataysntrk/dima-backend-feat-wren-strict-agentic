"""FAZ O-2 — PLAN ŞEMASININ KAPISI.

Bu kapı bir **sözleşmeyi** sabitler, bir davranışı değil: bugün hiçbir yol plan şemasını
okumuyor (`KURAL B`). Ama şema **şimdi** yazıldığı için **şimdi** sınanabilir — ve
sınanmazsa, onu okuyacak faz geldiğinde kusurları o fazın hatası sanılır.

*Bir sözleşmeyi bağlamadan önce sınamak, iki kusuru birbirine karıştırmamanın tek yoludur.*
"""

from __future__ import annotations

from app.plan_semasi import FIILLER, plan_json_schema, tek_adimli

IDX = {"parti": {"measures": ["toplam_fire_kg", "fire_orani_yuzde"],
                 "dimensions": ["makine", "kisim"], "time_dimensions": ["tarih"]}}


def _dallar() -> dict[str, dict]:
    s = plan_json_schema(IDX)
    return {d["title"]: d for d in s["properties"]["adimlar"]["items"]["oneOf"]}


def test_FIIL_KUMESI_KAPALI():
    """🔴 **Taşıyıcı kolon:** plan yeni bir fiil **icat edemez**.

    Serbest bırakılsaydı plan üreten LLM, SQL üreten LLM'den **daha az** denetlenebilir
    olurdu — hatası birkaç adım sonra, **birleşik sonuçta** ortaya çıkar ve hangi adımdan
    geldiği görünmez.
    """
    dallar = _dallar()
    assert set(dallar) == set(FIILLER), (
        f"şema dalları fiil kümesiyle örtüşmüyor: {set(dallar) ^ set(FIILLER)}")
    for ad, dal in dallar.items():
        assert dal["properties"]["fiil"] == {"const": ad}, f"{ad}: fiil sabit değil"
        assert dal["additionalProperties"] is False, (
            f"{ad}: `additionalProperties` açık — plan şemanın bilmediği bir alan "
            "taşıyabilir ve o alan hiçbir kapıdan geçmez")


def test_HER_FIIL_PARAMETRE_ZORUNLU_KILAR():
    """🔴 `B1`'in kapısı: **parametresiz bir plan, bir zincir değil bir sıralamadır.**

    Bir fiil parametre istemiyorsa adımlar birbirine değer geçiremez ve her adım kendi
    varsayımıyla koşar — plan bir **sıraya** dönüşür.
    """
    for ad, dal in _dallar().items():
        gerekli = set(dal["required"]) - {"fiil"}
        assert gerekli, f"{ad}: hiçbir parametre zorunlu değil — bu bir sıralama adımı"


def test_ADIM_REFERANSI_SERBEST_IFADE_DEGIL():
    """⚠ Referans dili **bilerek dar**: `$1` biçimi, başka hiçbir şey.

    Genişletilseydi plan aritmetik/koşul/döngü yazabilirdi ve denetim şemadan
    **yorumlayıcıya** kayardı. *Bir referans dilini genişletmek, onu bir programlama
    diline çevirir.*
    """
    import re

    from app.plan_semasi import ADIM_REFERANSI
    rx = re.compile(ADIM_REFERANSI)
    assert rx.match("$1") and rx.match("$12")
    for kotu in ("$0", "$1+1", "$a", "1", "$", "$1.cube", "${1}"):
        assert not rx.match(kotu), f"referans dili çok geniş: {kotu!r} kabul edildi"


def test_PLAN_UZUNLUGU_TAVANLI():
    """🔴 `E9`'un karşı önlemi — **bu belgenin kendi yüklemi de yanılabilir.**

    *«Bu soru çok adımlıdır»* yanlışsa cevap **yanlış olmaz, pahalı olur** ve `E6`'nın
    kapısına takılır. Şema burada sert bir tavan koyar.
    """
    s = plan_json_schema(IDX)
    assert s["properties"]["adimlar"]["maxItems"] == 5
    assert s["properties"]["adimlar"]["minItems"] == 1


def test_TEK_ADIMLI_PLAN_BUGUNKU_CUBEQUERY():
    """🔴🔴 `E6` düzeltmesinin **kod karşılığı** — geçişin denklik köprüsü.

    `plan_kur` `select_cube`'un yerine geçtiğinde basit sorular için çıktı **bire bir
    aynı** olmalı. Böylece geçiş bir davranış değişikliği değil, bir **temsil
    genişlemesidir**: bugünkü yol, planın **özel hâlidir**.
    """
    cq = {"cube": "parti", "measures": ["toplam_fire_kg"]}
    assert tek_adimli({"adimlar": [{"fiil": "SORGU", "cube_query": cq}]}) == cq
    # Çok adımlı → None: çağıran gerçek çalıştırıcıya gider.
    assert tek_adimli({"adimlar": [{"fiil": "SORGU", "cube_query": cq},
                                   {"fiil": "BAGLA", "kaynak": "$1"}]}) is None
    # Tek adım ama SORGU değilse de None — bir `ANLAT` adımı bir CubeQuery değildir.
    assert tek_adimli({"adimlar": [{"fiil": "ANLAT", "kaynak": "$1"}]}) is None
    assert tek_adimli(None) is None


def test_SORGU_GOVDESI_KOPYALANMADI():
    """⚠ `KAT-1`: `cube_query` şeması **çağrılır**, yeniden yazılmaz.

    İkinci bir kopya, katalog değişince **birinin bayatlaması** demekti.
    """
    from app.intent_semasi import cube_query_json_schema
    assert _dallar()["SORGU"]["properties"]["cube_query"] == cube_query_json_schema(IDX)
