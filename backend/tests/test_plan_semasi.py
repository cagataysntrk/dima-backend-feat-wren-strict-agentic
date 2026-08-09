"""FAZ O-2 — PLAN ŞEMASININ KAPISI.

Bu kapı bir **sözleşmeyi** sabitler, bir davranışı değil: bugün hiçbir yol plan şemasını
okumuyor (`KURAL B`). Ama şema **şimdi** yazıldığı için **şimdi** sınanabilir — ve
sınanmazsa, onu okuyacak faz geldiğinde kusurları o fazın hatası sanılır.

*Bir sözleşmeyi bağlamadan önce sınamak, iki kusuru birbirine karıştırmamanın tek yoludur.*
"""

from __future__ import annotations

from app.plan_semasi import ADIM_REFERANSI, FIILLER, plan_json_schema, tek_adimli

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
    # ⟳ Sayı **elle yazılmıyor** artık: `AZAMI_ADIM` tek sahip. İlk hâl `== 5` diyordu
    # ve tavan dört yeteneğin en kısa zincirine göre 8'e çıkınca **bayatladı** — kapı
    # bir sayıyı değil bir **kararı** korumalı. *Bir sabiti iki yerde yazmak, birini
    # eskitmeye söz vermektir.*
    from app.plan_semasi import AZAMI_ADIM
    s = plan_json_schema(IDX)
    assert s["properties"]["adimlar"]["maxItems"] == AZAMI_ADIM
    assert s["properties"]["adimlar"]["minItems"] == 1
    # ⚠ Ve tavanın **var olduğu** iddiası korunuyor: sınırsız bir plan uzunluğu,
    # `E9`'un tam olarak yasakladığı şey.
    assert 1 < AZAMI_ADIM <= 12, "tavan ya yok ya anlamsız derecede geniş"


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

    # ⟳ `FAZ 7` — `SORGU.cube_query` artık **inline nesne YA DA `$n` referansı**
    # (`oneOf`), çünkü `KIR`/`SUZ` bir sorgu üretir ve `SORGU` onu koşar. İddia
    # değişmedi, yalnız **yeri** değişti: cq şeması `oneOf`un bir üyesi olarak
    # **aynen** durmalı. Kopyalansaydı bir alanı bile farklı olurdu.
    _alan = _dallar()["SORGU"]["properties"]["cube_query"]
    assert cube_query_json_schema(IDX) in _alan["oneOf"], (
        "`cube_query` şeması ÇAĞRILMIYOR — bir kopya yazılmış olmalı (KAT-1)")
    # ⚠ Ve öteki üye **yalnız** bir adım referansı olmalı: `SORGU`ya serbest bir dize
    # kabul ettirmek, beyaz listeyi delerdi.
    _oteki = [d for d in _alan["oneOf"] if d != cube_query_json_schema(IDX)]
    assert len(_oteki) == 1 and _oteki[0].get("pattern") == ADIM_REFERANSI


def test_TAVAN_YETENEGI_KESMIYOR():
    """🔴 Bir tavan, taşıması gereken işi kesiyorsa maliyeti değil **yeteneği** kısar.

    Eski tavan **5**'ti ve kök-neden inişinin en kısa zinciri **6** adım:
    `SORGU→BAGLA→SUZ→SORGU→AYRISTIR→ANLAT`. Yani fiiller bağlanmış ama plan hiç
    kurulamamış olurdu — **yapısal** bir imkânsızlık, sessiz bir tanesi.

    ⚠ Tavan yine de bir maliyet kapısıdır (`E9`): pay dar tutuldu (6 + 2).
    """
    from app.plan_semasi import AZAMI_ADIM
    EN_KISA = {"kok_neden": 6, "karar_matrisi": 5, "rapor": 5, "pano": 4}
    assert AZAMI_ADIM >= max(EN_KISA.values()), (
        f"tavan {AZAMI_ADIM} — en uzun 'en kısa zincir' {max(EN_KISA.values())}; "
        "bir yetenek yapısal olarak ifade EDİLEMEZ")
    assert AZAMI_ADIM <= max(EN_KISA.values()) + 2, (
        "tavan gereğinden geniş — plan uzunluğu bir maliyettir (E9)")


def test_ISTEM_FIIL_KUMESINDEN_URETILIYOR():
    """🔴 `KAT-1` — istem elle yazılsaydı, küme 7'den 14'e çıkınca model yeni fiilleri
    **hiç öğrenmezdi** ve kusur ancak canlıda görünürdü."""
    from app.plan_semasi import FIILLER, plan_sistem_metni
    metin = plan_sistem_metni("KATALOG")
    eksik = [f for f in FIILLER if f not in metin]
    assert not eksik, f"istem şu fiilleri hiç anlatmıyor: {eksik}"
    # ⚠ Ve kök-neden halkası istemde **açıkça** yazılı olmalı: model `$n`'i bir
    # `cube_query` alanına koyabileceğini bilmezse iniş hiç kurulmaz.
    assert '"cube_query":"$2"' in metin.replace(" ", ""), "iniş halkası anlatılmamış"
    assert '"kaynaklar"' in metin.replace(" ", ""), "liste referansı anlatılmamış"
